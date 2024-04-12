import calendar
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
from pyautowire import autowire

from src.model.record import Record
from src.repository.record_repository import RecordRepository


@autowire("record_repository")
def retrieve_records(
    user_id: int, record_repository: RecordRepository, month: Tuple[int, int]
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
    Path(output_dir).mkdir(parents=True, exist_ok=True)


def visualize(records: list[Record], month: Tuple[int, int]) -> str:
    """
    Generate a line graph of the record data for a given month.
    :param records: List of records holding record data.
    :param month: Tuple of (year, month) for the month to visualize.
    :return: JPG file path of the generated graph.
    """
    ensure_output_dir()
    # Calculate the first and last day of the given month
    (year, month) = month
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, calendar.monthrange(year, month)[1]).date()

    records = [record.serialize() for record in records]

    df = create_panda_df(records)

    # Calculate daily averages
    daily_avg = df.groupby("timestamp")[["mood", "sleep"]].mean().reset_index()

    # Generate a complete date range for the month
    date_range = pd.date_range(start=first_day, end=last_day).date

    plt.style.use("seaborn-v0_8-dark")

    # Plotting
    plt.figure(figsize=(10, 6))

    # Creating two y-axes
    # Creating two y-axes
    ax1 = plt.gca()
    ax2 = ax1.twinx()

    # Mood plot on ax1
    ax1.plot(
        date_range,
        daily_avg.set_index("timestamp").reindex(date_range)["mood"],
        marker="o",
        color="blue",
        label="Mood",
        markersize=3,
        linestyle="-",
    )
    ax1.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)  # Baseline for mood
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Mood", color="blue")
    ax1.tick_params(axis="y", labelcolor="blue")
    ax1.set_ylim(-5, 5)

    # Sleep plot on ax2
    ax2.plot(
        date_range,
        daily_avg.set_index("timestamp").reindex(date_range)["sleep"],
        marker="o",
        color="red",
        label="Sleep",
        markersize=3,
        linestyle="--",
    )
    ax2.axhline(y=8, color="gray", linestyle="--", linewidth=0.5)  # sleep baseline
    ax2.set_ylabel("Sleep", color="red")
    ax2.tick_params(axis="y", labelcolor="red")
    ax2.set_ylim(4, 12)

    # Title and layout
    plt.title(f"Average Mood and Sleep from {first_day} to {last_day}")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot
    file_path = f"graphs/mood_sleep_{first_day}_{last_day}.jpg"
    plt.savefig(file_path, format="jpg", dpi=300)
    return file_path


def create_panda_df(records: list[dict]):
    """
    Create a pandas DataFrame from the records for easier visualization purposes.
    :param records: serialized records
    :return: pandas DataFrame
    """
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.date
    df["mood"] = df["data"].apply(lambda x: x["mood"])
    df["sleep"] = df["data"].apply(lambda x: x["sleep"])
    return df


if __name__ == "__main__":
    retrieve_records(1, (2022, 1))
