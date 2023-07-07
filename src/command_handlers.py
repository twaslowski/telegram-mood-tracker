import datetime
import logging

from telegram import Update

from src.config import metrics_configuration
from src.metrics_handlers import handle_enum_metric, handle_numeric_metric
from src.persistence import save_record


def init_user_data():
    return {key: None for key in metrics_configuration.keys()}


# create user data from config, but with all values set to None
user_data = init_user_data()


async def main_handler(update: Update, _) -> None:
    logging.info(f"received message: {update}")
    for metric, config in metrics_configuration.items():
        print(metric, config, user_data[metric])
        if config['type'] == 'enum' and user_data[metric] is None:
            logging.info(f"collecting information on metric {metric}, configured with {config}")
            return await handle_enum_metric(update, config['prompt'], config['values'])
        elif config['type'] == 'numeric' and user_data[metric] is None:
            logging.info(f"collecting information on metric {metric}, configured with {config}")
            return await handle_numeric_metric(update, config['prompt'], config['range'])


async def button(update: Update, _) -> None:
    """Parses the CallbackQuery and updates the message text."""
    global user_data
    query = update.callback_query
    await query.answer()
    logging.info(f"Query: {query}")
    metric = query.message.text.split(":")[0].lower().replace(" ", "_")

    user_data[metric] = query.data
    logging.info(f"Selected option for metric {metric}: {query.data}")
    logging.info(f"updated user data: {user_data}")
    if all(user_data.values()):
        user_data['timestamp'] = datetime.datetime.now().isoformat()
        await cleanup(update)
    else:
        await main_handler(update, None)


async def cleanup(update: Update) -> None:
    global user_data
    logging.info(f"Saving record: {user_data}")
    save_record(user_data)
    user_data = init_user_data()
    await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id,
                                                       text="Thank you for your input!")
