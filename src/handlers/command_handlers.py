import datetime
import logging

from telegram import Update

import src.persistence as persistence
from src.config import config
from src.handlers.metrics_handlers import handle_enum_metric, handle_numeric_metric
from src.visualise import visualize_monthly_data


async def init_user(update: Update, _) -> None:
    user_id = update.effective_user.id
    if not persistence.find_user(user_id):
        logging.info(f"Creating user {user_id}")
        persistence.create_user(user_id)


def init_record():
    record = {key: None for key in config['metrics'].keys()}
    record['timestamp'] = datetime.datetime.now().isoformat()
    record['completed'] = False
    return record


async def main_handler(update: Update, _) -> None:
    """
    Main handler for the bot. This is what starts the query process; determines whether a new record needs to be
    created, creates records and sends out the prompts to populate them.
    """
    latest_record = persistence.get_latest_record()
    if not latest_record or latest_record.get('completed', True):
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id, text="Creating record.")
        persistence.save_record(init_record())
        await main_handler(update, None)
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
