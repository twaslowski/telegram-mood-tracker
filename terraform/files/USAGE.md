# Usage

## DEPRECATION NOTICE

I'm discontinuing support for ECR. Please use the Docker Hub image instead. The new repository is:

    tobiaswaslowski/mood-tracker

## Quickstart

You have to create your ownm Telegram via the [Botfather](https://t.me/botfather) and supply it to the container as an environment variable.
Additionally, you'll have to have a MongoDB instance running for persistence.
Assuming you have a MongoDB instance running on your local machine that is bound to `127.0.0.1:27017`,
(e.g. by running `docker run -p 27017:27017 mongo`) you can run the following command:

    docker run --env TELEGRAM_TOKEN=$TELEGRAM_TOKEN \
      tobiaswaslowski/mood-tracker:latest

DynamoDB is also supported as a backend. For more information, check out the [documentation](https://github.com/twaslowski/telegram-mood-tracker?tab=readme-ov-file#running).
