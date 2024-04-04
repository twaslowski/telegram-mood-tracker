import logging

from telegram import Update
from telegram.ext import CallbackContext


async def error_handler(update: Update, context: CallbackContext):
    """Log all errors."""
    logging.error(msg="Exception while handling an update:", exc_info=context.error)
    # Get exception text

    error_message = context.error
    await update.effective_user.send_message(
        text=f"An error occurred while processing your message: {error_message}."
    )
