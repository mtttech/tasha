from dataclasses import dataclass, field
from math import floor
from typing import Dict, List

import dice


@dataclass
class Score:
    attribute: str = ""
    score: int = 0
    modifier: int = field(init=False)
    bonus: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.attribute in self.bonus:
            self.score += self.bonus[self.attribute]
            if self.score > 20:
                self.score = 20
        self.modifier = get_modifier(self.score)


class Attributes:
    def __init__(self, attributes: Dict[str, Dict[str, int]]) -> None:
        self.attributes = attributes

    @staticmethod
    def _can_adjust(base_value: int, bonus_value: int) -> bool:
        if (base_value + bonus_value) > 20:
            return False
        return True

    def add(self, attribute: str, bonus: int) -> None:
        old_value = self.attributes[attribute]["score"]
        if not self._can_adjust(old_value, bonus):
            return
        new_value = old_value + bonus
        self.attributes[attribute]["score"] = new_value
        self.attributes[attribute]["modifier"] = get_modifier(new_value)


def generate_attributes(threshold: int) -> List[int]:
    """Generates the six attributes.

    Continuously rerolls attributes if one of the following is true:

    1. attributes total less than the specified threshold
    2. or smallest attribute < 8
    3. or largest attribute < 15
    """
    while True:
        dice_rolls = [sum(dice.roll("4d6^3")) for _ in range(6)]
        if sum(dice_rolls) < threshold:
            continue
        if min(dice_rolls) < 8:
            continue
        if max(dice_rolls) < 15:
            continue
        break
    return dice_rolls


def get_modifier(score: int) -> int:
    """Returns the modifier by calculation of the specified score."""
    return floor((score - 10) / 2)
