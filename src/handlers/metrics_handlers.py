from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from src.model.metric import Metric


async def prompt_user_for_metric(update: Update, metric: Metric) -> None:
    """
    Sends InlineKeyboardButton to the user to prompt them for a metric.
    :param update: Telegram Update object
    :param metric: Metric object
    :return:
    """
    bot = update.effective_user.get_bot()
    keyboard = [
        [
            InlineKeyboardButton(
                key.capitalize().replace("_", " "),
                callback_data=f"{metric.name}:{value}",
            )
        ]
        for key, value in metric.values.items()
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(
        chat_id=update.effective_user.id,
        text=metric.user_prompt,
        reply_markup=reply_markup,
    )
