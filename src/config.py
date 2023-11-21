import datetime

config = {
    "metrics": [
        {
            "name": "mood",
            "prompt": "How do you feel right now?",
            "type": "enum",
            "values": {
                "SEVERELY_ELEVATED": 3,
                "MODERATELY_ELEVATED": 2,
                "MILDLY_ELEVATED": -1,
                "NEUTRAL": 0,
                "MILDLY_DEPRESSED": -1,
                "MODERATELY_DEPRESSED": -2,
                "SEVERELY_DEPRESSED": -3
            },
        },
        {
            "name": "appetite",
            "type": "enum",
            "prompt": "Are you eating enough?",
            "values": {
                "SEVERELY_REDUCED_APPETITE": -2,
                "REDUCED_APPETITE": -1,
                "NORMAL_APPETITE": 0,
                "INCREASED_APPETITE": 1
            },
        },
        {
            "name": "weed",
            "type": "enum",
            "prompt": "Have you smoked?",
            "values": {
                "🌳": 1,
                "❌": 0
            },
        },
        {
            "name": "energy",
            "type": "numeric",
            "prompt": "How much energy do you have right now?",
            "range": (1, 11),
        },
        {
            "name": "stress",
            "type": "numeric",
            "prompt": "How much are you currently under?",
            "range": (1, 11),
        },
        {
            "name": "irritability",
            "type": "numeric",
            "prompt": "Are you more or less irritable than usual?",
            "range": (1, 11),
        },
        {
            "name": "back_pain",
            "type": "numeric",
            "prompt": "How much back pain do you have right now?",
            "range": (1, 11),
        },
        {
            "name": "sleep",
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
