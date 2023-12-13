import datetime

defaults = {
    "metrics": [
        {
            "name": "Mood",
            "prompt": "How do you feel right now?",
            "type": "enum",
            "values": {
                "\U0001F92A": 3,
                "\uE415": 2,
                "\U0001F642": 1,
                "\U0001F636": 0,
                "\U0001F615": -1,
                "\u2639\uFE0F": -2,
                "\uE11C": -3
            },
        },
        {
            "name": "Sleep",
            "type": "numeric",
            "prompt": "How much sleep did you get last night?",
            "range": (4, 12),
        }
    ],
    "notifications": [
        # two hour offset makes these 8am and 6pm
        datetime.time(hour=6, minute=00, second=00).isoformat(),
        datetime.time(hour=16, minute=00, second=00).isoformat()
    ]
}
