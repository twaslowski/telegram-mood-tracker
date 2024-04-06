import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from src.state import State, APPLICATION_STATE
from src.visualise import retrieve_records


def get_all_months_for_offset(
    time_range: int, year: int, month: int
) -> list[tuple[int, int]]:
    """
    Determines how many months should be considered for the graph.
    :param time_range: The number of months to consider.
    Year and month are provided for testability purposes so that I don't have to mock datetime.datetime.now().
    :param year: The current year.
    :param month: The current month.
    :return: a list of tuples (year, month) for the given time range.
    """
    months = [(year, month)]
    for i in range(time_range - 1):
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        months.append((year, month))
    months.reverse()
    return months


async def handle_graph_specification(update):
    """
    Button handler to determine the timeframe for the graph.
    :param update: button press.
    :return: None
    """
    # await timeframe specification
    query = update.callback_query
    await query.answer()

    # calculate arguments for determining time range
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    time_range = int(update.callback_query.data)

    # get all months for the given time range
    months = get_all_months_for_offset(time_range, year, month)

    # create graphs for all months
    for month in months:
        path = retrieve_records(update.effective_user.id, month)
        if path:
            await update.effective_user.get_bot().send_photo(
                update.effective_user.id, open(path, "rb")
            )


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
