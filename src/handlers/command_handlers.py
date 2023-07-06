import datetime
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from src.persistence import save_record

user_data = {}


async def main_handler(update: Update, _) -> None:
    global user_data
    # get current timestamp in UTC
    timestamp = datetime.datetime.now().isoformat()
    user_data = {
        'timestamp': timestamp,
        'mood': None,
        'energy': None,
        'appetite': None,
        'back_pain': None,
        'sleep': None
    }
    await handle_ask_mood_state(update, _)
    await handle_ask_energy_state(update, _)
    await handle_ask_appetite(update, _)
    await handle_ask_back_pain(update, _)
    await handle_ask_sleep(update, _)


async def handle_ask_mood_state(update: Update, _) -> None:
    """Sends a message with three inline buttons attached."""
    keyboard = [
        [InlineKeyboardButton("Severely Elevated", callback_data="SEVERELY_ELEVATED")],
        [InlineKeyboardButton("Moderately Elevated", callback_data="MODERATELY_ELEVATED")],
        [InlineKeyboardButton("Mildly Elevated", callback_data="MILDLY_ELEVATED")],
        [InlineKeyboardButton("Neutral", callback_data="NEUTRAL")],
        [InlineKeyboardButton("Mildly Depressed", callback_data="MILDLY_DEPRESSED")],
        [InlineKeyboardButton("Moderately Depressed", callback_data="MODERATELY_DEPRESSED")],
        [InlineKeyboardButton("Severely Depressed", callback_data="SEVERELY_DEPRESSED")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Mood: How do you feel right now?", reply_markup=reply_markup)


async def handle_ask_energy_state(update: Update, _) -> None:
    # ask for numeric input in the range of 1-10; if not in range, ask again
    """Sends a message with three inline buttons attached."""

    keyboard = [
        [InlineKeyboardButton("1", callback_data="1")],
        [InlineKeyboardButton("2", callback_data="2")],
        [InlineKeyboardButton("3", callback_data="3")],
        [InlineKeyboardButton("4", callback_data="4")],
        [InlineKeyboardButton("5", callback_data="5")],
        [InlineKeyboardButton("️6", callback_data="6")],
        [InlineKeyboardButton("7", callback_data="7")],
        [InlineKeyboardButton("8", callback_data="8")],
        [InlineKeyboardButton("9", callback_data="9")],
        [InlineKeyboardButton("10", callback_data="10")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Energy: How much do you have?", reply_markup=reply_markup)


async def handle_ask_back_pain(update: Update, _) -> None:
    # ask for numeric input in the range of 1-10; if not in range, ask again
    """Sends a message with three inline buttons attached."""

    keyboard = [
        [InlineKeyboardButton("1", callback_data="1")],
        [InlineKeyboardButton("2", callback_data="2")],
        [InlineKeyboardButton("3", callback_data="3")],
        [InlineKeyboardButton("4", callback_data="4")],
        [InlineKeyboardButton("5", callback_data="5")],
        [InlineKeyboardButton("️6", callback_data="6")],
        [InlineKeyboardButton("7", callback_data="7")],
        [InlineKeyboardButton("8", callback_data="8")],
        [InlineKeyboardButton("9", callback_data="9")],
        [InlineKeyboardButton("10", callback_data="10")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Back pain: How bad is it?", reply_markup=reply_markup)


async def handle_ask_sleep(update: Update, _) -> None:
    # ask for numeric input in the range of 1-10; if not in range, ask again
    """Sends a message with three inline buttons attached."""

    keyboard = [
        [InlineKeyboardButton("5", callback_data="5")],
        [InlineKeyboardButton("️6", callback_data="6")],
        [InlineKeyboardButton("7", callback_data="7")],
        [InlineKeyboardButton("8", callback_data="8")],
        [InlineKeyboardButton("9", callback_data="9")],
        [InlineKeyboardButton("10", callback_data="10")],
        [InlineKeyboardButton("11", callback_data="10")],
        [InlineKeyboardButton("12", callback_data="10")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Sleep: How much did you get?", reply_markup=reply_markup)


async def handle_ask_appetite(update: Update, _) -> None:
    # ask for numeric input in the range of 1-10; if not in range, ask again
    """Sends a message with three inline buttons attached."""

    keyboard = [
        [InlineKeyboardButton("Little to no appetite", callback_data="SEVERELY_REDUCED_APPETITE")],
        [InlineKeyboardButton("Less appetite", callback_data="REDUCED_APPETITE")],
        [InlineKeyboardButton("Normal appetite", callback_data="NORMAL_APPETITE")],
        [InlineKeyboardButton("More appetite than normal", callback_data="INCREASED_APPETITE")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Appetite", reply_markup=reply_markup)


async def button(update: Update, _) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()
    logging.info(f"Query: {query}")
    metric = query.message.text.split(":")[0].lower().replace(" ", "_")

    user_data[metric] = query.data
    logging.info(f"Selected option: {query.data}")
    if all(user_data.values()):
        await cleanup(update, _)


async def cleanup(update: Update, _) -> None:
    global user_data
    logging.info(f"Saving record: {user_data}")
    save_record(user_data)
    user_data = {}
    await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id,
                                                       text="Thank you for your input!")
