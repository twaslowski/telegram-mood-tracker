import datetime

metrics = {
    "mood": {
        "prompt": "Mood: How do you feel right now?",
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
    "appetite": {
        "type": "enum",
        "prompt": "Appetite: Are you eating enough?",
        "values": {
            "SEVERELY_REDUCED_APPETITE": -2,
            "REDUCED_APPETITE": -1,
            "NORMAL_APPETITE": 0,
            "INCREASED_APPETITE": 1
        },
    },
    "weed": {
        "type": "enum",
        "prompt": "Weed: Have you smoked?",
        "values": {
            "🌳": 1,
            "❌": 0
        },
    },
    "energy": {
        "type": "numeric",
        "prompt": "Energy: How much energy do you have right now?",
        "range": (1, 11),
    },
    "stress": {
        "type": "numeric",
        "prompt": "Stress: How much are you currently under?",
        "range": (1, 11),
    },
    "irritability": {
        "type": "numeric",
        "prompt": "Irritability: Are you more or less irritable than usual?",
        "range": (1, 11),
    },
    "back_pain": {
        "type": "numeric",
        "prompt": "Back pain: How much back pain do you have right now?",
        "range": (1, 11),
    },
    "sleep": {
        "type": "numeric",
        "prompt": "Sleep: How much sleep did you get last night?",
        "range": (4, 12),
    }
}

notifications = [
    datetime.time(hour=8, minute=00, second=00),
    datetime.time(hour=18, minute=00, second=00)
]
