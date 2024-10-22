from dataclasses import asdict, replace
from pathlib import Path
from typing import List, Literal, Union

from rich.console import Console

from tasha.actor import CharacterSheet, PlayerCharacter
from tasha.attributes import generate_abilities, get_modifier
from tasha.d20 import SystemResourceDocument
from tasha.utils import stdin

console = Console(width=80)
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
    console.print("[bold green]Choose a class.[/bold green]")
    klass = stdin(oSRD.getClasses())[0]
    console.print("[bold green]What is your character's class level?[/bold green]")
    level = int(stdin(20)[0])
    subclass = ""
    if level >= 3:
        console.print(
            "[yellow]If you start at level 3 or higher, choose a subclass.[/yellow]"
        )
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
    console.print("[bold green]Choose your character's background.[/bold green]")
    oSheet.set("background", stdin(oSRD.getBackgrounds())[0])

    # Choose ability bonuses
    console.print(
        "[bold green]A background lists three of your character's ability scores. Increase "
        "one by 2 and another one by 1, or increase all three by 1. None of "
        "these increases can raise a score above 20.[/bold green]"
    )
    ability_bonus_array = {
        "Strength": 0,
        "Dexterity": 0,
        "Constitution": 0,
        "Intelligence": 0,
        "Wisdom": 0,
        "Charisma": 0,
    }
    bonus_array_selections = stdin(
        ["Apply 2/1", "Apply 1/1/1"],
    )
    if bonus_array_selections[0] == "Apply 2/1":
        background_abilities = oSRD.getAbilitiesByBackground(oPC.getMyBackground())

        print("Choose which ability to apply a 2 point bonus.")
        two_point_ability = stdin(background_abilities)
        chosen_ability = two_point_ability[0]
        ability_bonus_array[chosen_ability] = 2

        print("Choose which ability to apply a 1 point bonus.")
        one_point_ability = stdin(background_abilities)
        chosen_ability = one_point_ability[0]
        ability_bonus_array[chosen_ability] = 1

    if bonus_array_selections[0] == "Apply 1/1/1":
        for ability in oSRD.getAbilitiesByBackground(oPC.getMyBackground()):
            ability_bonus_array[ability] = 1

    oSheet.set("bonus", ability_bonus_array)

    console.print(
        "[bold green]A background gives your character a specified Origin feat.[/bold green]"
    )
    oSheet.set("feats", stdin(oSRD.getFeatsByCategory("Origin")))

    console.print(
        "[bold green]A background gives your character proficiency in two specified skills.[/bold green]"
    )
    skills = stdin(
        oSRD.getSkillsByBackground(oPC.getMyBackground()),
        loop_count=2,
    )
    oSheet.set("skills", skills)

    print(
        "[bold green]Each background gives a character proficiency with one tool-either a "
        "specific tool or one chosen from the Artisan's Tools category.[/bold green]"
    )
    tool = stdin(
        oSRD.getToolProficienciesByBackground(oPC.getMyBackground()),
    )
    oSheet.set("tools", tool)

    console.print("[bold green]Choose a species for your character.[/bold green]")
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
        "[bold green]Your character knows at least three languages: Common plus two languages.[/bold green]"
    )
    languages = stdin(
        oSRD.getStandardLanguages(),
        loop_count=2,
    )
    oSheet.set("languages", ["Common"] + languages)


def step3() -> None:
    # Generate/Assign ability scores
    from random import randint

    ability_array = {
        "Strength": {"score": 0, "modifier": 0},
        "Dexterity": {"score": 0, "modifier": 0},
        "Constitution": {"score": 0, "modifier": 0},
        "Intelligence": {"score": 0, "modifier": 0},
        "Wisdom": {"score": 0, "modifier": 0},
        "Charisma": {"score": 0, "modifier": 0},
    }
    results = generate_abilities(randint(65, 90))
    results.sort(reverse=True)
    ability_names = list(ability_array.keys())
    for score in results:
        console.print(f"[bold green]Assign {score} to which ability?[/bold green]")
        ability_array[stdin(ability_names)[0]] = {
            "score": score,
            "modifier": get_modifier(score),
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
                "modifier": get_modifier(new_score),
            }

    oSheet.set("attributes", ability_array)


def step4() -> None:
    # Choose an alignment
    console.print("[bold green]Choose your alignment.[/bold green]")
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
    skills = oSRD.getSkillsByClass(klass, oPC.getMySkills())
    console.print("[bold green]Choose a class skill.[/bold green]")
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

    console.print("[bold green]Choose your feats.[/bold green]")
    ability_score_improvements = oSRD.getFeaturesByClass(
        klass, oPC.getTotalLevel()
    ).count("Ability Score Improvement")
    oSheet.set(
        "feats", stdin(getSelectableFeats(), loop_count=ability_score_improvements)
    )

    console.print("[bold green]What's your gender?[/bold green]")
    oSheet.set("gender", stdin(["Female", "Male"])[0])

    oSheet.set(
        {
            "cantrips": oSRD.getCantripsKnownByClass(klass, oPC.getTotalLevel()),
            "features": oSRD.getFeaturesByClass(klass, oPC.getClassLevel(klass)),
            "hit_die": oSRD.getHitDieByClass(klass),
            "initiative": oPC.getAttributeModifier("Dexterity"),
            "savingthrows": oSRD.getSavingThrowsByClass(klass),
            "spell_slots": oSRD.getSpellSlotsByClass(klass, oPC.getTotalLevel()),
        }
    )

    if klass == "Bard":
        print("Choose your bardic musical instrument tool proficiencies.")
        oSheet.set(
            "tools",
            stdin(
                oSRD.getToolProficienciesByClass(klass),
                loop_count=3,
            ),
        )
    elif klass == "Monk":
        print("Choose your monk artisan or musical instrument tool proficiency.")
        oSheet.set(
            "tools",
            stdin(
                oSRD.getToolProficienciesByClass(klass),
            ),
        )
    else:
        oSheet.set("tools", oSRD.getToolProficienciesByClass(klass))

    if oPC.isSpellcaster():
        prepared_spells = list()
        prepared_spell_count = oSRD.getPreparedSpellCountByClass(
            klass, oPC.getTotalLevel()
        )
        spell_levels = [l + 1 for l, _ in enumerate(oPC.getMySpellSlots())]
        while len(prepared_spells) < prepared_spell_count:
            try:
                spell_level = int(
                    input(
                        f"Choose a level of spells to select from {spell_levels[0]}-{spell_levels[-1]}. "
                    )
                )
                if spell_level not in spell_levels:
                    raise ValueError

                print(f"Choose a level {spell_level} spell.")
                chosen_spell = stdin(
                    oSRD.getSpellListByClass(klass, spell_level)[spell_level]
                )[0]
                prepared_spells.append(chosen_spell)
            except ValueError:
                pass

        oSheet.set("prepared_spells", {klass: prepared_spells})


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
