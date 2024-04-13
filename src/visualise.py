import calendar
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
from pyautowire import autowire

from src.config.config import ConfigurationProvider
from src.model.metric import Metric
from src.model.record import Record
from src.model.user import User
from src.repository.initialize import initialize_database
from src.repository.record_repository import RecordRepository

"""
Provide graphing functionality for record data.
Is used by handlers/graphing_handler.py to visualize record data.
Can also be used as a standalone by calling the main function.
"""


def visualize(user: User, month: Tuple[int, int]) -> str:
    """
    Generate a line graph of the record data for a given month.
    :param user: User for whom to generate the graph. Needed for metric information.
    :param month: Tuple of (year, month) for the month to visualize. For naming purposes only.
    :return: JPG file path of the generated graph.
    """
    ensure_output_dir()
    # Calculate the first and last day of the given month
    (year, month) = month
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()
    user_metrics = user.metrics

    records = retrieve_records(user.user_id, month)

    records = [record.serialize() for record in records]
    metric_names = [metric.name for metric in user_metrics]

    df = create_panda_df(records, metric_names)

    # In case of multiple records per day, take the average
    daily_avg = df.groupby("timestamp")[metric_names].mean().reset_index()

    # Generate a complete date range for the month
    date_range = pd.date_range(start=first_day, end=last_day)

    plt.style.use("seaborn-v0_8-dark")

    # Plotting
    plt.figure(figsize=(10, 6))

    ax = visualize_metric(plt, date_range, daily_avg, "red", user_metrics[0])
    visualize_metric(plt, date_range, daily_avg, "blue", user_metrics[1], ax)

    # Title and layout
    plt.title(f"Average Mood and Sleep from {first_day} to {last_day}")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot
    file_path = f"graphs/mood_sleep_{first_day}_{last_day}.jpg"
    plt.savefig(file_path, format="jpg", dpi=300)
    return file_path


@autowire("record_repository")
def retrieve_records(
    user_id: int, month: Tuple[int, int], record_repository: RecordRepository
) -> list[Record]:
    """
    Retrieve records for a given month.
    :param user_id: user for whom to retrieve record data.
    :param record_repository: autowired.
    :param month: (year, month) tuple for the month to retrieve records for.
    :return: list of records for the given month.
    """
    (year, month) = month

    # Calculate the first and last day of the given month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])

    records = list(
        record_repository.find_records_for_time_range(user_id, first_day, last_day)
    )
    logging.info(f"Found {len(records)} records for {month}/{year}")
    return records


def ensure_output_dir(output_dir: str = "graphs") -> None:
    """
    Ensure the output directory exists.
    Creates the directory if it does not exist.
    :param output_dir: Directory to ensure exists.
    """
    logging.info(f"Ensuring output directory {output_dir} exists")
    Path(output_dir).mkdir(parents=True, exist_ok=True)


def visualize_metric(
    plt, date_range, daily_avg, color: str, metric: Metric, axis=None
) -> str:
    """
    Create matplotlib axis for a given metric.
    :param records:
    :param metric:
    :return:
    """
    if not axis:
        ax = plt.gca()
    else:
        ax = axis.twinx()
    ax.plot(
        date_range,
        daily_avg.set_index("timestamp").reindex(date_range)[metric.name],
        marker="o",
        color=color,
        label=metric.name.capitalize(),
        markersize=3,
        linestyle="-",
    )
    ax.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)  # Baseline for mood
    ax.set_xlabel("Date")
    ax.set_ylabel(metric.name.capitalize(), color=color)
    ax.tick_params(axis="y", labelcolor=color)
    ax.set_ylim(metric.min_value(), metric.max_value())
    return ax


def create_panda_df(records: list[dict], metrics: list[str]):
    """
    Create a pandas DataFrame from the records for easier visualization purposes.
    :param records: serialized records
    :param metrics: metrics from those records.
    :return: pandas DataFrame
    """
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601").dt.date
    for metric in metrics:
        df[metric] = df["data"].apply(lambda x: x[metric])
    return df


def main(user_id: int, months: list[Tuple[int, int]]):
    """
    Main function that retrieves records for a given month and visualizes them.
    """
    # Provide configuration and databases for application context
    configuration = ConfigurationProvider().get_configuration().register()
    user_repository, record_repository = initialize_database(configuration)

    user = user_repository.find_user(user_id)
    for month in months:
        records = retrieve_records(user_id, month, record_repository=record_repository)
        file_path = visualize(user, records, month)
        logging.info(f"Graph saved to {file_path}")


if __name__ == "__main__":
    main(1965256751, [(2024, 2), (2024, 3), (2024, 4)])
