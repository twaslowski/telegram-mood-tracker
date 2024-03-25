import datetime
import emoji

defaults = {
    "metrics": [
        {
            "name": "mood",
            "prompt": "How do you feel right now?",
            "type": "enum",
            "values": {
                f"{emoji.emojize(':zany_face:')}": 3,
                f"{emoji.emojize(':grinning_face_with_smiling_eyes:')}": 2,
                f"{emoji.emojize(':slightly_smiling_face:')}": 1,
                f"{emoji.emojize(':face_without_mouth:')}": 0,
                f"{emoji.emojize(':slightly_frowning_face:')}": -1,
                f"{emoji.emojize(':frowning_face:')}": -2,
                f"{emoji.emojize(':skull:')}": -3,
            },
        },
        {
            "name": "sleep",
            "type": "numeric",
            "prompt": "How much sleep did you get last night?",
            "range": (4, 12),
        },
    ],
    "notifications": [datetime.time(hour=18, minute=00, second=00).isoformat()],
}
