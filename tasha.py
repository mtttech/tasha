from dataclasses import asdict, replace
from pathlib import Path
from typing import List, Literal, Union

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
    print("Created the character directory.")


def getSelectableFeats() -> List[str]:
    """Returns a list of selectable feats."""
    return [f for f in oSRD.getFeats() if hasFeatRequirements(f)]


def hasFeatRequirements(feat: str) -> Union[Literal[False], Literal[True]]:
    """Returns True if character meets feat prerequisites, False otherwise."""
    raw_ability_requirements = oSRD.getAbilityRequirementsByFeat(feat)
    required_abilities = list(raw_ability_requirements.keys())
    if len(required_abilities) > 0:
        ability_chk_success = False
        for ability in required_abilities:
            if oPC.getAttributeScore(ability) >= raw_ability_requirements[ability]:
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


def loadPC(character_name: str) -> PlayerCharacter:
    """Loads character toml file to PlayerCharacter object."""
    import tomllib

    with Path(character_dir, f"{character_name}.toml").open("rb") as file:
        data = tomllib.load(file)
    del data["hit_points"]
    return PlayerCharacter(CharacterSheet(**data))


def step1() -> None:
    # Choose class/subclass
    # Select level
    print("Choose a class.")
    klass = stdin(oSRD.getClasses())[0]
    print("What is your character's class level?")
    level = int(stdin(20)[0])
    subclass = ""
    if level >= 3:
        print("If you start at level 3 or higher, choose a subclass.")
        subklass = stdin(
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
    print("Choose your character's background.")
    background = stdin(oSRD.getBackgrounds())
    oSheet.set("background", background[0])

    # Choose ability bonuses
    print(
        "A background lists three of your character's ability scores. Increase "
        "one by 2 and another one by 1, or increase all three by 1. None of "
        "these increases can raise a score above 20."
    )
    ability_bonus_array = stdin(
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

        print("Choose which ability to apply a 2 point bonus.")
        two_point_ability = stdin(background_abilities)
        chosen_ability = two_point_ability[0]
        bonus_array[chosen_ability] = 2

        print("Choose which ability to apply a 1 point bonus.")
        one_point_ability = stdin(background_abilities)
        chosen_ability = one_point_ability[0]
        bonus_array[chosen_ability] = 1

    if ability_bonus_array[0] == "Apply 1/1/1":
        for ability in oSRD.getAbilityByBackground(oPC.getMyBackground()):
            bonus_array[ability] = 1

    oSheet.set("bonus", bonus_array)

    print("A background gives your character a specified Origin feat.")
    feat = stdin(oSRD.getFeatsByCategory("Origin"))
    oSheet.set("feats", feat)

    print("A background gives your character proficiency in two specified skills.")
    skills = stdin(
        oSRD.getSkillsByBackground(oPC.getMyBackground()),
        loop_count=2,
    )
    oSheet.set("skills", skills)

    print(
        "Each background gives a character proficiency with one tool-either a "
        "specific tool or one chosen from the Artisan's Tools category."
    )
    tool = stdin(
        oSRD.getToolsByBackground(oPC.getMyBackground()),
    )
    oSheet.set("tools", tool)

    print("Choose a species for your character.")
    species = stdin(oSRD.getSpecies())[0]
    oSheet.set(
        {
            "size": oSRD.getSizeBySpecies(species),
            "species": species,
            "speed": oSRD.getSpeedBySpecies(species),
            "traits": oSRD.getTraitsBySpecies(species),
        }
    )

    print("Your character knows at least three languages: Common plus two languages.")
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
    results = generate_abilities(67)
    results.sort(reverse=True)
    ability_names = list(ability_array.keys())
    for score in results:
        print(f"Assign {score} to which ability?")
        ability = stdin(ability_names)
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
    print("Choose your alignment.")
    alignment = stdin(oSRD.getAlignments())[0]
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
    print("Choose a class skill.")
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

    print("Choose your feats.")
    ability_score_improvements = oSRD.getFeaturesByClass(
        klass, oPC.getTotalLevel()
    ).count("Ability Score Improvement")
    oSheet.set(
        "feats", stdin(getSelectableFeats(), loop_count=ability_score_improvements)
    )

    print("What's your gender?")
    oSheet.set("gender", stdin(["Female", "Male"])[0])

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
        print("Choose your musical instrument tool proficiencies.")
        oSheet.set(
            "tools",
            stdin(
                oSRD.getToolsByClass(klass),
                loop_count=3,
            ),
        )
    elif klass == "Monk":
        print("Choose your artisan tool or musical instrument tool proficiencies.")
        oSheet.set(
            "tools",
            stdin(
                oSRD.getToolsByClass(klass),
            ),
        )
    else:
        oSheet.set("tools", oSRD.getToolsByClass(klass))


def main() -> None:
    try:
        step1()
        step2()
        step3()
        step4()
        step5()

        name = None
        while name is None:
            name = input("What is your character's name? ").strip()
            if name == "":
                name = None
            else:
                oSheet.set("name", name.replace(" ", "_"))

        import toml

        cs = replace(
            oSheet,
            level=oPC.getTotalLevel(),
        )
        with Path(character_dir, f"{oPC.getMyName()}.toml").open("w") as record:
            toml.dump(asdict(cs), record)
            print(f"Character '{oPC.getMyName()}' created successfully.")
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
