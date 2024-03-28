# telegram-mood-tracker

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
