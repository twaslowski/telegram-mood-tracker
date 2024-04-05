![Build](https://github.com/twaslowski/telegram-mood-tracker/actions/workflows/build.yml/badge.svg)

[1. About](#about)
[2. Features](#features)
[3. Running](#running)
  [3.1. Quickstart](#quickstart)
  [3.2. MongoDB Configuration](#mongodb-configuration)
  [3.3. Specifying Metrics](#specifying-metrics)
    [3.3.1. Using Emojis](#using-emojis)
    [3.3.2. Strictly Numerical Metrics](#strictly-numerical-metrics)
  [3.4. Reminders](#reminders)
[4. Developing](#developing)

# About

This is a Telegram-based Mood Tracker bot. It allows users to record their mood states and other health-related
metrics. Mood Trackers are generally "[useful for people with mental health conditions — such as depression and anxiety —
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
but I'll probably set it up, so you can add your own configuration by sending it a YAML file or something.

But generally, you're going to be better off hosting your own bot. Find out how in the [Running](#running) section.

<sup>1 Meaning that if you have not tracked your mood by end of day, a record with your baseline values will be created.
This makes tracking easier if you are relatively stable for long amounts of time.</sup>

<sup>2 This feature currently only works for mood and sleep. I haven't put too much time into visualization yet.
If you have any `matplotlib` or `seaborn` experience and want to contribute, feel free to raise a PR.</sup>

# Running

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

## Specifying Metrics

In the `config.yaml` you can configure your own metrics and notifications. For example, you can track your own mood
as follows:

```yaml
metrics:
  - name: anxiety
    user_prompt: "What are your anxiety levels like right now?"
    values:
      HIGHLY_ANXIOUS: 2
      SOMEWHAT_ANXIOUS: 1
      CALM: 0
```

Metrics have to map to numbers under the hood for purposes of visualization and statistical evaluation (potentially).
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

## Reminders

You can specify reminders as a list of text/time strings. Because no user information is available except for the
user_id, there is no localization, so all times are interpreted as UTC. If you want your reminder to be at 8:00 AM
CET, you'll have to specify it as 7:00 AM UTC.

```yaml
notifications:
  - text: "Don't forget to track your mood today!"
    time: "7:00"
```

# Developing

If you'd like to contribute to this repository, feel free to raise a PR.
You'll have to have Poetry and Python 3.11 installed.
You can clone the repo and set up your own poetry environment:

```shell
git clone git@github.com:twaslowski/telegram-mood-tracker.git && cd telegram-mood-tracker
poetry env use 3.11.6  # or another patch version
poetry install --with dev
make test
```

I encourage the use of pre-commit hooks. You can enable them by running

```shell
pre-commit install
pre-commit run --all-files --verbose
```
