import datetime
import logging

from expiringdict import ExpiringDict
from telegram import Update

import src.repository.record_repository as record_repository
from src.autowiring.inject import autowire
from src.handlers.graphing import handle_graph_specification
from src.handlers.metrics_handlers import prompt_user_for_metric
from src.handlers.util import send, handle_no_known_state
from src.model.metric import Metric
from src.model.record import TempRecord
from src.repository.user_repository import UserRepository
from src.state import State, APPLICATION_STATE

"""
The temp_records data structures holds unfinished records for up to five minutes while users are creating them.
This is a key-value data structure, with the keys being the user id and the value being exactly one temporary record.
"""
temp_records = ExpiringDict(max_len=100, max_age_seconds=300)


def get_temp_record(user_id: int) -> TempRecord | None:
    """
    Utility method to make typing easier when accessing the temp_records structure
    :param user_id: user_id for which to retrieve temporary record
    :return: TempRecord if available, else None
    """
    return temp_records.get(user_id)


@autowire("user_repository")
def create_temporary_record(user_id: int, user_repository: UserRepository):
    """
    Creates a new record for the user with the given user_id.
    Additionally, updates the state map to move through the questions easier.
    :param user_repository: autowired.
    :param user_id:
    """
    # create temporary record from user configuration
    # todo handle find_user() == None?
    metrics = user_repository.find_user(user_id).metrics
    record = TempRecord(metrics=metrics)

    logging.info(f"Creating temporary record for user {user_id}: {record}")
    # Store temporary record in the record ExpiringDict
    temp_records[user_id] = record
    APPLICATION_STATE[user_id] = State.RECORDING


def find_first_metric(temp_record: TempRecord) -> Metric:
    """
    Finds the first metric in the record that has not been answered yet.
    :param temp_record: The temporary record.
    :return: The first metric that has not been answered yet.
    """
    # todo is there a scenario first_unanswered_data is None, i.e. all metrics have been answered already?
    first_unanswered_data = list(filter(lambda x: x.value is None, temp_record.data))[
        0
    ]  # RecordData instance
    return list(
        filter(
            lambda x: x.name == first_unanswered_data.metric_name, temp_record.metrics
        )
    )[0]


async def record_handler(update: Update, _) -> None:
    """
    Handles /record.
    Handles the recording process for the user. If /record is processed, it will start the recording process.
    Otherwise, it will send out metric user prompts. The responses to those prompts are then handled by dedicated
    button handlers, which ultimately redirect back to this function after handling their own logic.
    """
    user_id = update.effective_user.id
    # if no record exists in the temporary records
    if not temp_records.get(user_id):
        await send(update, text="Creating a new record for you ...")
        create_temporary_record(user_id)
        # Recurse to start the record entry process
        await record_handler(update, None)
    else:
        # find the first metric for which the record value is still None
        temp_record = get_temp_record(user_id)
        metric = find_first_metric(temp_record)

        logging.info(f"collecting information on metric {metric}")
        # this needs to be refactored, since I want to get rid of this distinction entirely eventually
        await prompt_user_for_metric(update, metric)


async def button(update: Update, _) -> None:
    """
    General button handler.
    Disambiguates between different states and forwards the query to the appropriate handler.
    :param update: Button press.
    """
    user = update.effective_user.id
    user_state = APPLICATION_STATE.get(user)
    if user_state is State.GRAPHING:
        await handle_graph_specification(update)
    if user_state is State.RECORDING:
        await handle_record_entry(update)
    else:
        await handle_no_known_state(update)


async def handle_record_entry(update: Update) -> None:
    """
    When a button update is received while the user is recording a record, this function is called.
    It represents the entering of a piece of record data, e.g. mood or sleep.
    Broadly, this function has to figure out which metric was being answered based on the prompt in the query;
    then, it has to update the temporary record with the answer.
    Lastly, it has to check if the record is complete and store it in the database if it is.

    This mechanism of figuring out which metric has been answered is a bit convoluted, but ultimately the only way
    to do it if you want to be able to handle duplicate inputs for any given metrics.
    :param update: Telegram update object
    :return:
    """
    # retrieve query prompt and answer
    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()

    # retrieve current record
    user_record = get_temp_record(user_id)
    if not user_record:
        logging.error(f"User {user_id} does not have a temporary record")
        return await handle_no_known_state(update)

    # find metric that was answered and update the record
    metric, value = parse_query_data(query.data)
    logging.info(f"User {user_id} answered {metric} with {query.data}")
    user_record.update_data(metric, value)
    temp_records[user_id] = user_record

    # check if record is complete
    if user_record.is_complete():
        store_record(user_id, user_record)
        await send(update, text="Record completed. Thank you!")
    # send out next metric prompt
    else:
        logging.info(
            f"Record for user {user_id} is not complete yet: {user_record.data}"
        )
        await record_handler(update, None)


def parse_query_data(query_data: str) -> tuple[str, int]:
    """
    Parses the query data into a metric name and value.
    :param query_data: The query data.
    :return: A tuple containing the metric name and value.
    """
    assert (
            ":" in query_data
    ), "Query data must be a key/value pair of metric name and value."
    metric = query_data.split(":")[0]
    value = int(query_data.split(":")[1])
    return metric, value


def store_record(user_id: int, user_record: TempRecord):
    """
    Stores a temporary record in the database.
    :param user_id: user to whom the record belongs
    :param user_record: the temporary record being saved
    :return:
    """
    logging.info(f"Record for user {user_id} is complete: {user_record}")
    record_repository.create_record(
        user_id,
        {
            # todo refactor this
            record_data.metric_name: record_data.value
            for record_data in user_record.data
        },
        user_record.timestamp.isoformat(),
    )
    del temp_records[user_id]


async def offset_handler(update: Update, context) -> None:
    """
    Handles the /offset command.
    :param update: Telegram update object
    :param context: holds the arguments passed to the command
    :return:
    """
    incorrect_state_message = (
        "You can only use /offset while recording a record. "
        "Press /record to create a new record."
    )
    success_message = "The timestamp of your record has been updated to {}."
    invalid_args_message = "Please provide an offset in days like this: /offset 1"
    user_state = APPLICATION_STATE.get(update.effective_user.id)
    if (
            user_state is not None
            and APPLICATION_STATE[update.effective_user.id] == State.RECORDING
    ):
        if len(context.args) != 1:
            await send(update, text=invalid_args_message)
        offset = int(context.args[0])
        user_id = update.effective_user.id

        # overwrite temp record; it's assumed the record exists since the user state is RECORDING
        # state inconsistencies are not accounted for here
        record = temp_records[user_id]
        record.timestamp = modify_timestamp(record.timestamp, offset)
        temp_records[user_id] = record
        logging.info(f"Updated timestamp for user {user_id} to {record.timestamp}")
        # so i got kind of lazy on this one. splitting an iso-formatted timestamp just returns the date section.
        await send(
            update,
            text=success_message.format(record.timestamp.isoformat().split("T")[0]),
        )
    else:
        await send(update, text=incorrect_state_message)


def modify_timestamp(timestamp: datetime.datetime, offset: int) -> datetime.datetime:
    return timestamp - datetime.timedelta(days=offset)
