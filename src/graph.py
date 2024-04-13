import calendar
import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
from pandas import DatetimeIndex
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


class Graph:
    """
    This class encapsulates the functionality to visualize record data.
    :param user: User object to retrieve metrics from.
    :param month: Tuple of year and month to visualize.
    :param record_repository: RecordRepository to retrieve records from.
    :return: Path to the generated graph.
    """

    # Provided
    year: int
    month: int
    user: User
    # Autowired
    record_repository: RecordRepository
    # Calculated
    first_day: datetime.date
    last_day: datetime.date
    # Output
    path: str | None = None

    @autowire("record_repository")
    def __init__(
        self, user: User, month: Tuple[int, int], record_repository: RecordRepository
    ):
        self.year, self.month = month
        self.user = user
        self.record_repository = record_repository
        self.first_day = datetime(self.year, self.month, 1).date()
        self.last_day = datetime(
            self.year, self.month, calendar.monthrange(self.year, self.month)[1]
        ).date()
        records = self.retrieve_records_for_month()
        self.ensure_output_dir()
        self.path = self.visualize(records)

    def get_path(self):
        return self.path

    def retrieve_records_for_month(self) -> list[Record]:
        """
        Retrieve records for a given month.
        :return: list of records for the given month.
        """
        # Calculate the first and last day of the given month
        first_day = datetime(self.year, self.month, 1)
        last_day = datetime(
            self.year, self.month, calendar.monthrange(self.year, self.month)[1]
        )

        records = list(
            self.record_repository.find_records_for_time_range(
                self.user.user_id, first_day, last_day
            )
        )
        logging.info(f"Found {len(records)} records for {self.month}/{self.year}")
        return records

    @staticmethod
    def ensure_output_dir(output_dir: str = "graphs") -> None:
        """
        Ensure the output directory exists.
        Creates the directory if it does not exist.
        :param output_dir: Directory to ensure exists.
        """
        logging.info(f"Ensuring output directory {output_dir} exists")
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def visualize(self, records: list[Record]) -> str:
        """
        Generate a line graph of the record data for a given month.
        :param records: List of records holding record data.
        :return: JPG file path of the generated graph.
        """
        # Calculate the first and last day of the given month
        records = [record.serialize() for record in records]
        metric_names = [metric.name for metric in self.user.metrics]

        df = self.create_panda_df(records)

        # In case of multiple records per day, take the average
        daily_avg = df.groupby("timestamp")[metric_names].mean().reset_index()

        # Generate a complete date range for the month
        date_range = pd.date_range(start=self.first_day, end=self.last_day)

        self.graph_meta()

        ax = None
        colors = ["red", "blue"]
        for i, metric in enumerate(self.user.metrics):
            ax = self.visualize_metric(date_range, daily_avg, colors[i], metric, ax)

        return self.save_graph()

    def save_graph(self):
        # Save the plot
        file_path = f"graphs/mood_sleep_{self.first_day}_{self.last_day}.jpg"
        plt.savefig(file_path, format="jpg", dpi=300)
        return file_path

    def graph_meta(self):
        plt.style.use("seaborn-v0_8-dark")
        # Plotting
        plt.figure(figsize=(10, 6))
        # Title and layout
        plt.title(f"Average Mood and Sleep from {self.first_day} to {self.last_day}")
        plt.xticks(rotation=45)
        plt.tight_layout()

    @staticmethod
    def visualize_metric(
        date_range: DatetimeIndex, daily_avg, color: str, metric: Metric, axis=None
    ) -> str:
        """
        Create matplotlib axis for a given metric.
        :param axis:
        :param color:
        :param daily_avg:
        :param date_range:
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
        ax.axhline(
            y=0, color="gray", linestyle="--", linewidth=0.5
        )  # Baseline for mood
        ax.set_xlabel("Date")
        ax.set_ylabel(metric.name.capitalize(), color=color)
        ax.tick_params(axis="y", labelcolor=color)
        ax.set_ylim(metric.min_value(), metric.max_value())
        return ax

    def create_panda_df(self, records: list[dict]):
        """
        Create a pandas DataFrame from the records for easier visualization purposes.
        :param records: serialized records
        :return: pandas DataFrame
        """
        df = pd.DataFrame(records)
        df["timestamp"] = pd.to_datetime(df["timestamp"], format="ISO8601").dt.date
        for metric in [metric.name for metric in self.user.metrics]:
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
        graph = Graph(user, month)


if __name__ == "__main__":
    main(1965256751, [(2024, 2), (2024, 3), (2024, 4)])
