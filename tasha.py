from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Dict, List, Literal, Union

import toml

from actor import CharacterSheet, PlayerCharacter
from attributes import Attributes, Score, generate_attributes, get_modifier
from d20 import SystemResourceDocument
import utils

oSheet = CharacterSheet()
oPC = PlayerCharacter(oSheet)
oSRD = SystemResourceDocument()


character_dir = Path.home() / ".config" / "tasha" / "characters"
if not character_dir.exists():
    character_dir.mkdir(parents=True)
    print(f"creating character directory.")


"""
def assignAttributeValues(results: List[int]) -> Dict[str, Dict[str, int]]:"
    attribute_options = [
        "Strength",
        "Dexterity",
        "Constitution",
        "Intelligence",
        "Wisdom",
        "Charisma",
    ]
    attribute_array = dict()
    results.sort(reverse=True)

    def setAttributeOrder(array: Dict[str, Any]) -> Dict[str, Any]:
        attribute_order = (
            "Strength",
            "Dexterity",
            "Constitution",
            "Intelligence",
            "Wisdom",
            "Charisma",
        )
        ordered_attributes = dict()
        for entry_key in attribute_order:
            ordered_attributes[entry_key] = array[entry_key]
        return ordered_attributes

    def setAttributeValue(attribute_name: str, attribute_value: int) -> None:
        attribute_options.remove(attribute_name)
        results.remove(attribute_value)
        attr_values = asdict(Score(attribute_name, attribute_value))
        del attr_values["attribute"]
        del attr_values["bonus"]
        attribute_array[attribute_name] = attr_values

    for _ in range(6):
        if len(results) == 1:
            setAttributeValue(attribute_options[0], results[0])
            break

        attribute = Scan(
            message="Assign {} ({}) to which attribute?".format(
                results[0], ", ".join([str(d) for d in results])
            ),
            selections=attribute_options,
            completer=True,
        )
        setAttributeValue(attribute, results[0])

    return setAttributeOrder(attribute_array)
"""


def step1():
    # Choose class/subclass
    # Select level
    klass = utils.stdin("Choose a class.", oSRD.getClasses())[0]
    level = int(utils.stdin("What is your character's class level?", 20)[0])
    subclass = ""
    if level >= 3:
        subklass = utils.stdin(
            "If you start at level 3 or higher, choose a subclass.",
            oSRD.getSubclassesByClass(klass),
        )
        subclass = subklass[0]
    oSheet.set("armors", oSRD.getArmorProficienciesByClass(klass))
    oSheet.set("classes", {klass: {"level": level, "subclass": subclass}})


def step2():
    # Choose a background
    # Choose a species
    # Choose equipment
    background = utils.stdin(
        "Choose your character's background.", oSRD.getBackgrounds()
    )
    oSheet.set("background", background[0])

    # Choose ability bonuses
    ability_bonus_array = utils.stdin(
        "A background lists three of your character's ability scores. Increase "
        "one by 2 and another one by 1, or increase all three by 1. None of "
        "these increases can raise a score above 20.",
        ["Apply 2/1", "Apply 1/1/1"],
    )
    bonus_array = {
        "Strength": 0,
        "Dexterity": 0,
        "Constitution": 0,
        "Intelligence": 0,
        "Wisdom": 0,
        "Charisma": 0,
    }
    if ability_bonus_array[0] == "Apply 2/1":
        background_abilities = oSRD.getAbilityByBackground(oPC.getMyBackground())

        two_point_ability = utils.stdin(
            "Choose which ability to apply a 2 point bonus.", background_abilities
        )
        chosen_ability = two_point_ability[0]
        bonus_array[chosen_ability] = 2

        one_point_ability = utils.stdin(
            "Choose which ability to apply a 1 point bonus.", background_abilities
        )
        chosen_ability = one_point_ability[0]
        bonus_array[chosen_ability] = 1

    if ability_bonus_array[0] == "Apply 1/1/1":
        for ability in oSRD.getAbilityByBackground(oPC.getMyBackground()):
            bonus_array[ability] = 1

    oSheet.set("bonus", bonus_array)

    feat = utils.stdin(
        "A background gives your character a specified Origin feat.",
        oSRD.getFeatsByCategory("Origin"),
    )
    oSheet.set("feats", feat)

    skills = utils.stdin(
        "A background gives your character proficiency in two specified skills.",
        oSRD.getSkillsByBackground(oPC.getMyBackground()),
        loop_count=2,
    )
    oSheet.set("skills", skills)

    tool = utils.stdin(
        "Each background gives a character proficiency with one tool-either a "
        "specific tool or one chosen from the Artisan's Tools category.",
        oSRD.getToolsByBackground(oPC.getMyBackground()),
    )
    oSheet.set("tools", tool)

    species = utils.stdin("Choose a species for your character.", oSRD.getSpecies())[0]
    oSheet.set(
        {
            "size": oSRD.getSizeBySpecies(species),
            "species": species,
            "speed": oSRD.getSpeedBySpecies(species),
            "traits": oSRD.getTraitsBySpecies(species),
        }
    )

    languages = utils.stdin(
        "Your character knows at least three languages: Common plus two languages.",
        oSRD.getStandardLanguages(),
        loop_count=2,
    )
    oSheet.set("languages", ["Common"] + languages)


def step3():
    # Generate/Assign ability scores
    pass


def step4():
    # Choose an alignment
    alignment = utils.stdin("Choose your alignment.", oSRD.getAlignments())[0]
    oSheet.set("alignment", alignment)


def step5():
    klass = oPC.getMyClasses()[0]
    oSheet.set(
        {
            "savingthrows": oSRD.getSavingThrowsByClass(klass),
            "features": oSRD.getFeaturesByClass(klass, oPC.getClassLevel(klass)),
        }
    )
    gender = utils.stdin("What is your gender?", ["Female", "Male"])[0]
    oSheet.set("gender", gender)


def main() -> None:
    try:
        step1()
        step2()
        step3()
        step4()
        step5()

        print(oSheet)
    except KeyboardInterrupt:
        print()
        pass


if __name__ == "__main__":
    main()
