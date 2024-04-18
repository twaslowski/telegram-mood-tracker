import logging

from telegram import Update
from telegram.ext import CallbackContext


async def error_handler(update: Update, context: CallbackContext) -> None:
    """Log all errors."""
    error_message = context.error
    logging.error(msg="Exception while handling an update:", exc_info=error_message)
    # This fails when the error is not directly caused by a user updated, e.g. in a JobQueue job
    if update is None:
        logging.error("Update is None, cannot send error message to user.")
        return
    await update.effective_user.send_message(
        text=f"An error occurred while processing your message: {error_message}."
    )
