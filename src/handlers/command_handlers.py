from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update


async def start(update: Update, _) -> None:
    """Sends a message with three inline buttons attached."""
    await update.message.reply_text('Please choose:', reply_markup=keyboard_main_menu())


def keyboard_main_menu():
    """ Creates the main menu keyboard """
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')]]

    return InlineKeyboardMarkup(keyboard)


def confirm(update: Update, _) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer()

    keyboard = [[InlineKeyboardButton("Yes", callback_data=f'YES{query.data}'),
                 InlineKeyboardButton("No", callback_data='main'), ], ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=f"Selected option {query.data}."
                                 f"Are you sure ? ", reply_markup=reply_markup)


def do_action_1(update: Update, _) -> None:
    keyboard = [[InlineKeyboardButton("Main menu", callback_data='main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Selected option {query.data}\n"
                                 f"Executed action 1.", reply_markup=reply_markup)


def do_action_2(update: Update, _) -> None:
    keyboard = [[InlineKeyboardButton("Main menu", callback_data='main')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query = update.callback_query
    query.answer()
    query.edit_message_text(text=f"Selected option {query.data}\n"
                                 f"Executed action 2.", reply_markup=reply_markup)


async def handle_record(update: Update, _) -> None:
    await update.message.reply_text("Session reset.")
