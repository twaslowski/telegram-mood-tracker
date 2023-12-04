import datetime
import logging

from expiringdict import ExpiringDict
from telegram import Update

import src.persistence as persistence
from src.config import defaults
from src.handlers.metrics_handlers import handle_enum_metric, handle_numeric_metric
from src.visualise import visualize_monthly_data

# in-memory storage for user records before they get persisted; if a user doesn't finish a record, it will be deleted
temp_records = ExpiringDict(max_len=100, max_age_seconds=300)

bullet_point_list = '\n'.join([f"- {metric['name'].capitalize()}" for metric in defaults['metrics']])
introduction_text = "Hi! You can track your mood with me. Simply type /record to get started. By default, " \
                    f"I will track the following metrics: \n " \
                    f"{bullet_point_list}"


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
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id,
                                                           text=introduction_text)
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
    record = {
        'record': {metric['name']: None for metric in metrics},
        'timestamp': datetime.datetime.now().isoformat(),
        'config': metrics
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
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id,
                                                           text="Creating a new record for you ...")
        init_record(user_id)
        await main_handler(update, None)
    else:
        # find the first metric for which the record value is still None
        metric = [metric for metric in temp_records[user_id]['config'] if
                  temp_records[user_id]['record'][metric['name']] is None][0]
        logging.info(f"collecting information on metric {metric}")
        if metric['type'] == 'enum':
            await handle_enum_metric(update, metric['prompt'], metric['values'])
        elif metric['type'] == 'numeric':
            await handle_numeric_metric(update, metric['prompt'], metric['range'])


async def button(update: Update, _) -> None:
    """
    Processes the inputs from the InlineKeyboardButtons and maintains the temporary record.
    """
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
    metric = [metric for metric in user_record['config'] if metric['prompt'] == prompt][0]
    user_record['record'][metric['name']] = query.data

    logging.info(f"User {user_id} answered {metric} with {query.data}")

    # update temporary record
    temp_records[user_id] = user_record

    # check if record is complete
    if all(value is not None for value in user_record['record'].values()):
        logging.info(f"Record for user {user_id} is complete: {user_record['record']}")
        persistence.create_record(user_id, user_record['record'])
        del temp_records[user_id]
        await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id,
                                                           text="Record completed. Thank you!")
    else:
        logging.info(f"Record for user {user_id} is not complete yet: {user_record['record']}")
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
