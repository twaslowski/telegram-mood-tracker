import datetime
import logging
from typing import Sequence

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from src.data.appetite import Appetite
from src.data.mood import Mood
from src.persistence import save_record

user_data = {
    "mood": None,
    "appetite": None,
    "energy": None,
    "back_pain": None,
    "sleep": None,
}


async def main_handler(update: Update, _) -> None:
    global user_data
    if user_data['mood'] is None:
        return await handle_enum_metric(update, "Mood: How do you feel right now?", Mood)
    elif user_data['appetite'] is None:
        return await handle_enum_metric(update, "Appetite: Are you eating enough?", Appetite)
    elif user_data['energy'] is None:
        await handle_numeric_metric(update, "Energy: How much energy do you have right now?", (1, 11))
    elif user_data['back_pain'] is None:
        await handle_numeric_metric(update, "Back pain: How much back pain do you have right now?", (1, 11))
    elif user_data['sleep'] is None:
        await handle_numeric_metric(update, "Sleep: How much sleep did you get last night?", (4, 12))


async def handle_enum_metric(update: Update, prompt: str, enum: Sequence) -> None:
    bot = update.effective_user.get_bot()
    keyboard = [[InlineKeyboardButton(e.name.capitalize().replace("_", " "), callback_data=e.value)] for e in enum]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=update.effective_user.id, text=prompt, reply_markup=reply_markup)


async def handle_numeric_metric(update: Update, prompt: str, bounds: (int, int)) -> None:
    bot = update.effective_user.get_bot()
    keyboard = [[InlineKeyboardButton(str(i), callback_data=i)] for i in range(bounds[0], bounds[1])]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=update.effective_user.id, text=prompt, reply_markup=reply_markup)


async def button(update: Update, _) -> None:
    """Parses the CallbackQuery and updates the message text."""
    global user_data
    query = update.callback_query
    await query.answer()
    logging.info(f"Query: {query}")
    metric = query.message.text.split(":")[0].lower().replace(" ", "_")

    user_data[metric] = query.data
    logging.info(f"Selected option: {query.data}")
    if all(user_data.values()):
        user_data['timestamp'] = datetime.datetime.now().isoformat()
        await cleanup(update)
    else:
        await main_handler(update, None)


async def cleanup(update: Update) -> None:
    global user_data
    logging.info(f"Saving record: {user_data}")
    save_record(user_data)
    user_data = {}
    await update.effective_user.get_bot().send_message(chat_id=update.effective_user.id,
                                                       text="Thank you for your input!")
