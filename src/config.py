import datetime

defaults = {
    "metrics": [
        {
            "name": "Mood",
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
            "name": "Appetite",
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
            "name": "Weed",
            "type": "enum",
            "prompt": "Have you smoked?",
            "values": {
                "🌳": 1,
                "❌": 0
            },
        },
        {
            "name": "Energy",
            "type": "numeric",
            "prompt": "How much energy do you have right now?",
            "range": (1, 11),
        },
        {
            "name": "Stress",
            "type": "numeric",
            "prompt": "What's your current anxiety like?",
            "range": (1, 11),
        },
        {
            "name": "Irritability",
            "type": "numeric",
            "prompt": "How irritable are you right now?",
            "range": (1, 11),
        },
        {
            "name": "Back pain",
            "type": "numeric",
            "prompt": "How much back pain do you have right now?",
            "range": (1, 11),
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
