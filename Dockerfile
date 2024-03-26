FROM python:3.11-slim-bullseye

ENV TELEGRAM_TOKEN=""
ENV MONGODB_HOST="localhost:27017"

# install dependencies
COPY package/requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY src ./src/

CMD ["python", "src/app.py"]
