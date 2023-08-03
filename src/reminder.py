import os

from telegram.ext import CallbackContext


async def reminder(context: CallbackContext):
    """Send the reminder message."""
    message = "Hi! It's time to record your mood :)"
    await context.bot.send_message(chat_id=os.getenv('CHAT_ID'), text=message)
