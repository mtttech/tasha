from dataclasses import asdict, replace
from math import floor
from pathlib import Path
from typing import Any, Dict, List

import dice  # pyright: ignore
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from rich.progress import track
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.theme import Theme
import toml

from tasha.actor import PlayerCharacter
from tasha.d20 import SystemResourceDocument
from tasha.settings import SettingsLoader
from tasha.themes import ThemeLoader

settings = SettingsLoader()
console = Console(
    tab_size=2,
    theme=Theme(ThemeLoader(settings.default_theme).load()),
    width=80,
)
oPC = PlayerCharacter()
oSRD = SystemResourceDocument()


def apply_class(klass: str, primary_class: bool) -> None:
    """Applies primary/secondary class features.

    Args:
        klass (str): Name of the class to apply class features for.
        primary_class (bool): Attributes to use in the requirements check.

    Returns:
        None."""
    console.print(f"What is your '{klass}' class level?", style="default")
    level = int(io(20)[0])

    subclass = ""
    if level >= 3:
        console.print(
            f"If you start at level 3 or higher, choose a {klass} subclass.",
            style="default",
        )
        subclass = io(
            oSRD.getSubclassesByClass(klass),
        )[0]

    oPC.set(
        {
            "armors": oSRD.getArmorProficienciesByClass(klass, primary_class),
            "classes": {
                klass: {
                    "level": level,
                    "hit_die": oSRD.getHitDieByClass(klass),
                    "subclass": subclass,
                }
            },
            "weapons": oSRD.getWeaponProficienciesByClass(klass, primary_class),
        }
    )

    # Skill allocations.
    skills = oSRD.getSkillsByClass(klass, oPC.getMySkills())
    console.print("Choose a class skill.", style="default")
    if not primary_class:
        if klass == "Rogue":
            allotted_skills = 4
        elif klass in ("Bard", "Ranger"):
            allotted_skills = 1
        oPC.set(
            "skills",
            io(skills, loop_count=allotted_skills),  # pyright: ignore
        )
    else:
        if klass == "Rogue":
            allotted_skills = 4
        elif klass in ("Bard", "Ranger"):
            allotted_skills = 3
        else:
            allotted_skills = 2
        oPC.set(
            "skills",
            io(skills, loop_count=allotted_skills),
        )

    # Handle tool proficiency allocations.
    if klass == "Bard":
        console.print(
            "Choose your bardic musical instrument tool proficiencies.",
            style="default",
        )
        oPC.set(
            "tools",
            io(
                oSRD.getToolProficienciesByClass(klass, oPC.getMyToolProficiencies()),
                loop_count=3 if primary_class else 1,
            ),
        )
    elif primary_class and klass == "Monk":
        console.print(
            "Choose your monk artisan/musical instrument tool proficiency.",
            style="default",
        )
        oPC.set(
            "tools",
            io(
                oSRD.getToolProficienciesByClass(klass, oPC.getMyToolProficiencies()),
            ),
        )
    else:
        oPC.set("tools", oSRD.getToolProficienciesByClass(klass))


def assign_abilities() -> Dict[str, Dict[str, int]]:
    """Prompt to assign a score to each of the six abilities.

    Returns:
        Dict[str, Dict[str, int]]: Returns dict of abilities, scores, modifiers."""
    ability_array = {
        "Strength": {"score": 0, "modifier": 0},
        "Dexterity": {"score": 0, "modifier": 0},
        "Constitution": {"score": 0, "modifier": 0},
        "Intelligence": {"score": 0, "modifier": 0},
        "Wisdom": {"score": 0, "modifier": 0},
        "Charisma": {"score": 0, "modifier": 0},
    }
    results = generate_scores()
    results.sort(reverse=True)
    ability_names = list(ability_array.keys())
    for score in results:
        console.print(f"Assign {score} to which ability?", style="default")
        ability_array[io(ability_names)[0]] = {
            "score": score,
            "modifier": calculate_modifier(score),
        }

    # Apply background ability bonuses.
    for ability, bonus in oPC.getMyBonus().items():
        if bonus > 0:
            old_score = ability_array[ability]["score"]
            new_score = old_score + bonus
            if new_score > 20:
                new_score = 20
            ability_array[ability] = {
                "score": new_score,
                "modifier": calculate_modifier(new_score),
            }

    console.print(
        Panel(
            Pretty(ability_array, expand_all=True),
            title="Generated Ability Scores (Background bonuses applied)",
        )
    )
    if not Confirm.ask("Are you satisfied with these ability scores?", console=console):
        return assign_abilities()

    return ability_array


def calculate_modifier(score: int) -> int:
    """Calculates the modifier of the specified score.

    Args:
        score (int): Score to calculate the modifier for.

    Returns:
        int: Returns the calculated modifier of the specified score."""
    return floor((score - 10) / 2)


def generate_scores() -> List[int]:
    """Randomly generates six values.

    Continuously rerolls if one of the following is true:

    1. smallest score < 8
    2. or largest score < 15

    Returns:
        List[int]: Returns a list of six integers."""
    while True:
        dice_rolls = [sum(dice.roll("4d6^3")) for _ in range(6)]  # pyright: ignore
        if min(dice_rolls) >= 8 and max(dice_rolls) >= 15:
            break

    return dice_rolls


def get_feats() -> List[str]:
    """Returns a list of selectable feats.

    1. feats the character doesn't already have
    2. and feats the character meets the requirements for

    Returns:
        List[str]: List of all relevant feats."""
    return [f for f in oSRD.getFeats() if has_requirements(f)]


def get_multiclasses(
    primary_class: str, attributes: Dict[str, Dict[str, Any]]
) -> List[str]:
    """Retrieves a list of valid multiclassing options.

    Returns:
        List[str]: Returns a list of allowable character multiclasses."""
    multiclasses = list()

    # If the primary class ability score(s) are under 13.
    if not oSRD.hasAbilityRequirementsByClass(primary_class, attributes):
        return multiclasses

    # if the secondary class abiity score(s) are under 13
    for klass in oSRD.getClasses():
        if klass not in oPC.getMyClasses() and oSRD.hasAbilityRequirementsByClass(
            klass, attributes
        ):
            multiclasses.append(klass)

    return multiclasses


def has_requirements(feat: str) -> bool:
    """Determines if a character meets the prerequisites for the specified feat.

    1. feats the character doesn't already have
    2. and feats the character meets the requirements for

    Args:
        feat (str): Name of the feat.

    Returns:
        bool: True if prerequisites met, False otherwise."""
    ability_requirements = oSRD.getAbilityRequirementsByFeat(feat)
    required_abilities = list(ability_requirements.keys())
    if len(required_abilities) > 0:
        ability_chk_success = False
        for ability in required_abilities:
            if oPC.getScoreByAbility(ability) >= ability_requirements[ability]:
                ability_chk_success = True
                break

        if not ability_chk_success:
            return ability_chk_success

    armor_requirements = oSRD.getArmorRequirementsByFeat(feat)
    if len(armor_requirements) > 0:
        for armor in armor_requirements:
            if armor not in oPC.getMyArmorProficiencies():
                return False

    features_requirements = oSRD.getFeatureRequirementsByFeat(feat)
    if len(features_requirements) > 0:
        features_chk_success = False
        for feature in features_requirements:
            if feature in oPC.getMyFeatures():
                features_chk_success = True
                break

        if not features_chk_success:
            return features_chk_success

    if oPC.getTotalLevel() < oSRD.getLevelRequirementByFeat(feat):
        return False

    return True


def io(choices: List[str] | int, loop_count: int = 1) -> List[str]:
    """Captures user input from the console.

    Args:
        choices (List[str]|int): List of choices or max value in a range of numbers.
        loop_count (int): Number of times to prompt the user. Default 1 prompt.

    Returns:
        List[str]: A list of the user's responses."""

    # If using numbers, create a range, starting from 1.
    if isinstance(choices, int):
        choices = list(str(n + 1) for n in range(choices))

    selections = list()
    for _ in range(0, loop_count):
        # Map out menu selections
        indexed_choices = dict()
        for index, option in enumerate(choices):  # pyright: ignore
            indexed_choices[index + 1] = option

        # Automatically select the last option.
        if len(indexed_choices) == loop_count:
            return list(indexed_choices.values())

        indexes = list(indexed_choices.keys())
        first_index = indexes[0]
        last_index = indexes[-1]
        message = f"[prompt]Make a selection {first_index}-{last_index}.[/prompt]\n\n"
        for index, option in indexed_choices.items():
            message += f"\t[menu.index]{index}[/menu.index].) [menu.option]{option}[/menu.option]\n"
        console.print(message)

        user_input = int(input(">> "))
        try:
            chosen_option = indexed_choices[user_input]
            # Hax to keep the 'Ability Score Improvement' feat selectable.
            if chosen_option != "Ability Score Improvement":
                selections.append(chosen_option)
                choices.remove(chosen_option)
        except (KeyError, TypeError, ValueError):
            return io(choices)

    return selections


def main() -> None:
    # Choose class/subclass
    # Select level
    console.print("Choose a primary class.", style="default")
    apply_class(io(oSRD.getClasses())[0], True)

    # Choose a background
    # Choose a species
    # Choose equipment
    console.print("Choose your character's background.", style="default")
    oPC.set("background", io(oSRD.getBackgrounds())[0])

    # Choose ability bonuses
    console.print(
        "A background lists three of your character's ability scores. Increase "
        "one by 2 and another one by 1, or increase all three by 1. None of "
        "these increases can raise a score above 20.",
        style="default",
    )
    ability_bonus_array = {
        "Strength": 0,
        "Dexterity": 0,
        "Constitution": 0,
        "Intelligence": 0,
        "Wisdom": 0,
        "Charisma": 0,
    }
    array_selection = io(
        ["Apply 2/1", "Apply 1/1/1"],
    )[0]
    if array_selection == "Apply 2/1":
        background_abilities = oSRD.getAbilitiesByBackground(oPC.getMyBackground())

        console.print("Choose which ability to apply a 2 point bonus", style="default")
        two_point_ability = io(background_abilities)[0]
        ability_bonus_array[two_point_ability] = 2

        console.print("Choose which ability to apply a 1 point bonus.", style="default")
        one_point_ability = io(background_abilities)[0]
        ability_bonus_array[one_point_ability] = 1

    if array_selection == "Apply 1/1/1":
        for ability in oSRD.getAbilitiesByBackground(oPC.getMyBackground()):
            ability_bonus_array[ability] = 1

    oPC.set("bonus", ability_bonus_array)

    console.print(
        "A background gives your character a specified Origin feat.", style="default"
    )
    oPC.set("feats", io(oSRD.getFeatsByCategory("Origin")))

    console.print(
        "A background gives your character proficiency in two specified skills.",
        style="default",
    )
    background_skills = list()
    for skill in oSRD.getSkillsByBackground(oPC.getMyBackground()):
        if skill not in oPC.getMySkills():
            background_skills.append(skill)
    skills = io(
        background_skills,
        loop_count=len(background_skills),
    )
    oPC.set("skills", skills)

    console.print(
        "Each background gives a character proficiency with one tool-either a "
        "specific tool or one chosen from the Artisan's Tools category.",
        style="default",
    )
    tool = io(
        oSRD.getToolProficienciesByBackground(oPC.getMyBackground()),
    )
    oPC.set("tools", tool)

    console.print("Choose a species for your character.", style="default")
    species = io(oSRD.getSpecies())[0]
    oPC.set(
        {
            "size": oSRD.getSizeBySpecies(species),
            "species": species,
            "speed": oSRD.getSpeedBySpecies(species),
            "traits": oSRD.getTraitsBySpecies(species),
        }
    )

    console.print(
        "Your character knows at least three languages: Common plus two languages.",
        style="default",
    )
    languages = io(
        oSRD.getStandardLanguages(),
        loop_count=2,
    )
    oPC.set("languages", ["Common"] + languages)

    # Generate/Assign ability scores
    oPC.set("attributes", assign_abilities())

    # Multiclass
    klass = oPC.getMyClasses()[0]
    if Confirm.ask("Would you like to multiclass?", console=console):
        console.print("Choose a secondary class.", style="default")
        apply_class(io(get_multiclasses(klass, oPC.getMyAttributes()))[0], False)

    # Choose an alignment
    console.print("Choose your alignment.", style="default")
    oPC.set("alignment", io(oSRD.getAlignments())[0])

    # Saving Throws
    # Passive Perception
    # Hit Point Dice
    # Initiative
    # Cantrips
    # Prepared Spells
    # Spell Slots
    console.print("Choose your feats.", style="default")
    ability_score_improvements = oSRD.getFeaturesByClass(
        klass, oPC.getTotalLevel()
    ).count("Ability Score Improvement")
    oPC.set("feats", io(get_feats(), loop_count=ability_score_improvements))

    console.print("What's your gender?", style="default")
    oPC.set("gender", io(["Female", "Male"])[0])

    oPC.set(
        {
            "cantrips": oSRD.getCantripsKnownByClass(klass, oPC.getTotalLevel()),
            "initiative": oPC.getModifierByAbility("Dexterity"),
            "savingthrows": oSRD.getSavingThrowsByClass(klass),
            "spell_slots": oSRD.getSpellslotsByClass(klass, oPC.getTotalLevel()),
        }
    )

    # Set class features
    for _class in oPC.getMyClasses():
        oPC.set(
            {
                "features": oSRD.getFeaturesByClass(
                    _class, oPC.getLevelByClass(_class)
                ),
            }
        )

    if oPC.isSpellcaster():
        prepared_spells = list()
        prepared_spell_count = oSRD.getPreparedSpellCountByClass(
            klass, oPC.getTotalLevel()
        )
        spell_levels = [str(l + 1) for l, _ in enumerate(oPC.getMySpellslots())]
        while len(prepared_spells) < prepared_spell_count:
            spell_level = IntPrompt.ask(
                f"Choose a spell by level to create your prepared spell list.",
                choices=spell_levels,
                console=console,
            )

            console.print(f"Choose a level {spell_level} spell.", style="default")
            chosen_spell = io(oSRD.getSpellsByLevel(spell_level, klass)[spell_level])[0]
            prepared_spells.append(chosen_spell)

        oPC.set("prepared_spells", {klass: prepared_spells})

    name = Prompt.ask("What is your character's name?", console=console).strip()
    oPC.set("name", name)

    character_sheet = replace(
        oPC,
        level=oPC.getTotalLevel(),
    )
    console.print(
        Panel(
            Pretty(character_sheet, expand_all=True),
            title=f"{oPC.getMyName()}'s Character Sheet",
        )
    )

    if not Confirm.ask("Save this character?", console=console):
        console.print(f"Save aborted for '{oPC.getMyName()}'.", style="exit")
    else:
        character_dir = Path.home() / ".config" / "tasha" / "characters"
        for _ in track(range(100), description="Saving..."):
            with Path(character_dir, f"{name.replace(" ", "_")}.toml").open(
                "w"
            ) as record:
                toml.dump(asdict(character_sheet), record)
        console.print(f"Character '{oPC.getMyName()}' saved!", style="default")


def tasha_main() -> None:
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        console.print("Exited program.", style="exit")


if __name__ == "__main__":
    tasha_main()
