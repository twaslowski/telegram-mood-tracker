import datetime
import logging

from expiringdict import ExpiringDict
from telegram import Update

import src.repository.record_repository as record_repository
from src.config import defaults
from src.handlers.metrics_handlers import (
    handle_enum_metric,
    handle_numeric_metric,
    handle_graphing_dialog,
)
from src.repository import user_repository
from src.state import State
from src.visualise import visualize_monthly_data

# in-memory storage for user records before they get persisted; if a user doesn't finish a record, it will be deleted
temp_records = ExpiringDict(max_len=100, max_age_seconds=300)
state = ExpiringDict(max_len=100, max_age_seconds=300)

bullet_point_list = "\n".join(
    [f"- {metric['name'].capitalize()}" for metric in defaults["metrics"]]
)
introduction_text = (
    "Hi! You can track your mood with me. Simply type /record to get started. By default, "
    f"I will track the following metrics: \n "
    f"{bullet_point_list}"
)


async def init_user(update: Update, _) -> None:
    """
    Creates user based on the user_id included in the update object.
    :param update: Update from the Telegram bot.
    :param _: CallbackContext: is irrelevant
    :return:
    """
    user_id = update.effective_user.id
    if not user_repository.find_user(user_id):
        logging.info(f"Creating user {user_id}")
        user_repository.create_user(user_id)
        await update.effective_user.get_bot().send_message(
            chat_id=update.effective_user.id, text=introduction_text
        )
    else:
        logging.info(f"Received /start, but user {user_id} already exists")


def init_record(user_id: int):
    """
    Creates a new record for the user with the given user_id.
    Additionally, updates the state map to move through the questions easier.
    :param user_id:
    """
    # create temporary record from user configuration
    # todo handle find_user() == None?
    metrics = user_repository.find_user(user_id).metrics
    record = {
        "record": {metric["name"]: None for metric in metrics},
        "timestamp": datetime.datetime.now().isoformat(),
        "config": metrics,
    }

    logging.info(f"Creating temporary record for user {user_id}: {record}")
    temp_records[user_id] = record


async def main_handler(update: Update, _) -> None:
    """
    Main handler for the bot. This is what starts the query process; determines whether a new record needs to be
    created, creates records and sends out the prompts to populate them.
    """
    user_id = update.effective_user.id
    if not temp_records.get(user_id):
        await update.effective_user.get_bot().send_message(
            chat_id=update.effective_user.id, text="Creating a new record for you ..."
        )
        init_record(user_id)
        state[user_id] = State.RECORDING
        await main_handler(update, None)
    else:
        # find the first metric for which the record value is still None
        metric = [
            metric
            for metric in temp_records[user_id]["config"]
            if temp_records[user_id]["record"][metric["name"]] is None
        ][0]
        logging.info(f"collecting information on metric {metric}")
        if metric["type"] == "enum":
            await handle_enum_metric(update, metric["prompt"], metric["values"])
        elif metric["type"] == "numeric":
            await handle_numeric_metric(update, metric["prompt"], metric["range"])


def get_all_months_for_offset(time_range: int, year: int, month: int):
    """
    Returns a list of tuples (year, month) for the given time range, i.e. how many records in the past should be considered.
    """
    months = [(year, month)]
    for i in range(time_range - 1):
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        months.append((year, month))
    months.reverse()
    return months


async def handle_graph_specification(update):
    # await timeframe specification
    query = update.callback_query
    await query.answer()

    now = datetime.datetime.now()
    time_range = int(update.callback_query.data)
    year = now.year
    month = now.month
    months = get_all_months_for_offset(time_range, year, month)
    for month in months:
        path = visualize_monthly_data(update.effective_user.id, month)
        if path:
            await update.effective_user.get_bot().send_photo(
                update.effective_user.id, open(path, "rb")
            )


async def button(update: Update, _) -> None:
    """
    Processes the inputs from the InlineKeyboardButtons and maintains the temporary record.
    """
    user = update.effective_user.id
    user_state = state.get(user)
    if user_state is State.GRAPHING:
        await handle_graph_specification(update)
    if user_state is State.RECORDING:
        await handle_record_entry(update)
    else:
        await handle_no_known_state(update)


async def handle_no_known_state(update: Update) -> None:
    """
    Handles the case where the user is not in a known state.
    """
    no_state_message = """It doesn't appear like you're currently recording mood or graphing.
                       Press /record to create a new record, /graph to visualise your mood progress."""
    await update.effective_user.get_bot().send_message(
        chat_id=update.effective_user.id, text=no_state_message
    )


async def handle_record_entry(update):
    query = update.callback_query
    # Fetch prompt from query to figure out which question was being answered
    # If a user answers Question A, then Question B and then Question A again, the prompt will be the same
    # I don't see a better mechanism for handling this scenario.
    prompt = query.message.text
    await query.answer()
    # get current record registration state; remove the metric that was just answered
    user_id = update.effective_user.id
    user_record = temp_records.get(user_id)
    # find metric that was answered
    metric = [metric for metric in user_record["config"] if metric["prompt"] == prompt][
        0
    ]
    user_record["record"][metric["name"]] = query.data
    logging.info(f"User {user_id} answered {metric} with {query.data}")
    # update temporary record
    temp_records[user_id] = user_record
    # check if record is complete
    if all(value is not None for value in user_record["record"].values()):
        logging.info(f"Record for user {user_id} is complete: {user_record['record']}")
        record_repository.create_record(
            user_id, user_record["record"], user_record["timestamp"]
        )
        del temp_records[user_id]
        await update.effective_user.get_bot().send_message(
            chat_id=update.effective_user.id, text="Record completed. Thank you!"
        )
    else:
        logging.info(
            f"Record for user {user_id} is not complete yet: {user_record['record']}"
        )
        await main_handler(update, None)


async def graph_handler(update: Update, context) -> None:
    await handle_graphing_dialog(update, context)
    state[update.effective_user.id] = State.GRAPHING


async def offset_handler(update: Update, context) -> None:
    incorrect_state_message = """You can only use /offset while recording a record.
    Press /record to create a new record."""
    success_message = "The timestamp of your record has been updated to {}."
    invalid_args_message = "Please provide an offset in days like this: /offset 1"
    user_state = state.get(update.effective_user.id)
    if user_state is not None and state[update.effective_user.id] == State.RECORDING:
        if len(context.args) != 1:
            await update.effective_user.get_bot().send_message(
                chat_id=update.effective_user.id, text=invalid_args_message
            )
        offset = int(context.args[0])
        user_id = update.effective_user.id
        record = temp_records[user_id]
        record["timestamp"] = modify_timestamp(record["timestamp"], offset).isoformat()
        temp_records[user_id] = record
        logging.info(f"Updated timestamp for user {user_id} to {record['timestamp']}")
        # so i got kind of lazy on this one. splitting an iso-formatted timestamp just returns the date section.
        await update.effective_user.get_bot().send_message(
            chat_id=update.effective_user.id,
            text=success_message.format(record["timestamp"].split("T")[0]),
        )
    else:
        await update.effective_user.get_bot().send_message(
            chat_id=update.effective_user.id, text=incorrect_state_message
        )


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(days=offset)
