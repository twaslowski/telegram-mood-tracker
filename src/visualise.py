from pymongo import MongoClient
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd

# Connect to MongoDB (replace with your connection details)
client = MongoClient("mongodb://localhost:27017/")
db = client.records
collection = db.records

# Filter records from the last calendar month
start_date = datetime.now() - timedelta(days=30)
query = {"timestamp": {"$gte": start_date.strftime('%Y-%m-%dT%H:%M:%S')}}

# Retrieve data
data = list(collection.find(query))

# Process data
df = pd.DataFrame(data)
df['timestamp'] = pd.to_datetime(df['timestamp']).dt.date
df[['mood', 'sleep']] = df[['mood', 'sleep']].astype(float)

# Calculate daily averages
daily_avg = df.groupby('timestamp')[['mood', 'sleep']].mean().reset_index()

plt.style.use("seaborn-v0_8-dark")

# Plotting
plt.figure(figsize=(10, 6))

# Creating two y-axes
ax1 = plt.gca()  # get current axes
ax2 = ax1.twinx()  # create another axes that shares the same x-axis

# Mood plot on ax1
ax1.plot(daily_avg['timestamp'], daily_avg['mood'], marker='o', color='blue', markersize=3, label='Mood', linestyle='-')
ax1.set_xlabel('Date')
ax1.set_ylabel('Mood', color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_ylim(-5, 5)

# Sleep plot on ax2
ax2.plot(daily_avg['timestamp'], daily_avg['sleep'], marker='o', color='red', label='Sleep', markersize=3, linestyle='--')
ax2.set_ylabel('Sleep', color='red')
ax2.tick_params(axis='y', labelcolor='red')

# Title and layout
plt.title('Average Mood and Sleep over the Last Month')
plt.xticks(rotation=45)
plt.tight_layout()

# Save the plot as a JPG file
plt.savefig('mood_sleep_combined_graph.jpg', format='jpg', dpi=300)

