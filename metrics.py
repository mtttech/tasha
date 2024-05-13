from typing import Tuple


class Anthropometry:
    def __init__(
        self, base_metrics: Tuple[str, str], gender: str, dominant_gender: str
    ) -> None:
        self.base_metrics = base_metrics
        self.gender = gender
        self.dominant_gender = dominant_gender

    def calculate(self) -> Tuple[int, int]:
        """Using the race or subrace, calculates a character's height/weight."""
        import math
        import random

        import dice

        height_values, weight_values = self.base_metrics
        # Height formula = base + modifier result
        height_pair = height_values.split(",")
        height_base = int(height_pair[0])
        height_modifier = sum(dice.roll(height_pair[1]))
        height_calculation = height_base + height_modifier
        # Weight formula = height modifier * weight modifier + base
        weight_pair = weight_values.split(",")
        weight_base = int(weight_pair[0])
        weight_modifier = sum(dice.roll(weight_pair[1]))
        weight_calculation = (weight_modifier * height_modifier) + weight_base
        # "Unofficial" rule for height/weight differential by gender
        if self.dominant_gender != "" and self.dominant_gender != self.gender:
            # Subtract 0-5 inches from height.
            height_calculation -= random.randint(0, 5)
            # Subtract 15-20% lbs from weight.
            weight_diff = random.randint(15, 20) / 100
            weight_diff = math.floor(weight_calculation * weight_diff)
            weight_calculation -= weight_diff
        return height_calculation, weight_calculation
