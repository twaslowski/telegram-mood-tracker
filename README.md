# About

This is a Telegram-based mood tracker for individuals suffering from [bipolar disorder](https://www.nimh.nih.gov/health/topics/bipolar-disorder).
It allows the specification of arbitrary metrics that can be tracked and persisted on a regular basis for later evaluation.

# Motivation

As the US National Institute of Mental Health states: _Bipolar disorder (formerly called manic-depressive illness or manic depression)
is a mental illness that causes unusual shifts in a person’s mood, energy, activity levels, and concentration._

One tool in the therapy process for bipolar disorder is the use of a mood tracker. Mood trackers enable individuals
to record and track metrics like sleep, mood, medication dosages and other things over a long amount of time.
However, which metrics should be tracked highly depends on the individual. If someone takes mood-balancing medication,
they may be less prone to obvious mood swings, and other metrics may become more important.

However, most mood trackers that offer such advanced features are either locked behind paywalls or lack
easy usability. For people to build habits, such tools need to be easily accessible. This is an attempt at
building such a tool. It is in an early MVP stage right now, where mood states can only be recorded and persisted,
not evaluated, but this will be implemented over time.

# Building and Running

If you would like to try this bot out on your own, you can run it on your own machine, or preferably a
Raspberry Pi or on a free tier AWS EC2 t2.micro instance. The requirements are:

- Python 3.10+
- Docker
- A valid Telegram API token ([learn more here](https://core.telegram.org/bots/tutorial))

 With those prerequisites, simply run the following commands:

    $ git clone git@github.com:TobiasWaslowski/telegram-mood-tracker.git && cd telegram-mood-tracker
    $ echo $YOUR_TELEGRAM_TOKEN > .env
    $ ./run.sh
