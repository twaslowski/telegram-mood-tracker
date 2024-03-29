FROM python:3.11-slim-bullseye

ENV TELEGRAM_TOKEN=""
ENV MONGODB_HOST="host.docker.internal:27017"
ENV PYTHONPATH=./

# install dependencies
COPY requirements.txt .
COPY src ./src/
COPY config.yaml .

RUN python3 -m pip install -r requirements.txt

CMD ["python", "src/app.py"]
