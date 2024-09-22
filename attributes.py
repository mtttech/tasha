from dataclasses import dataclass, field
from typing import List

import dice


@dataclass
class Score:
    attribute: str = ""
    score: int = 0
    bonus: dict = field(default_factory=dict)
    modifier: int = field(init=False)

    def __post_init__(self) -> None:
        if self.attribute in self.bonus:
            self.score += self.bonus[self.attribute]
            if self.score > 20:
                self.score = 20
        self.modifier = get_modifier(self.score)


@dataclass
class Attributes:
    attributes: dict = field(default_factory=dict)

    def add(self, attribute: str, bonus: int) -> None:
        """Applies bonus to the specified attribute."""
        old_value = self.attributes[attribute]["score"]
        if (old_value + bonus) > 20:
            new_value = 20
        else:
            new_value = old_value + bonus
        self.attributes[attribute]["score"] = new_value
        self.attributes[attribute]["modifier"] = get_modifier(new_value)


def generate_attributes(threshold: int) -> List[int]:
    """Generates the character's six attributes.

    Continuously rerolls attributes if one of the following is true:

    1. attributes total less than the specified threshold
    2. or smallest attribute < 8
    3. or largest attribute < 15
    """
    while True:
        dice_rolls = [
            sum(
                dice.roll(
                    "4d6^3"
                )  # pyright: ignore[reportArgumentType, reportCallIssue]
            )
            for _ in range(6)
        ]
        if sum(dice_rolls) < threshold:
            continue
        if min(dice_rolls) < 8:
            continue
        if max(dice_rolls) < 15:
            continue
        break
    return dice_rolls


def get_modifier(score: int) -> int:
    """Calculates the modifier for the specified score."""
    from math import floor

    return floor((score - 10) / 2)
