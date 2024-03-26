from telegram.ext import CallbackContext


async def reminder(context: CallbackContext, text: str = None):
    """Send the reminder message."""
    if not text:
        text = "Hi! It's time to record your mood :)"
    await context.bot.send_message(context.chat_data.chat_id, text=text)
