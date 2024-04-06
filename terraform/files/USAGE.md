# Usage

## Quickstart

I host the Docker image for this application on a public ECR repository. You have to create your own
Telegram via the [Botfather](https://t.me/botfather) and supply it to the container as an environment variable.
Additionally, you'll have to have a MongoDB instance running for persistence.
Assuming you have a MongoDB instance running on your local machine that is bound to `127.0.0.1:27017`,
(e.g. by running `docker run -p 27017:27017 mongo`) you can run the following command:

    docker run --env TELEGRAM_TOKEN=$TELEGRAM_TOKEN \
      public.ecr.aws/c1o1h8f4/mood-tracker:latest

Supported architectures are x86_64 (amd64) and arm64. If you require images
for additional architectures, feel free to raise a ticket or build your own images (see [Development](#development)).

## MongoDB Configuration

If your MongoDB instance is bound to a different hosts, you'll have to supply the connection string as an environment
variable. If you're running Docker for Linux, I recommend using `--network="host"` for simplicity's sake.
The run command in that case could look like this:

    docker run --env TELEGRAM_TOKEN=$TELEGRAM_TOKEN \
        --env MONGO_HOST=192.168.1.1:27017 \
        --network="host" \
          public.ecr.aws/c1o1h8f4/mood-tracker:latest

For more guidance on Docker networking, please refer to the [official documentation](https://docs.docker.com/network/).
