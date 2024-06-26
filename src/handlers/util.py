import logging

from telegram import Update
from telegram.error import TimedOut
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    retry=retry_if_exception_type((TimeoutError, TimedOut)),
)
async def send(update: Update, text: str):
    """
    Sends a message to the chat. Shorthand utility to keep the code clean.
    :param update: Update from the Telegram bot.
    :param text: The message to send.
    """
    logging.info(f"Sending message to {update.effective_user.id}: {text}")
    await update.effective_user.get_bot().send_message(
        chat_id=update.effective_user.id, text=text
    )


async def handle_no_known_state(update: Update) -> None:
    """
    Handles the case where the user is not in a known state.
    This can happen if the user has not started recording or graphing, or if the state has expired.
    :param update: The update object.
    """
    no_state_message = (
        "It doesn't appear like you're currently recording mood or graphing. "
        "Press /record to create a new record, /graph to visualise your mood progress."
    )
    await send(update, text=no_state_message)
