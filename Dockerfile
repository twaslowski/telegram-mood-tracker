FROM python:3.11-slim-bullseye

WORKDIR /app

ENV TELEGRAM_TOKEN=""
ENV MONGODB_HOST="host.docker.internal:27017"
ENV PYTHONPATH=/app

# install dependencies
COPY requirements.txt /app
COPY src /app/src/
COPY config.yaml /app

RUN python3 -m pip install -r /app/requirements.txt

# Temporarily add registry ARG so that deprecation notice can be displayed only for ECR-hosted images
ARG REGISTRY="dockerhub"
ENV REGISTRY=${REGISTRY}

CMD ["python", "src/app.py"]
