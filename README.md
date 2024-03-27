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

# Developing