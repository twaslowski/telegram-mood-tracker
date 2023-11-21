import datetime
import logging

from expiringdict import ExpiringDict
from telegram import Update

import src.persistence as persistence
from src.config import config
from src.handlers.metrics_handlers import handle_enum_metric, handle_numeric_metric
from src.visualise import visualize_monthly_data

# state map to keep track of the current question
user_record_registration_state = ExpiringDict(max_len=100, max_age_seconds=300)

# in-memory storage for user records before they get persisted; if a user doesn't finish a record, it will be deleted
temp_records = ExpiringDict(max_len=100, max_age_seconds=300)


async def init_user(update: Update, _) -> None:
    """
    Creates user based on the user_id included in the update object.
    :param update: Update from the Telegram bot.
    :param _: CallbackContext: is irrelevant
    :return:
    """
    user_id = update.effective_user.id
    if not persistence.find_user(user_id):
        logging.info(f"Creating user {user_id}")
        persistence.create_user(user_id)
    else:
        logging.info(f"Received /start, but user {user_id} already exists")


def init_record(user_id: int):
    """
    Creates a new record for the user with the given user_id.
    Additionally, updates the state map to move through the questions easier.
    :param user_id:
    """
    # create temporary record from user configuration
    metrics = persistence.get_user_config(user_id)
    record = {metric['name']: None for metric in metrics}
    record['timestamp'] = datetime.datetime.now().isoformat()
    logging.info(f"Creating temporary record for user {user_id}: {record}")
    temp_records[user_id] = record

    # update state map
    user_record_registration_state[user_id] = metrics
    return


async def main_handler(update: Update, _) -> None:
    """
    Main handler for the bot. This is what starts the query process; determines whether a new record needs to be
    created, creates records and sends out the prompts to populate them.
    """
    user_id = update.effective_user.id
    if not temp_records.get(user_id):
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id,
                                                           text="Creating a new record for you ...")
        init_record(user_id)
        await main_handler(update, None)
    else:
        # check first field that is not set
        for metric in temp_records[user_id]:
            if config['type'] == 'enum':
                logging.info(f"collecting information on metric {metric}, configured with {config}")
                return await handle_enum_metric(update, metric['prompt'], metric['values'])
            elif config['type'] == 'numeric':
                logging.info(f"collecting information on metric {metric}, configured with {config}")
                return await handle_numeric_metric(update, metric['prompt'], metric['range'])


async def button(update: Update, _) -> None:
    """
    Processes the inputs from the InlineKeyboardButtons and maintains the temporary record.
    """
    query = update.callback_query
    await query.answer()
    metric = query.message.text.split(":")[0].lower().replace(" ", "_")

    record = temp_records[update.effective_user.id]
    record[metric] = query.data

    persistence.update_latest_record(record)

    # check if record is complete
    if all(value is not None for value in record.values()):
        record['completed'] = True
        persistence.update_latest_record(record)
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id,
                                                           text="Record completed. Thank you!")
    else:
        await main_handler(update, None)


async def graph_handler(update: Update, context) -> None:
    now = datetime.datetime.now()
    year = now.year
    months = [8, 9, 10, 11]
    for month in months:
        path = visualize_monthly_data(year, month)
        await update.effective_user.get_bot().send_photo(update.effective_user.id, open(path, 'rb'))


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(hours=offset)
