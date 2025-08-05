from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.progress import track
from rich.prompt import Confirm, IntPrompt
from rich.table import Table
from rich.theme import Theme
import toml

from tasha.actor import PlayerCharacter
from tasha.d20 import SystemResourceDocument
from tasha.stylesheet import css

console = Console(
    style="default",
    tab_size=4,
    theme=Theme(css),
    width=80,
)
oPC = PlayerCharacter()
oSRD = SystemResourceDocument()


def assign_ability_scores() -> dict[str, dict[str, int]]:
    """Prompt to assign the character's ability scores.

    Returns:
        dict[str, dict[str, int]]: Returns dict of abilities."""
    ability_score_array = {
        "Strength": {"score": 0, "modifier": 0},
        "Dexterity": {"score": 0, "modifier": 0},
        "Constitution": {"score": 0, "modifier": 0},
        "Intelligence": {"score": 0, "modifier": 0},
        "Wisdom": {"score": 0, "modifier": 0},
        "Charisma": {"score": 0, "modifier": 0},
    }

    # Apply background ability bonuses.
    for ability, bonus in oPC.getMyBonus().items():
        if bonus > 0:
            new_score = ability_score_array[ability]["score"] + bonus
            ability_score_array[ability] = {
                "score": new_score,
                "modifier": calculate_modifier(new_score),
            }

    return ability_score_array


def assign_prepared_spells(klass: str) -> None:
    """Prompt to choose your character's prepared spells.

    Args:
        klass (str): Name of the class to choose spells for.

    Returns:
        None."""
    if not oPC.isSpellcastingClass(klass):
        return

    spellcaster_level = oPC.getSpellcastingLevel(klass)
    oPC.set(
        {
            "cantrips": {klass: oSRD.getCantripsKnownByClass(klass, spellcaster_level)},
            "spell_slots": oSRD.getSpellslotsByClass(klass, spellcaster_level),
        }
    )

    number_of_prepared_spells = oSRD.getPreparedSpellCountByClass(
        klass, oPC.getLevelByClass(klass)
    )
    if number_of_prepared_spells == 0:
        return

    console.print(f"You can select ({number_of_prepared_spells}) prepared spells.")
    prepared_spells = list()
    spell_level_options = [str(l + 1) for l, _ in enumerate(oPC.getMySpellslots())]
    while len(prepared_spells) < number_of_prepared_spells:
        spell_level = IntPrompt.ask(
            "Choose a level to select spells from.",
            choices=spell_level_options,
            console=console,
        )
        console.print(f"Choose a level {spell_level} spell.")
        chosen_spell = menu(oSRD.getSpellsByLevel(spell_level, klass)[spell_level])[0]
        console.print(f":book: You learned the spell {chosen_spell}.")
        prepared_spells.append(chosen_spell)

    oPC.set("prepared_spells", {klass: prepared_spells})


def assign_subclass(klass: str, level: int) -> str:
    """Prompt to choose a primary/secondary class subclass.

    Args:
        klass (str): Name of the class to choose a subclass for.
        level (int): Level of the class to determine subclass eligibility.

    Returns:
        str: The selected subclass."""
    if level < 3:
        return ""

    return menu(
        oSRD.getSubclassesByClass(klass),
    )[0]


def calculate_modifier(score: int) -> int:
    """Calculates the modifier of the specified score.

    Args:
        score (int): Score to calculate the modifier for.

    Returns:
        int: Returns the calculated modifier of the specified score."""
    from math import floor

    return floor((score - 10) / 2)


def generate_scores() -> list[int]:
    """Randomly generates six scores.

    Continuously rerolls if one of the following is true:

        1. smallest score < 8
        2. or largest score < 15
        
    Returns:
        list[int]: Returns a list of six integers."""
    import dice  # pyright: ignore

    while True:
        dice_rolls = [sum(dice.roll("4d6^3")) for _ in range(6)]  # pyright: ignore
        if min(dice_rolls) >= 8 and max(dice_rolls) >= 15:
            break

    dice_rolls.sort(reverse=True)
    return dice_rolls


def get_allowed_feats() -> list[str]:
    """Returns a list of selectable feats.

    1. feats the character doesn't already have
    2. and feats the character meets the requirements for

    Returns:
        list[str]: List of all relevant feats."""
    return [f for f in oSRD.getFeats() if has_requirements(f)]


def get_allowed_multiclasses() -> list[str]:
    """Retrieves a list of valid multiclassing options.

    Returns:
        list[str]: Returns a list of allowable character multiclasses."""
    multiclasses = []

    # If the primary class ability score(s) are under 13.
    if not oSRD.hasAbilityRequirementsByClass(oPC.getMyClasses()[0], oPC.attributes):
        return multiclasses

    # if the secondary class abiity score(s) are under 13
    for klass in oSRD.getClasses():
        if klass not in oPC.getMyClasses() and oSRD.hasAbilityRequirementsByClass(
            klass, oPC.attributes
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
        features_check = False
        for feature in features_requirements:
            if feature in oPC.getMyFeatures():
                features_check = True
                break

        if not features_check:
            return features_check

    if oPC.getTotalLevel() < oSRD.getLevelRequirementByFeat(feat):
        return False

    return True


def menu(choices: list[str] | int, loop_count: int = 1) -> list[str]:
    """Captures user input from the console.

    Args:
        choices (List[str]|int): List of choices or max value in a range of numbers.
        loop_count (int): Number of times to prompt the user. Default 1 prompt.

    Returns:
        list[str]: A list of the user's responses."""

    def first_and_last(choices: dict[int, Any]) -> tuple[int, int]:
        indexes = list(choices.keys())
        return (indexes[0], indexes[-1])

    def index_choices(choices: list[Any]) -> dict[int, Any]:
        indexed_choices = {}
        for index, option in enumerate(choices):  # pyright: ignore
            indexed_choices[index + 1] = option
        return indexed_choices

    # If using numbers, create a range, starting from 1.
    if isinstance(choices, int):
        choices = list(str(n + 1) for n in range(choices))

    selections = []
    for _ in range(0, loop_count):
        indexed_choices = index_choices(choices)

        # Automatically select the last option.
        if len(indexed_choices) == loop_count:
            return list(indexed_choices.values())

        first_index, last_index = first_and_last(indexed_choices)
        message = (
            f"\n[prompt]Make a selection <{first_index}-{last_index}>.[/prompt]\n\n"
        )
        for index, option in indexed_choices.items():
            message += f"\t{index}.) [prompt.choices]{option}[/prompt.choices]\n"
        console.print(message)

        try:
            user_input = int(input(">> "))
            chosen_option = indexed_choices[user_input]
            # Hax to keep the 'Ability Score Improvement' feat selectable.
            if chosen_option != "Ability Score Improvement":
                selections.append(chosen_option)
                choices.remove(chosen_option)
        except (KeyError, TypeError, ValueError):
            return menu(choices)

    return selections


def set_class_features(
    klass: str, primary_class: bool, level: int, subclass: str = ""
) -> None:
    """Applies primary/secondary class features.

    Args:
        klass (str): Name of the class to apply class features for.
        primary_class (bool): Determines if primary class or not.
        level (int): Level of the class to apply class features for.
        subclass (str): Name of the class' subclass.

    Returns:
        None."""
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

    # Handle class tool proficiency allocations.
    if klass == "Bard":
        console.print("Choose your bardic musical instrument tool proficiencies.")
        oPC.set(
            "tools",
            menu(
                oSRD.getToolProficienciesByClass(klass, oPC.getMyToolProficiencies()),
                loop_count=3 if primary_class else 1,
            ),
        )
    elif primary_class and klass == "Monk":
        console.print("Choose your monk artisan/musical instrument tool proficiency.")
        oPC.set(
            "tools",
            menu(
                oSRD.getToolProficienciesByClass(klass, oPC.getMyToolProficiencies()),
            ),
        )
    else:
        oPC.set("tools", oSRD.getToolProficienciesByClass(klass))

    # Set class features
    oPC.set(
        {
            "features": {
                klass: oSRD.getFeaturesByClass(klass, oPC.getLevelByClass(klass))
            },
        }
    )


def set_class_skills(klass: str, primary_class: bool) -> None:
    """Applies primary/secondary class skills.

    Args:
        klass (str): Name of the class to apply class skills for.
        primary_class (bool): Determines if the class is the primary class.

    Returns:
        None."""
    if klass == "Rogue":
        allotted_skills = 4
    elif klass in ("Bard", "Ranger"):
        allotted_skills = 1 if not primary_class else 3
    else:
        allotted_skills = 0 if not primary_class else 2

    oPC.set(
        "skills",
        menu(oSRD.getSkillsByClass(klass, oPC.getMySkills()), loop_count=allotted_skills),
    )


def main(name: str) -> None:
    # Register the character's name
    oPC.set("name", name.strip())

    # Choose class/subclass
    # Select level
    console.print("Choose a primary class.")
    first_class = menu(oSRD.getClasses())[0]

    console.print(f"What is your primary class' {first_class} level?")
    level = int(menu(20)[0])
    if level >= 3:
        console.print(
            f"If you start at level 3 or higher, choose a {first_class} subclass."
        )

    subclass = assign_subclass(first_class, level)
    set_class_features(first_class, True, level, subclass)

    console.print(f"Choose your primary class' {first_class} skill(s).")
    set_class_skills(first_class, True)

    # Choose a background
    # Choose a species
    # Choose equipment
    console.print("Choose your character's background.")
    oPC.set("background", menu(oSRD.getBackgrounds())[0])

    # Choose ability bonuses
    console.print(
        "A background provides a bonus to up to three of your character's "
        "ability scores. Increase one ability by 2 and another ability by 1, "
        "or increase all abilities by 1. No score can be raised above 20.",
    )
    ability_bonus_array = {
        "Strength": 0,
        "Dexterity": 0,
        "Constitution": 0,
        "Intelligence": 0,
        "Wisdom": 0,
        "Charisma": 0,
    }
    array_selection = menu(
        ["Apply 2/1", "Apply 1/1/1"],
    )[0]
    if array_selection == "Apply 2/1":
        background_abilities = oSRD.getAbilitiesByBackground(oPC.getMyBackground())

        console.print("Choose which ability score to apply a 2 point bonus.")
        two_point_ability = menu(background_abilities)[0]
        ability_bonus_array[two_point_ability] = 2

        console.print("Choose which ability score to apply a 1 point bonus.")
        one_point_ability = menu(background_abilities)[0]
        ability_bonus_array[one_point_ability] = 1

    if array_selection == "Apply 1/1/1":
        for ability in oSRD.getAbilitiesByBackground(oPC.getMyBackground()):
            ability_bonus_array[ability] = 1

    oPC.set("bonus", ability_bonus_array)

    console.print("A background gives your character a specified Origin feat.")
    oPC.set("feats", menu(oSRD.getFeatsByCategory("Origin")))

    console.print(
        "A background gives your character proficiency in two specified skills."
    )
    background_skills = []
    # Loop through background skills.
    for skill in oSRD.getSkillsByBackground(oPC.getMyBackground()):
        # If the skill is not known, add to the filtered background skill list.
        if skill not in oPC.getMySkills():
            background_skills.append(skill)

    skills = menu(
        background_skills,
        loop_count=len(background_skills),
    )

    for skill in background_skills:
        console.print(f":book: You learned the skill {skill} from your background.")

    oPC.set("skills", skills)

    console.print(
        "Each background gives a character proficiency with one tool-either a "
        "specific tool or one chosen from the Artisan's Tools category."
    )
    tool = menu(
        oSRD.getToolProficienciesByBackground(oPC.getMyBackground()),
    )
    oPC.set("tools", tool)

    console.print("Choose a species for your character.")
    species = menu(oSRD.getSpecies())[0]
    oPC.set(
        {
            "size": oSRD.getSizeBySpecies(species),
            "species": species,
            "speed": oSRD.getSpeedBySpecies(species),
            "traits": oSRD.getTraitsBySpecies(species),
        }
    )

    console.print("You know at least three languages: Common plus two languages.")
    languages = menu(
        oSRD.getStandardLanguages(),
        loop_count=2,
    )
    oPC.set("languages", ["Common"] + languages)

    # Generate/Assign attributes
    attributes_array = {}
    while len(attributes_array) == 0:
        attributes_array = assign_ability_scores()
        ability_score_names = list(attributes_array.keys())
        for score in generate_scores():
            console.print(f"Assign an {score} to which ability?")
            ability_selection = menu(ability_score_names)[0]
            score = score + attributes_array[ability_selection]["score"]
            attributes_array[ability_selection] = {
                "score": score,
                "modifier": calculate_modifier(score),
            }

        table = Table(
            title="Generated Ability Scores", caption="*Background bonuses applied"
        )
        table.add_column("")
        table.add_column("Score", justify="center")
        table.add_column("Modifier", justify="center")
        for attribute_name, attribute_pair in attributes_array.items():
            score, modifier = tuple(attribute_pair.values())
            table.add_row(attribute_name, str(score), str(modifier))

        console.print("\n")
        console.print(table)
        console.print("\n")

        if not Confirm.ask(
            "Are you satisfied with these ability scores?", console=console
        ):
            attributes_array = {}

    oPC.set("attributes", attributes_array)

    # Multiclass
    primary_class = oPC.getMyClasses()[0]
    if Confirm.ask("Would you like to multiclass?", console=console):
        console.print("Choose a secondary class.")
        second_class = menu(get_allowed_multiclasses())[0]

        console.print(f"What is your secondary class' {second_class} level?")
        level = int(menu(20)[0])
        if level >= 3:
            console.print(
                f"If you start at level 3 or higher, choose a {second_class} subclass."
            )

        subclass = assign_subclass(second_class, level)
        set_class_features(second_class, False, level, subclass)

        console.print(f"Choose your secondary class' {second_class} skill(s).")
        set_class_skills(second_class, False)

    # Choose an alignment
    console.print("Choose your alignment.")
    oPC.set("alignment", menu(oSRD.getAlignments())[0])

    # Saving Throws
    # Passive Perception
    # Initiative
    # Cantrips
    # Prepared Spells
    # Spell Slots
    console.print("Choose your feats.")
    ability_score_improvements = oSRD.getFeaturesByClass(
        primary_class, oPC.getTotalLevel()
    ).count("Ability Score Improvement")
    oPC.set("feats", menu(get_allowed_feats(), loop_count=ability_score_improvements))

    console.print("What's your gender?")
    oPC.set("gender", menu(["Female", "Male"])[0])

    oPC.set("savingthrows", oSRD.getSavingThrowsByClass(primary_class))

    # Select prepared spells.
    for klass in oPC.getMyClasses():
        assign_prepared_spells(klass)

    # Finalize character save.
    if not Confirm.ask("Save this character?", console=console):
        console.print(
            f":floppy_disk: :red_circle: Character {oPC.getMyName()} save was aborted."
        )
    else:
        character_sheet = replace(
            oPC,
            level=oPC.getTotalLevel(),
        )
        character_dir = Path.cwd()
        for _ in track(range(100), description="Saving..."):
            with Path(character_dir, f"{name.replace(" ", "_")}.toml").open(
                "w"
            ) as record:
                toml.dump(asdict(character_sheet), record)
        console.print(
            f":floppy_disk: :green_circle: Character {oPC.getMyName()} save was successful!"
        )


@click.version_option()
@click.command()
@click.option("--new", help="Generates a new player character.")
def tasha_main(new):
    try:
        main(new)
    except KeyboardInterrupt:
        console.print("\n")
        console.print(":dagger:  [exit]Exited program.[/exit]")
