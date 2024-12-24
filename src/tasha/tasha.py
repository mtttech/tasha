from dataclasses import asdict, replace
from math import floor
from pathlib import Path
from typing import Dict, List

import dice  # pyright: ignore
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from rich.progress import track
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.theme import Theme
import toml

from tasha.actor import CharacterSheet, PlayerCharacter
from tasha.d20 import SystemResourceDocument
from tasha.settings import SettingsLoader
from tasha.themes import ThemeLoader

settings = SettingsLoader()
console = Console(
    tab_size=2,
    theme=Theme(ThemeLoader(settings.default_theme).load()),
    width=80,
)
oSheet = CharacterSheet()
oPC = PlayerCharacter(oSheet)
oSRD = SystemResourceDocument()


def calculate_modifier(score: int) -> int:
    """Calculates the modifier value of the specified score.

    Args:
        score (int): Score to calculate the modifier for.

    Returns:
        int: Returns result of the modifier calculation."""
    return floor((score - 10) / 2)


def generate_scores() -> List[int]:
    """Randomly generates six values.

    Continuously rerolls if one of the following is true:

    1. smallest attribute < 8
    2. or largest attribute < 15

    Returns:
        List[int]: Returns a list of six integers."""
    while True:
        dice_rolls = [sum(dice.roll("4d6^3")) for _ in range(6)]  # pyright: ignore
        if min(dice_rolls) >= 8 and max(dice_rolls) >= 15:
            break

    return dice_rolls


def get_selectable_feats() -> List[str]:
    """Returns a list of selectable feats.

    Returns:
        List[str]: List of all relevant feats."""
    return [f for f in oSRD.getFeats() if has_feat_requirements(f)]


def has_feat_requirements(feat: str) -> bool:
    """Checks if character meets prerequisites for a feat.

    Args:
        feat (str): Name of the feat.

    Returns:
        bool: True if prerequisites met, False otherwise."""
    ability_requirements = oSRD.getAbilityRequirementsByFeat(feat)
    required_abilities = list(ability_requirements.keys())
    if len(required_abilities) > 0:
        ability_chk_success = False
        for ability in required_abilities:
            if oPC.getAttributeScore(ability) >= ability_requirements[ability]:
                ability_chk_success = True
                break

        if not ability_chk_success:
            return ability_chk_success

    armor_requirements = oSRD.getArmorProficiencyRequirementByFeat(feat)
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


def stdin(choices: List[str] | int, loop_count=1) -> List[str]:
    """Captures user input from the console.

    Args:
        choices (List[str]|int): List of choices or max value in a range of numbers.

    Returns:
        List[str]: A list of the user's responses."""

    def associate_choice_indexes() -> Dict[int, str]:
        """Assign an index to each choice."""
        indexed_options = dict()
        for index, option in enumerate(choices):  # pyright: ignore
            indexed_options[index + 1] = option
        return indexed_options

    if isinstance(choices, int):
        choices = list(str(n + 1) for n in range(choices))

    selections = list()
    for _ in range(0, loop_count):
        expanded_options = associate_choice_indexes()
        if len(expanded_options) == loop_count:
            return list(expanded_options.values())

        option_keys = list(expanded_options.keys())
        first_option_index = option_keys[0]
        last_option_index = option_keys[-1]

        message = f"[prompt]Make a selection {first_option_index}-{last_option_index}.[/prompt]\n\n"
        for index, option in expanded_options.items():
            message += f"\t[menu.index]{index}[/menu.index].) [menu.option]{option}[/menu.option]\n"
        console.print(message)

        user_input = input(">> ")
        import time

        time.sleep(1.0)

        try:
            chosen_option = expanded_options[int(user_input)]
            # Hax to keep the 'Ability Score Improvement' feat selectable multiple times.
            if chosen_option != "Ability Score Improvement":
                selections.append(chosen_option)
                choices.remove(chosen_option)
        except (KeyError, TypeError, ValueError):
            return stdin(choices)

    return selections


def step1() -> None:
    # Choose class/subclass
    # Select level
    console.print("Choose a class.", style="default")
    klass = stdin(oSRD.getClasses())[0]
    oSheet.set(
        {
            "armors": oSRD.getArmorProficienciesByClass(klass),
            "weapons": oSRD.getWeaponProficienciesByClass(klass),
        }
    )
    console.print("What is your class level?", style="default")
    level = int(stdin(20)[0])
    subclass = ""
    if level >= 3:
        console.print(
            "If you start at level 3 or higher, choose a subclass.", style="default"
        )
        subklass = stdin(
            oSRD.getSubclassesByClass(klass),
        )
        subclass = subklass[0]
    oSheet.set(
        "classes",
        {
            klass: {
                "level": level,
                "hit_die": oSRD.getHitDieByClass(klass),
                "subclass": subclass,
            }
        },
    )


def step2() -> None:
    # Choose a background
    # Choose a species
    # Choose equipment
    console.print("Choose your character's background.", style="default")
    oSheet.set("background", stdin(oSRD.getBackgrounds())[0])

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
    array_selection = stdin(
        ["Apply 2/1", "Apply 1/1/1"],
    )[0]
    if array_selection == "Apply 2/1":
        background_abilities = oSRD.getBackgroundAbilityScores(oPC.getMyBackground())

        console.print("Choose which ability to apply a 2 point bonus", style="default")
        two_point_ability = stdin(background_abilities)[0]
        ability_bonus_array[two_point_ability] = 2

        console.print("Choose which ability to apply a 1 point bonus.", style="default")
        one_point_ability = stdin(background_abilities)[0]
        ability_bonus_array[one_point_ability] = 1

    if array_selection == "Apply 1/1/1":
        for ability in oSRD.getBackgroundAbilityScores(oPC.getMyBackground()):
            ability_bonus_array[ability] = 1

    oSheet.set("bonus", ability_bonus_array)

    console.print(
        "A background gives your character a specified Origin feat.", style="default"
    )
    oSheet.set("feats", stdin(oSRD.getFeatsByCategory("Origin")))

    console.print(
        "A background gives your character proficiency in two specified skills.",
        style="default",
    )
    skills = stdin(
        oSRD.getBackgroundSkills(oPC.getMyBackground()),
        loop_count=2,
    )
    oSheet.set("skills", skills)

    console.print(
        "Each background gives a character proficiency with one tool-either a "
        "specific tool or one chosen from the Artisan's Tools category.",
        style="default",
    )
    tool = stdin(
        oSRD.getBackgroundToolProficiencies(oPC.getMyBackground()),
    )
    oSheet.set("tools", tool)

    console.print("Choose a species for your character.", style="default")
    species = stdin(oSRD.getSpecies())[0]
    oSheet.set(
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
    languages = stdin(
        oSRD.getStandardLanguages(),
        loop_count=2,
    )
    oSheet.set("languages", ["Common"] + languages)


def step3() -> None:
    # Generate/Assign ability scores
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
        ability_array[stdin(ability_names)[0]] = {
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
        step3()

    oSheet.set("attributes", ability_array)


def step4() -> None:
    # Choose an alignment
    console.print("Choose your alignment.", style="default")
    oSheet.set("alignment", stdin(oSRD.getAlignments())[0])


def step5() -> None:
    # Saving Throws
    # Skills
    # Passive Perception
    # Hit Point Dice
    # Initiative
    # Cantrips
    # Prepared Spells
    # Spell Slots
    klass = oPC.getMyClasses()[0]
    skills = oSRD.getClassSkills(klass, oPC.getMySkills())
    console.print("Choose a class skill.", style="default")
    if klass == "Rogue":
        allotted_skills = 4
    elif klass in ("Bard", "Ranger"):
        allotted_skills = 3
    else:
        allotted_skills = 2
    oSheet.set(
        "skills",
        stdin(skills, loop_count=allotted_skills),
    )

    console.print("Choose your feats.", style="default")
    ability_score_improvements = oSRD.getClassFeatures(
        klass, oPC.getTotalLevel()
    ).count("Ability Score Improvement")
    oSheet.set(
        "feats", stdin(get_selectable_feats(), loop_count=ability_score_improvements)
    )

    console.print("What's your gender?", style="default")
    oSheet.set("gender", stdin(["Female", "Male"])[0])

    oSheet.set(
        {
            "cantrips": oSRD.getCantripsKnownByClass(klass, oPC.getTotalLevel()),
            "features": oSRD.getClassFeatures(klass, oPC.getClassLevel(klass)),
            "hit_die": oSRD.getHitDieByClass(klass),
            "initiative": oPC.getAttributeModifier("Dexterity"),
            "savingthrows": oSRD.getSavingThrowsByClass(klass),
            "spell_slots": oSRD.getClassSpellSlots(klass, oPC.getTotalLevel()),
        }
    )

    if klass == "Bard":
        console.print(
            "Choose your bardic musical instrument tool proficiencies.", style="default"
        )
        oSheet.set(
            "tools",
            stdin(
                oSRD.getToolProficienciesByClass(klass, oPC.getMyToolProficiencies()),
                loop_count=3,
            ),
        )
    elif klass == "Monk":
        console.print(
            "Choose your monk artisan/musical instrument tool proficiency.",
            style="default",
        )
        oSheet.set(
            "tools",
            stdin(
                oSRD.getToolProficienciesByClass(klass, oPC.getMyToolProficiencies()),
            ),
        )
    else:
        oSheet.set("tools", oSRD.getToolProficienciesByClass(klass))

    if oPC.isSpellcaster():
        prepared_spells = list()
        prepared_spell_count = oSRD.getPreparedSpellCountByClass(
            klass, oPC.getTotalLevel()
        )
        spell_levels = [str(l + 1) for l, _ in enumerate(oPC.getMySpellSlots())]
        while len(prepared_spells) < prepared_spell_count:
            spell_level = IntPrompt.ask(
                f"Choose a spell by level to create your prepared spell list.",
                choices=spell_levels,
                console=console,
            )

            console.print(f"Choose a level {spell_level} spell.", style="default")
            chosen_spell = stdin(
                oSRD.getSpellListByClass(klass, spell_level)[spell_level]
            )[0]
            prepared_spells.append(chosen_spell)

        oSheet.set("prepared_spells", {klass: prepared_spells})


def tasha_main() -> None:
    try:
        step1()
        step2()
        step3()
        step4()
        step5()

        name = Prompt.ask("What is your character's name?", console=console).strip()
        oSheet.set("name", name)

        character_sheet = replace(
            oSheet,
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
    except KeyboardInterrupt:
        print("\n")
        console.print("Exited program.", style="exit")


if __name__ == "__main__":
    tasha_main()
