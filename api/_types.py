from enum import StrEnum
from typing import Set


class States(StrEnum):
    ANGRY = "ANGRY"
    FEAR = "FEAR"
    HAPPY = "HAPPY"
    HATE = "HATE"
    OTHER = "OTHER"
    SAD = "SAD"
    SURPRISE = "SURPRISE"

    @classmethod
    def get_all_states(cls) -> Set[str]:
        return set(cls)
