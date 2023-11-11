mongodump --collection records --db records
aws s3 cp --recursive dump/records/ s3://mood-tracker-backup/records
