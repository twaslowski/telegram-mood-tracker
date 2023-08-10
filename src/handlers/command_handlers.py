import datetime
import logging

from telegram import Update

from src.config import metrics
from src.handlers.metrics_handlers import handle_enum_metric, handle_numeric_metric
from src.persistence import save_record, get_latest_record, update_latest_record


def init_record():
    record = {key: None for key in metrics.keys()}
    record['timestamp'] = datetime.datetime.now().isoformat()
    record['completed'] = False
    return record


async def main_handler(update: Update, _) -> None:
    """Main handler for the bot. This is what starts the query process; determines whether a new record needs to be
    created, creates records and sends out the prompts to populate them."""
    latest_record = get_latest_record()
    if not latest_record or latest_record.get('completed', True):
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id, text="Creating record.")
        save_record(init_record())
        await main_handler(update, None)
    else:
        # check first field that is not set
        for metric, config in metrics.items():
            if config['type'] == 'enum' and latest_record[metric] is None:
                logging.info(f"collecting information on metric {metric}, configured with {config}")
                return await handle_enum_metric(update, config['prompt'], config['values'])
            elif config['type'] == 'numeric' and latest_record[metric] is None:
                logging.info(f"collecting information on metric {metric}, configured with {config}")
                return await handle_numeric_metric(update, config['prompt'], config['range'])


async def button(update: Update, _) -> None:
    """Callback handler for the buttons that are sent out to populate the metrics."""
    # retrieve query data
    query = update.callback_query
    await query.answer()
    metric = query.message.text.split(":")[0].lower().replace(" ", "_")

    record = get_latest_record()

    # update record
    if metric == 'timestamp':
        record['timestamp'] = modify_timestamp(record['timestamp'], int(query.data)).isoformat()
        logging.info(f"Timestamp updated to {record['timestamp']}")
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id, text="Timestamp updated.")
    else:
        record[metric] = query.data

    update_latest_record(record)

    # check if record is complete
    if all(value is not None for value in record.values()):
        record['completed'] = True
        update_latest_record(record)
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id,
                                                           text="Record completed. Thank you!")
    else:
        await main_handler(update, None)


async def timestamp_handler(update: Update, _) -> None:
    """Enables the user to modify the timestamp of the latest record. Command handler for /timestamp."""
    record = get_latest_record()
    if record.get('completed', True):
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id,
                                                           text="No record to modify.")
    else:
        return await handle_numeric_metric(update, "Timestamp: For how many hours ago is this record?", (0, 12))


def modify_timestamp(timestamp: str, offset: int) -> datetime.datetime:
    timestamp = datetime.datetime.fromisoformat(timestamp)
    return timestamp - datetime.timedelta(hours=offset)
