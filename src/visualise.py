import calendar
import logging
from datetime import datetime
from typing import Tuple

import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient


def visualize_monthly_data(user_id: int, month: Tuple[int, int] = None):
    # Connect to MongoDB (replace with your connection details)
    client = MongoClient("mongodb://localhost:27017/")
    db = client.mood_tracker
    collection = db.records

    (year, month) = month

    # Calculate the first and last day of the given month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])

    logging.info(f"Retrieving data for between {first_day} and {last_day} for user {user_id}")
    # Filter records for the specified month
    query = {"timestamp": {"$gte": first_day.strftime('%Y-%m-%dT%H:%M:%S'),
                           "$lte": last_day.strftime('%Y-%m-%dT%H:%M:%S')},
             "user_id": user_id}

    data = list(collection.find(query))

    data = [{'timestamp': data['timestamp'], 'mood': data['record']['Mood'], 'sleep': data['record']['Sleep']}
            for data in data]
    logging.info(f"Found {len(data)} records for {month}/{year}")

    if not data:
        return

    # Process data
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp']).dt.date
    df[['mood', 'sleep']] = df[['mood', 'sleep']].astype(float)

    # Calculate daily averages
    daily_avg = df.groupby('timestamp')[['mood', 'sleep']].mean().reset_index()

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
    ax1.plot(date_range, daily_avg.set_index('timestamp').reindex(date_range)['mood'], marker='o', color='blue',
             label='Mood', markersize=3, linestyle='-')
    ax1.axhline(y=0, color='gray', linestyle='--', linewidth=0.5)  # Baseline for mood
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Mood', color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')
    ax1.set_ylim(-5, 5)

    # Sleep plot on ax2
    ax2.plot(date_range, daily_avg.set_index('timestamp').reindex(date_range)['sleep'], marker='o', color='red',
             label='Sleep', markersize=3, linestyle='--')
    ax2.axhline(y=8, color='gray', linestyle='--', linewidth=0.5)  # sleep baseline
    ax2.set_ylabel('Sleep', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(4, 12)

    # Title and layout
    plt.title(f'Average Mood and Sleep for {month}/{year}')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot
    file_path = f'graphs/mood_sleep_{year}_{month}.jpg'
    plt.savefig(file_path, format='jpg', dpi=300)
    return file_path


if __name__ == '__main__':
    visualize_monthly_data()
