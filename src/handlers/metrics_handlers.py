from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup


async def handle_enum_metric(update: Update, prompt: str, values: dict) -> None:
    bot = update.effective_user.get_bot()
    keyboard = [[InlineKeyboardButton(key.capitalize().replace("_", " "), callback_data=value)]
                for key, value in values.items()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=update.effective_user.id, text=prompt, reply_markup=reply_markup)


async def handle_numeric_metric(update: Update, prompt: str, bounds: (int, int)) -> None:
    bot = update.effective_user.get_bot()
    keyboard = [[InlineKeyboardButton(str(i), callback_data=i)] for i in range(bounds[0], bounds[1])]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=update.effective_user.id, text=prompt, reply_markup=reply_markup)


async def handle_graphing_dialog(update: Update, context) -> None:
    bot = update.effective_user.get_bot()
    keyboard = [[InlineKeyboardButton("Last month", callback_data="1")],
                [InlineKeyboardButton("Last three months", callback_data="3")],
                [InlineKeyboardButton("All time", callback_data="-1")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(chat_id=update.effective_user.id, text="How many months would you like me to graph?",
                           reply_markup=reply_markup)
