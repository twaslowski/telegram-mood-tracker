import datetime
import logging

from expiringdict import ExpiringDict
from telegram import Update

import src.persistence as persistence
from src.config import config
from src.handlers.metrics_handlers import handle_enum_metric, handle_numeric_metric
from src.state import State
from src.visualise import visualize_monthly_data

user_states = {}

temp_records = ExpiringDict(max_len=100, max_age_seconds=300)


def get_user_state(user_id: int) -> dict:
    return user_states[user_id]


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
    metrics = persistence.get_user_config(user_id)
    record = {metric['name']: None for metric in metrics}
    record['timestamp'] = datetime.datetime.now().isoformat()
    logging.info(f"Creating temporary record for user {user_id}: {record}")
    temp_records[user_id] = record
    return metrics


async def main_handler(update: Update, _) -> None:
    """
    Main handler for the bot. This is what starts the query process; determines whether a new record needs to be
    created, creates records and sends out the prompts to populate them.
    """
    user_id = update.effective_user.id
    state = get_user_state(user_id)
    if not state:
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id, text="Creating record.")
        persistence.save_record(init_record(user_id))
        await main_handler(update, None)
    elif state != State.RECORDING:
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id,
                                                           text="Aborting previous operations. Creating record.")
    else:
        # check first field that is not set
        for metric in config['metrics'].items():
            if config['type'] == 'enum' and latest_record[metric] is None:
                logging.info(f"collecting information on metric {metric}, configured with {config}")
                return await handle_enum_metric(update, metric['prompt'], metric['values'])
            elif config['type'] == 'numeric' and latest_record[metric] is None:
                logging.info(f"collecting information on metric {metric}, configured with {config}")
                return await handle_numeric_metric(update, metric['prompt'], metric['range'])


async def graph_handler(update: Update, context) -> None:
    now = datetime.datetime.now()
    year = now.year
    months = [8, 9, 10, 11]
    for month in months:
        path = visualize_monthly_data(year, month)
        await update.effective_user.get_bot().send_photo(update.effective_user.id, open(path, 'rb'))


async def button(update: Update, _) -> None:
    """Callback handler for the buttons that are sent out to populate the metrics."""
    # retrieve query data
    query = update.callback_query
    await query.answer()
    metric = query.message.text.split(":")[0].lower().replace(" ", "_")

    record = persistence.get_latest_record()

    # update record
    if metric == 'timestamp':
        record['timestamp'] = modify_timestamp(record['timestamp'], int(query.data)).isoformat()
        logging.info(f"Timestamp updated to {record['timestamp']}")
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id, text="Timestamp updated.")
    else:
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


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(hours=offset)
