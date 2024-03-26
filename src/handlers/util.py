from telegram import Update


async def send(update: Update, text: str):
    """
    Sends a message to the chat. Shorthand utility to keep the code clean.
    :param update: Update from the Telegram bot.
    :param text: The message to send.
    """
    await update.effective_user.get_bot().send_message(
        chat_id=update.effective_user.id, text=text
    )
