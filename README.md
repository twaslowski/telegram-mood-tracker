![Build](https://github.com/twaslowski/telegram-mood-tracker/actions/workflows/build.yml/badge.svg)

# About

This is a Telegram-based Mood Tracker bot. It allows users to record their mood states and other health-related
metrics. Mood Trackers are
generally "[useful for people with mental health conditions — such as depression and anxiety —
to help identify and regulate moods](https://www.verywellmind.com/what-is-a-mood-tracker-5119337)".

It can be difficult to get into the habit of tracking your mood. This project aims at making the process of tracking
your mood on a daily basis as frictionless as possible, by integrating into a popular messaging app that you may
be using on a daily basis anyway.

# Features

This bot allows you to ...

- specify metrics to track
- specify notifications to be sent to you at any time
- set up baselines for metrics to make tracking easier
- automatically create baseline records on a daily basis to make tracking _even easier_<sup>1</sup>
- Visualize metrics over time <sup>2</sup>

I host a bot for both demo-purposes and personal use, but you can also host your own bot.
I'm not going to put too much effort into making my bot 100% configurable unless it suddenly gains hundreds of users,
but I'll probably add an option to configure it by sending it a YAML file or something. If you want to try it out,
find it here: [Mood Tracker Bot](https://t.me/bipolar_mood_tracker_bot).

But generally, you're going to be better off hosting your own bot. Find out how in the [Running](#running) section.

<sup>1 Meaning that if you have not tracked your mood by end of day, a record with your baseline values will be created.
This makes tracking easier if you are relatively stable for long amounts of time.</sup>

<sup>2 This feature currently only works for mood and sleep. I haven't put too much time into visualization yet.
If you have any `matplotlib` or `seaborn` experience and want to contribute, feel free to raise a PR.</sup>

## Bot Commands

The bot currently supports the following commands:

- `/start`: This is the conversation start with the bot. It will initialise your user data in the database
- from the configuration loaded from the `config.yaml` at application start.

- `/record`: This command will prompt you to record your mood. It iterates through your metrics and asks you to
  provide values for each of them. Note that while creating a record, they are held in an `ExpiringDict` until they
  are completed; they expire after 300 seconds by default. Upon completion, a `record` is stored in the database.

- `/baseline`: If you have provided baselines for all your metrics in the configuration
  (for more details, check the [configuration section](#specifying-metrics)), you can use this command to create a
  record with your baseline metrics. This is useful if you are relatively stable and don't want to click through
  the entire record process every day.

- `auto_baseline`: This command enables automatically creating baseline records for you if you have not recorded your
  mood by a specific time. You can configure this feature in the [configuration section](#specifying-metrics)
  and toggle it via this command.

- `/graph`: Plot selected metrics over time.

# Running

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

## Persistence

There are two persistence backends you can choose to store user data: MongoDB, for running everything locally,
or DynamoDB, if you would like to take advantage of a serverless, managed database. This offers you the ability
to not have to worry about scaling, backups, or any other database-related tasks.

You can specify the persistence configuration in the `config.yaml`:

    database:
        type: 'dynamodb'
        aws_region: 'us-east-1'

Note that if you choose `dynamodb` as a persistence backend, you have to supply the `aws_region` as well.
The default is `mongodb`.

### MongoDB Configuration

If your MongoDB instance is bound to a different hosts, you'll have to supply the connection string as an environment
variable. If you're running Docker for Linux, I recommend using `--network="host"` for simplicity's sake.
The run command in that case could look like this:

    docker run --env TELEGRAM_TOKEN=$TELEGRAM_TOKEN \
        --env MONGO_HOST=192.168.1.1:27017 \
        --network="host" \
          public.ecr.aws/c1o1h8f4/mood-tracker:latest

For more guidance on Docker networking, please refer to the [official documentation](https://docs.docker.com/network/).

### DynamoDB

Using DynamoDB is more challenging, but brings substantial benefits, like scalability and automated backups.
Beyond simply configuring DynamoDB as a backend for the bot, you'll have to set up authentication. I have set up
static user credentials with the proper permissions and mount them onto the container as a volume.

There are different mechanisms for providing Docker containers with AWS credentials.
[This StackOverflow thread](https://stackoverflow.com/questions/36354423/what-is-the-best-way-to-pass-aws-credentials-to-a-docker-container)
goes into a lot of depth on this topic. You can refer to `scripts/run.sh` for an example of how to do this:

```bash
docker run -d --rm \
  --name mood-tracker \
  -e TELEGRAM_TOKEN="$TELEGRAM_TOKEN" \
  -v "$HOME/.aws/credentials:/root/.aws/credentials:ro" \
  public.ecr.aws/c1o1h8f4/mood-tracker:latest
```

Why `/root/.aws/credentials`? Because `boto3` checks in the home directory of the user running the script for the
credentials, and that's what this happens to be. I tried a bunch of configurations and found this to just work.

## Mounting Configuration files onto a Docker container

You may not want to build a custom image in which your configuration is stored.
You can write your own custom configuration and mount it into a container from one of my images like this:

```shell
docker run -d --rm \
  --name mood-tracker \
  -e TELEGRAM_TOKEN="$TELEGRAM_TOKEN" \
  -v ./config.yaml:/app/config.yaml \
  public.ecr.aws/c1o1h8f4/mood-tracker:latest
  ```

# Configuration

When hosting your own bot, you can use the `config.yaml` file to specify your own metrics and notifications.
The following section will guide you through the configuration process.

## Specifying Metrics

```yaml
metrics:
  - name: anxiety
    user_prompt: "What are your anxiety levels like right now?"
    values:
      HIGHLY_ANXIOUS: 2
      SOMEWHAT_ANXIOUS: 1
      CALM: 0
```

Metrics have to map to numbers under the hood for purposes of visualization.
These will show up as [Inline Buttons](https://core.telegram.org/bots/2-0-intro#switch-to-inline-buttons) when recording
your mood, with the labels showing up as "Highly Anxious", "Somewhat Anxious" and "Calm".

### Using Emojis

If you want to be cute, you can configure the above metric with emojis as well. Simply set the proper flag and
specify emoji codes that can be mapped internally:

```yaml
metrics:
  - name: anxiety
    user_prompt: "What are your anxiety levels like right now?"
    emoji: true
    values:
    ":face_screaming_in_fear:": 2
    ":fearful_face:": 1
    ":face_without_mouth:": 0
```

If you want to find emojis, I suggest doing so on the official webpage of the
[Unicode Consortium](https://unicode.org/emoji/charts/full-emoji-list.html). Generally, you can take the name like
"downcast face with sweat" and turn it into snakecase ("downcast_face_with_sweat") and put it into `emoji.emojize()`
to see if it will work or not.

### Strictly Numerical Metrics

There are metrics that are entirely numerical in nature. Let's say you want to track the amount of hours you sleep.
In this case, the labels would be exactly equal to their values ("8" would just map to the value 8).

For this case, I've added a metric type called `numeric`. You can declare `numeric` metrics like this:

```yaml
  - name: sleep
    user_prompt: "How much sleep did you get today?"
    type: numeric
    values:
      lower_bound: 4
      upper_bound: 12
```

This will auto-generate the corresponding dictionary for you, without you having to painstakingly type out every
possible value.

### Baselines

For convenience purposes, if you are relatively stable and don't want to click through the entire record process,
the recording process can be turned from at least three clicks to just one by specifying baselines for your metrics
and calling `/baseline` in the bot.

```yaml
metrics:
  - name: anxiety
    user_prompt: "What are your anxiety levels like right now?"
    baseline: 0
    values:
      HIGHLY_ANXIOUS: 2
      SOMEWHAT_ANXIOUS: 1
      CALM: 0
```

### Database Configuration

...

## Notifications

You can specify notifications as a list of text/time strings. Because no user information is available except for the
user_id, there is no localization, so all times are interpreted as UTC. If you want your reminder to be at 8:00 AM
CET, you'll have to specify it as 7:00 AM UTC (or whatever the time difference is, think of daylight savings).

```yaml
notifications:
  - text: "Don't forget to track your mood today!"
    time: "7:00"
```

## Auto-Baseline

If you want to automatically create a baseline record for you if you have not recorded your mood by a specific time,
you can specify the `auto_baseline` key in the configuration file. This will, at that point, create a record with your
baseline values for all metrics.

```yaml
auto_baseline:
  enabled: true
  time: "23:59"
```

You can toggle `auto_baseline` via the `/auto_baseline` command in the bot. However, you **need** to specify the `time`
in the `config.yaml` first in order to do that.

## Database

As outlined above, you can choose between MongoDB and DynamoDB as a persistence backend. You can specify the type
in the `config.yaml`:

```yaml
database:
  type: 'dynamodb' | 'mongodb'
  aws_region: 'us-east-1' [optional]
```

# Developing

If you'd like to contribute to this repository, feel free to raise a PR.
You'll have to have Poetry and Python 3.11 installed.
You can clone the repo and set up your own poetry environment:

```shell
git clone git@github.com:twaslowski/telegram-mood-tracker.git && cd telegram-mood-tracker
pyenv install 3.11.6  # or another patch version
poetry env use 3.11.6  # or another patch version
poetry install --with dev
```

I encourage the use of pre-commit hooks. You can enable them by running

```shell
pre-commit install
pre-commit run --all-files --verbose
```

If you would like to build a custom Docker image, you can do so by running

```shell
docker build -t mood-tracker:latest .
```
