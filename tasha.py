from dataclasses import asdict, replace
from pathlib import Path
from typing import Literal, Union

import toml

from actor import CharacterSheet, PlayerCharacter
from attributes import generate_abilities, get_modifier
from d20 import SystemResourceDocument
from utils import stdin

oSheet = CharacterSheet()
oPC = PlayerCharacter(oSheet)
oSRD = SystemResourceDocument()

character_dir = Path.home() / ".config" / "tasha" / "characters"
if not character_dir.exists():
    character_dir.mkdir(parents=True)
    print("Created the character save directory.")


def hasFeatRequirements(feat: str) -> Union[Literal[False], Literal[True]]:
    """Returns True if character meets feat prerequisites."""
    if feat in oPC.getMyFeats():
        return False

    raw_ability_requirements = oSRD.getAbilityRequirementsByFeat(feat)
    required_abilities = list(raw_ability_requirements.keys())
    ability_chk_success = False
    for ability in required_abilities:
        if oPC.getAttributeScore(ability) >= raw_ability_requirements[ability]:
            ability_chk_success = True
            break

    if not ability_chk_success:
        return False

    armor_requirements = oSRD.getArmorProficiencyRequirementByFeat(feat)
    for armor in armor_requirements:
        if armor not in oPC.getMyArmorProficiencies():
            return False

    features_requirements = oSRD.getFeatureRequirementsByFeat(feat)
    features_chk_success = False
    for feature in features_requirements:
        if feature in oPC.getMyArmorProficiencies():
            features_chk_success = True
            break

    if not features_chk_success:
        return False

    if oPC.getTotalLevel() < oSRD.getLevelRequirementByFeat(feat):
        return False

    return True


def step1() -> None:
    # Choose class/subclass
    # Select level
    klass = stdin("Choose a class.", oSRD.getClasses())[0]
    level = int(stdin("What is your character's class level?", 20)[0])
    subclass = ""
    if level >= 3:
        subklass = stdin(
            "If you start at level 3 or higher, choose a subclass.",
            oSRD.getSubclassesByClass(klass),
        )
        subclass = subklass[0]
    oSheet.set(
        {
            "armors": oSRD.getArmorProficienciesByClass(klass),
            "weapons": oSRD.getWeaponProficienciesByClass(klass),
        }
    )
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
    background = stdin("Choose your character's background.", oSRD.getBackgrounds())
    oSheet.set("background", background[0])

    # Choose ability bonuses
    ability_bonus_array = stdin(
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

        two_point_ability = stdin(
            "Choose which ability to apply a 2 point bonus.", background_abilities
        )
        chosen_ability = two_point_ability[0]
        bonus_array[chosen_ability] = 2

        one_point_ability = stdin(
            "Choose which ability to apply a 1 point bonus.", background_abilities
        )
        chosen_ability = one_point_ability[0]
        bonus_array[chosen_ability] = 1

    if ability_bonus_array[0] == "Apply 1/1/1":
        for ability in oSRD.getAbilityByBackground(oPC.getMyBackground()):
            bonus_array[ability] = 1

    oSheet.set("bonus", bonus_array)

    feat = stdin(
        "A background gives your character a specified Origin feat.",
        oSRD.getFeatsByCategory("Origin"),
    )
    oSheet.set("feats", feat)

    skills = stdin(
        "A background gives your character proficiency in two specified skills.",
        oSRD.getSkillsByBackground(oPC.getMyBackground()),
        loop_count=2,
    )
    oSheet.set("skills", skills)

    tool = stdin(
        "Each background gives a character proficiency with one tool-either a "
        "specific tool or one chosen from the Artisan's Tools category.",
        oSRD.getToolsByBackground(oPC.getMyBackground()),
    )
    oSheet.set("tools", tool)

    species = stdin("Choose a species for your character.", oSRD.getSpecies())[0]
    oSheet.set(
        {
            "size": oSRD.getSizeBySpecies(species),
            "species": species,
            "speed": oSRD.getSpeedBySpecies(species),
            "traits": oSRD.getTraitsBySpecies(species),
        }
    )

    languages = stdin(
        "Your character knows at least three languages: Common plus two languages.",
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
    results = generate_abilities(67)
    results.sort(reverse=True)
    ability_names = list(ability_array.keys())
    for score in results:
        ability = stdin(f"Assign {score} to which ability?", ability_names)
        ability_array[ability[0]] = {"score": score, "modifier": get_modifier(score)}

    # Apply background ability bonuses.
    for ability, bonus in oPC.getMyBonus().items():
        if bonus > 0:
            old_score = ability_array[ability]["score"]
            new_score = old_score + bonus
            if new_score > 20:
                new_score = 20
            ability_array[ability] = {
                "score": new_score,
                "modifier": get_modifier(new_score),
            }

    oSheet.set("attributes", ability_array)


def step4() -> None:
    # Choose an alignment
    alignment = stdin("Choose your alignment.", oSRD.getAlignments())[0]
    oSheet.set("alignment", alignment)


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
    skills = oSRD.getSkillsByClass(klass, oPC.getMySkills())
    if klass == "Rogue":
        allotted_skills = 4
    elif klass in ("Bard", "Ranger"):
        allotted_skills = 3
    else:
        allotted_skills = 2
    oSheet.set(
        "skills",
        stdin("Choose a class skill.", skills, loop_count=allotted_skills),
    )

    oSheet.set(
        {
            "cantrips": oSRD.getCantripsByClass(klass, oPC.getTotalLevel()),
            "features": oSRD.getFeaturesByClass(klass, oPC.getClassLevel(klass)),
            "hit_die": oSRD.getHitDieByClass(klass),
            "initiative": oPC.getAttributeModifier("Dexterity"),
            "prepared_spells": oSRD.getPreparedSpellsByClass(
                klass, oPC.getTotalLevel()
            ),
            "savingthrows": oSRD.getSavingThrowsByClass(klass),
            "spell_slots": oSRD.getSpellSlotsByClass(klass, oPC.getTotalLevel()),
        }
    )

    if klass == "Bard":
        oSheet.set(
            "tools",
            stdin(
                "Choose your musical instrument tool proficiencies.",
                oSRD.getToolsByClass(klass),
                loop_count=3,
            ),
        )
    elif klass == "Monk":
        oSheet.set(
            "tools",
            stdin(
                "Choose your artisan tool or musical instrument tool proficiencies.",
                oSRD.getToolsByClass(klass),
            ),
        )
    else:
        oSheet.set("tools", oSRD.getToolsByClass(klass))

    oSheet.set("gender", stdin("What's your gender?", ["Female", "Male"])[0])


def main() -> None:
    try:
        step1()
        step2()
        step3()
        step4()
        step5()

        name = None
        while name is None:
            name = input("What is your name? ")
            oSheet.set("name", name)

        cs = replace(
            oSheet,
            level=oPC.getTotalLevel(),
        )
        with Path(character_dir, f"{oPC.getMyName()}.toml").open("w") as record:
            toml.dump(asdict(cs), record)
            print("Character created successfully.")
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
