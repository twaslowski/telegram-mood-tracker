import calendar
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient


def visualize_monthly_data(year: str = None, month: str = None):
    # Connect to MongoDB (replace with your connection details)
    client = MongoClient("mongodb://localhost:27017/")
    db = client.records
    collection = db.records

    if year is None or month is None:
        now = datetime.now()
        year = now.year
        month = now.month

    # Calculate the first and last day of the given month
    first_day = datetime(year, month, 1)
    last_day = datetime(year, month, calendar.monthrange(year, month)[1])

    # Filter records for the specified month
    query = {"timestamp": {"$gte": first_day.strftime('%Y-%m-%dT%H:%M:%S'),
                           "$lte": last_day.strftime('%Y-%m-%dT%H:%M:%S')}}

    # Retrieve data
    data = list(collection.find(query))

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
    ax2.axhline(y=8, color='gray', linestyle='--', linewidth=0.5) # sleep baseline
    ax2.set_ylabel('Sleep', color='red')
    ax2.tick_params(axis='y', labelcolor='red')
    ax2.set_ylim(4, 12)

    # Title and layout
    plt.title(f'Average Mood and Sleep for {month}/{year}')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot
    plt.savefig(f'../graphs/mood_sleep_{year}_{month}.jpg', format='jpg', dpi=300)


if __name__ == '__main__':
    visualize_monthly_data()
