from dataclasses import dataclass


@dataclass
class Phase:
    name: str
    time_remaining: float
    description: str
    modifiers: dict[str, float]


class PhaseManager:
    def __init__(self):
        self.__modifiers: dict[str, float] = {}
