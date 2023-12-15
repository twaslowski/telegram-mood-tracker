mongodump --host "192.168.178.61" --collection records --db mood_tracker
aws s3 cp --recursive dump/records/ s3://mood-tracker-backup/records
