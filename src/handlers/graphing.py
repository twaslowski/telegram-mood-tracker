import datetime

from pyautowire import autowire
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from src.repository.user_repository import UserRepository
from src.state import State, APPLICATION_STATE
from src.visualise import visualize, Month


@autowire("user_repository")
async def handle_graph_specification(
    update, user_repository: UserRepository
) -> list[str]:
    """
    Button handler to determine the timeframe for the graph.
    :param user_repository: autowired.
    :param update: button press.
    :return: None
    """
    # await timeframe specification
    query = update.callback_query
    await query.answer()

    # calculate arguments for determining time range
    time_range = int(update.callback_query.data)

    # get all months for the given time range
    months = get_month_tuples_for_time_range(time_range)

    # Get user data to access their metrics configuration
    user = user_repository.find_user(update.effective_user.id)

    paths = []
    # create graphs for all months
    for month in months:
        path = visualize(user, month)
        paths.append(path)
        if path:
            await update.effective_user.get_bot().send_photo(
                update.effective_user.id, open(path, "rb")
            )
    return paths


def get_month_tuples_for_time_range(
    time_range: int,
    year: int = datetime.datetime.now().year,
    month: int = datetime.datetime.now().month,
) -> list[Month]:
    """
    Determines how many months should be considered for the graph.
    :param time_range: The number of months to consider.
    Year and month are provided for testability purposes so that I don't have to mock datetime.datetime.now().
    :param year: The current year.
    :param month: The current month.
    :return: a list of tuples (year, month) for the given time range.
    """

    months = [Month(year, month)]
    for i in range(time_range - 1):
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        months.append(Month(year, month))
    months.reverse()
    return months


async def graph_handler(update: Update, context) -> None:
    await handle_graphing_dialog(update, context)
    APPLICATION_STATE[update.effective_user.id] = State.GRAPHING


async def handle_graphing_dialog(update: Update, _) -> None:
    bot = update.effective_user.get_bot()
    keyboard = [
        [InlineKeyboardButton("Last month", callback_data="1")],
        [InlineKeyboardButton("Last three months", callback_data="3")],
        [InlineKeyboardButton("All time", callback_data="12")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await bot.send_message(
        chat_id=update.effective_user.id,
        text="How many months would you like me to graph?",
        reply_markup=reply_markup,
    )
