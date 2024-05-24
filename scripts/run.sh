#!/bin/bash

# This is how I personally choose to run the image.
# I stream my logs to CloudWatch because it is convenient, and so I configure the log driver accordingly.
# The --security-opt seccomp:unconfined flag is an unfortunate necessity because certain arm64 images do not run
# properly on Raspberry Pis without it.
# This is a known issue: https://github.com/distribution/distribution/issues/3008

sudo docker run -d --rm \
  --name mood-tracker \
  -e TELEGRAM_TOKEN="$TELEGRAM_TOKEN" \
  -e MONGODB_HOST="$MONGODB_HOST" \
  --network host \
  --log-driver=awslogs \
  --log-opt awslogs-region="$LOG_REGION" \
  --log-opt awslogs-group="$LOG_GROUP" \
  --log-opt awslogs-multiline-pattern='^ERROR' \
  --security-opt seccomp:unconfined \
  -v "$HOME/.aws/credentials:/root/.aws/credentials:ro" \
  -v ./config.yaml:/app/config.yaml \
  tobiaswaslowski/mood-tracker:latest
