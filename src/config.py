metrics_configuration = {
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
    "energy": {
        "type": "numeric",
        "prompt": "Energy: How much energy do you have right now?",
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
    },
}
