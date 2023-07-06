from enum import Enum


class Mood(int, Enum):
    SEVERELY_DEPRESSED = -3
    MODERATELY_DEPRESSED = -2
    MILDLY_DEPRESSED = -1
    NEUTRAL = 0
    MILDLY_ELEVATED = 1
    MODERATELY_ELEVATED = 2
    SEVERELY_ELEVATED = 3

    def get_prompt(self) -> str:
        return "Mood: How do you feel right now?"
