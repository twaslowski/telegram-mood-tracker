sudo docker run -d --rm \
  --name mood-tracker \
  -e TELEGRAM_TOKEN="$TELEGRAM_TOKEN" \
  -e MONGODB_HOST="$MONGODB_HOST" \
  --network host \
  --log-driver=awslogs \
  --log-opt awslogs-region="$LOG_REGION" \
  --log-opt awslogs-group="$LOG_GROUP" \
  --log-opt awslogs-stream="$LOG_STREAM" \
  --security-opt seccomp:unconfined \
  public.ecr.aws/c1o1h8f4/mood-tracker:latest
