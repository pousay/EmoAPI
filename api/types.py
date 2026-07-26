from typing import Set


class States:
    ANGRY = "ANGRY"
    FEAR = "FEAR"
    HAPPY = "HAPPY"
    HATE = "HATE"
    OTHER = "OTHER"
    SAD = "SAD"
    SURPRISE = "SURPRISE"

    @staticmethod
    def get_all_states() -> Set[str]:
        return {"ANGRY", "FEAR", "HAPPY", "HATE", "OTHER", "SAD", "SURPRISE"}

    