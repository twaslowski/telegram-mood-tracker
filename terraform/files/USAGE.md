## Quickstart

I host the Docker image for this application on a public ECR repository. You have to create your own
Telegram via the [Botfather](https://t.me/botfather) and supply it to the container as an environment variable.
Additionally, you'll have to have a MongoDB instance running for persistence.
Assuming you have a MongoDB instance running on your local machine that is bound to `127.0.0.1:27017`,
you can run the following command:

    docker run --env TELEGRAM_TOKEN=$TELEGRAM_TOKEN \
      public.ecr.aws/c1o1h8f4/mood-tracker:latest

I currently provide images for x86_64 and arm64v8 for my own machines and my Raspberry Pi. If you require images
for additional architectures, feel free to raise a ticket or build your own images.

## MongoDB Configuration

If your MongoDB instance is bound to a different hosts, you'll have to supply the connection string as an environment
variable. If you're running Docker for Linux, I recommend using `--network="host"` for simplicity's sake.
The run command in that case could look like this:

    docker run --env TELEGRAM_TOKEN=$TELEGRAM_TOKEN \
        --env MONGO_HOST=192.168.12.123:27017 \
        --network="host" \
          public.ecr.aws/c1o1h8f4/mood-tracker:latest

For more guidance on Docker networking, please refer to the [official documentation](https://docs.docker.com/network/).
