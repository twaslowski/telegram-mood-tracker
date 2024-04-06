# telegram-mood-tracker

This is a Telegram-based Mood Tracker bot. It allows users to record their mood states and other health-related
metrics. Mood Trackers are
generally useful for people with mental health conditions — such as depression and anxiety —
to help identify and regulate moods.

It can be difficult to get into the habit of tracking your mood. This project aims at making the process of tracking
your mood on a daily basis as frictionless as possible, by integrating into a popular messaging app that you may
be using on a daily basis anyway.

The following is an outline of the features of this bot, how to run it, and how to use it.
For more details, check out its [GitHub repository](https://github.com/twaslowski/telegram-mood-tracker).

## Features

This bot allows you to ...

- specify metrics to track
- specify notifications to be sent to you at any time
- set up baselines for metrics to make tracking easier
- automatically create baseline records on a daily basis to make tracking _even easier_
- Visualize metrics over time

I host a bot for both demo-purposes and personal use, but you can also host your own bot.
I'm not going to put too much effort into making my bot 100% configurable unless it suddenly gains hundreds of users,
but I'll probably set it up, so you can add your own configuration by sending it a YAML file or something.

But generally, you're going to be better off hosting your own bot.

## Bot Commands

The bot currently supports the following commands:

- `/start`: This is the conversation start with the bot. It will initialise your user data in the database
- from the configuration loaded from the `config.yaml` at application start.

- `/record`: This command will prompt you to record your mood. It iterates through your metrics and asks you to
  provide values for each of them. Note that while creating a record, they are held in an `ExpiringDict` until they
  are completed; they expire after 300 seconds by default. Upon completion, a `record` is stored in the database.

- `/baseline`: If you have provided baselines for all your metrics in the configuration , you can use this command
  to create a record with your baseline metrics. This is useful if you are relatively stable and don't want to click
  through the entire record process every day.

- `auto_baseline`: This command enables automatically creating baseline records for you if you have not recorded your
  mood by a specific time. You can configure this feature in the and toggle it via this command.

- `/graph`: Plot selected metrics over time.
