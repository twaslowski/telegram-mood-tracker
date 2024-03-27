![Build](https://github.com/TobiasWaslowski/telegram-mood-tracker/actions/workflows/build.yml/badge.svg)

# About

This is a Telegram-based Mood Tracker bot. It allows users to record their mood states and other health-related
metrics. Mood Trackers are generally "useful for people with mental health conditions — such as depression and anxiety —
to help identify and regulate moods" [[1]](https://www.verywellmind.com/what-is-a-mood-tracker-5119337).

It can be difficult to get into the habit of tracking your mood. This project aims at making the process of tracking
your mood on a daily basis as frictionless as possible, by integrating into a popular messaging app that you may
be using on a daily basis anyway.

# Features

This bot comes with several features right now. The version I host is tailored to me and may be fairly basic for other
people's usecases. As of now, you can customize the bot by hosting your own version and modifying the YAML
configuration. However, I am currently building features to enable users to customize their metrics within Telegram.

- You can specify the metrics you would like to track (only on self-hosted instances right now) via YAML spec
- You can set up notifications (only on self-hosted instances right now) via YAML spec

## Features in development

There are more features I want to provide to users to make this bot better.

- The ability to customize metrics and notifications without having to host your own bot
- A /baseline command that you can define as a shorthand for e.g. neutral mood and eight hours of sleep to make
  tracking even more easy
- Customized, more powerful visualization features

# Running

## Quickstart

I host the Docker image for this application on a public ECR repository. All you have to do is to create your own
Telegram via the [Botfather](https://t.me/botfather) and supply it to the container as an environment variable:

    docker run --env TELEGRAM_TOKEN=$TELEGRAM_TOKEN public.ecr.aws/c1o1h8f4/mood-tracker:latest

I currently provide images for x86_64 and arm64v8 for my own machines and my Raspberry Pi. If you require images
for additional architectures, feel free to raise a ticket or build your own images.

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
