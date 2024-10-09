from typing import List


def generate_abilities(threshold: int) -> List[int]:
    """Generates the character's six abilities.

    Continuously rerolls attributes if one of the following is true:

    1. attributes total less than the specified threshold
    2. or smallest attribute < 8
    3. or largest attribute < 15
    """
    import dice

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
