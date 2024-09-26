from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Dict, List, Literal, Union

import toml

from actor import CharacterSheet, PlayerCharacter
from attributes import Attributes, Score, generate_attributes, get_modifier
from system import SystemResourceDocument
import utils

oSheet = CharacterSheet()
oPC = PlayerCharacter(oSheet)
oSRD = SystemResourceDocument()


character_dir = Path.home() / ".config" / "tasha" / "characters"
if not character_dir.exists():
    character_dir.mkdir(parents=True)
    print(f"creating character directory.")


def tasha_cmd_save() -> None:
    """Performs the save action."""
    oSheet.set(
        {
            "allotted_asi": oSRD.calculateAllottedAsi(oPC.getMyRawClasses()),
            "traits": oSRD.getRacialMagic(oPC.getMySpecies(), oPC.getTotalLevel()),
        }
    )
    assignClassFeatures()
    assignClassSkills()
    assignAsiUpgrades()
    assignSpellcastingFeatures()
    cs = replace(
        oSheet,
        level=oPC.getTotalLevel(),
    )

    with Path(character_dir, f"{oPC.getMyName()}.toml").open("w") as record:
        toml.dump(asdict(cs), record)
        print("Character created successfully.")
        oSheet.reset()


def review_attributes() -> None:
    """Prints out all attributes (attribue/score/modifier)."""
    for attribute in tuple(oPC.getAttributes().keys()):
        print(
            f"{attribute}: {oPC.getAttributeScore(attribute)} ({oPC.getAttributeModifier(attribute)})"
        )


def assignAsiUpgrades() -> None:
    """Prompt assigns ability score improvements."""
    allotted_asi = oPC.getAllottedAsi()
    if allotted_asi == 0:
        return

    def assignAttributeUpgrade() -> None:
        """Prompt assigns an attribute upgrade."""
        bonus = int(
            Scan(
                message="How many points do you wish to apply?",
                selections=["1", "2"],
                completer=True,
            ),
        )
        bonus_attributes = list()
        if bonus == 1:
            num_of_bonuses = 2
        else:
            num_of_bonuses = 1

        for _ in range(0, num_of_bonuses):
            attribute = Scan(
                message="Which attribute do you wish to enhance?",
                selections=[
                    a
                    for a in oPC.getUpgradeableAttributes(bonus)
                    if a not in bonus_attributes
                ],
                completer=True,
            )
            bonus_attributes.append(attribute)
            base = Attributes(oPC.getAttributes())
            base.add(attribute, bonus)
            oSheet.attributes = base.attributes

    def assignFeatUpgrade() -> None:
        """Prompt assigns a feat upgrade."""
        excluded_feats = list()
        while True:
            feat = Scan(
                message="Choose a feat.",
                selections=oSRD.getFeats(oPC.getMyFeats() + excluded_feats),
                completer=True,
            )
            if hasFeatRequirements(feat):
                assignFeatEnhancements(feat)
                break
            else:
                excluded_feats.append(feat)
                print(f"You don't meet the requirements for '{feat}'.")

    asi_counter = allotted_asi
    for _ in range(0, allotted_asi):
        option = Scan(
            message=f"Would you like to select a feat or increase an ability? ({asi_counter})",
            selections=[
                "ability",
                "feat",
            ],
            completer=True,
        )
        if option == "Ability":
            assignAttributeUpgrade()
        if option == "Feat":
            assignFeatUpgrade()
        asi_counter -= 1


def assignAttributeValues(results: List[int]) -> Dict[str, Dict[str, int]]:
    """Assigns the six attributes and applies any bonuses where applicable."""
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
        """Returns the ordered attributes dictionary."""
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
        """Sets the attribute_name to the specified attribute_value."""
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


def assignCantrips(
    klass: str,
    cantrips_known: Union[int, None] = None,
    subklass: Union[str, None] = None,
) -> List[str]:
    """Selects character's cantrips."""
    if subklass is not None:
        subklass = oPC.getClassSubclass(klass)

    my_cantrip_list = list()
    cantrip_pool = oSRD.getListCantrips(klass, subklass)
    if len(cantrip_pool) == 0:
        return my_cantrip_list

    if cantrips_known is None:
        cantrips_known = int(oPC.getSpellSlots()[0])
    cantrip_selection_counter = cantrips_known

    for _ in range(cantrips_known):
        cantrip = Scan(
            message=f"Choose a cantrip ({cantrip_selection_counter}).",
            selections=cantrip_pool,
            completer=True,
        )
        my_cantrip_list.append(cantrip)
        cantrip_pool.remove(cantrip)
        cantrip_selection_counter -= 1

    if subklass == "Arcane Trickster" and "Mage Hand" not in my_cantrip_list:
        my_cantrip_list.append("Mage Hand")

    return my_cantrip_list


def assignClassFeatures() -> None:
    """Assigns class features."""

    def assignSubclassFeatures(klass: str) -> None:
        """Prompt assigns subclass features."""
        if not oPC.canSubclass(klass):
            return

        subclass = Scan(
            message=f"What is your '{klass}' subclass?",
            selections=oSRD.getSubclassesByClass(klass),
            completer=True,
        )
        oSheet.classes[klass]["subclass"] = subclass
        base_subclass_traits = oSRD.getEntryBySubclass(subclass)
        oSheet.set(
            {
                "armors": base_subclass_traits["armors"],
                "tools": base_subclass_traits["tools"],
                "weapons": base_subclass_traits["weapons"],
                "features": oSRD.getFeaturesByClass(subclass, oPC.getClassLevel(klass)),
            }
        )

    import dice

    for class_order, klass in enumerate(oPC.getMyClasses()):
        if class_order == 0:
            traits = oSRD.getEntryByClass(klass)
            starting_gold = sum(
                dice.roll(
                    traits["gold"]
                )  # pyright: ignore[reportArgumentType, reportCallIssue]
            )

            oSheet.set(
                {
                    "allotted_skills": oPC.getSkillTotal(),
                    "armors": traits["armors"],
                    "languages": traits["languages"],
                    "savingthrows": traits["savingthrows"],
                    "tools": traits["tools"],
                    "weapons": traits["weapons"],
                    "features": oSRD.getFeaturesByClass(
                        klass, oPC.getClassLevel(klass)
                    ),
                    "gold": starting_gold * 10 if klass != "Monk" else starting_gold,
                }
            )
        else:
            traits = oSRD.getEntryByMulticlass(klass)
            oSheet.set(
                {
                    "armors": traits["armors"],
                    "tools": traits["tools"],
                    "weapons": traits["weapons"],
                }
            )

        assignSubclassFeatures(klass)

    oSheet.set(
        "spell_slots", oSRD.getSpellSlots(oPC.getMyRawClasses(), oPC.getTotalLevel())
    )


def assignClassSkills() -> None:
    """Prompt to determining the character's skills features."""
    for _ in range(0, oPC.getAllottedSkills()):
        skill = Scan(
            message="Choose your class skill.",
            selections=oSRD.getSkillsByClass(oPC.getMyClasses()[0], oPC.getMySkills()),
            completer=True,
        )
        oSheet.set("skills", skill.capitalize())


def assignFeatEnhancements(feat: str) -> None:
    """Prompt assigns the proper enhancements by feat."""

    def getAdjustableAttributes(checked_attributes: List[str]) -> List[str]:
        """Checks the checked_attributes for upgradeable attributes."""
        adjustable_attributes = list()
        for attribute in checked_attributes:
            adjusted_score = oPC.getAttributeScore(attribute) + 1
            if adjusted_score <= 20:
                adjustable_attributes.append(attribute)
        return adjustable_attributes

    traits = oSRD.getEntryByFeat(feat)
    oSheet.set(
        {
            "armors": traits["armors"],
            "weapons": traits["weapons"],
        }
    )

    base_attributes = Attributes(oPC.getAttributes())

    # Actor/Heavy Armor Master/Keen Mind
    if feat in ("Actor", "Heavy Armor Master", "Keen Mind"):
        if feat == "Actor":
            base_attributes.add("Charisma", 1)
        elif feat == "Heavy Armor Master":
            base_attributes.add("Strength", 1)
        elif feat == "Keen Mind":
            base_attributes.add("Intelligence", 1)

    # Feats that allow attribute increase selections
    if feat in (
        "Athlete",
        "Chef",
        "Fade Away",
        "Fey Teleportation",
        "Lightly Armored",
        "Moderately Armored",
        "Observant",
        "Orcish Fury",
        "Second Chance",
        "Slasher",
        "Tavern Brawler",
        "Telekinetic",
        "Telepathic",
        "Weapon Master",
    ):
        if feat in ("Athlete", "Slasher"):
            attribute_bonuses = ["Dexterity", "Strength"]
        elif feat == "Chef":
            attribute_bonuses = ["Constitution", "Wisdom"]
        elif feat in ("Dragon Fear", "Dragon Hide"):
            attribute_bonuses = ["Charisma", "Constitution", "Strength"]
        elif feat == "Elven Accuracy":
            attribute_bonuses = ["Charisma", "Dexterity", "Intelligence", "Wisdom"]
        elif feat == "Fade Away":
            attribute_bonuses = ["Dexterity", "Intelligence"]
        elif feat == "Fey Teleportation":
            attribute_bonuses = ["Charisma", "Intelligence"]
        elif feat in ("Lightly Armored", "Moderately Armored"):
            attribute_bonuses = ["Dexterity", "Strength"]
        elif feat == "Observant":
            attribute_bonuses = ["Intelligence", "Wisdom"]
        elif feat in ("Orcish Fury", "Tavern Brawler"):
            attribute_bonuses = ["Constitution", "Strength"]
        elif feat == "Second Chance":
            attribute_bonuses = ["Charisma", "Constitution", "Dexterity"]
        elif feat in ("Fey Touched", "Shadow Touched", "Telekinetic", "Telepathic"):
            attribute_bonuses = ["Intelligence", "Wisdom", "Charisma"]
        elif feat == "Weapon Master":
            attribute_bonuses = ["Dexterity", "Strength"]
        attribute_bonus = Scan(
            message="Choose an attribute to upgrade.",
            selections=getAdjustableAttributes(attribute_bonuses),
            completer=True,
        )
        base_attributes.add(attribute_bonus, 1)

    # Durable/Dwarven Fortitude
    if feat in ("Durable", "Dwarven Fortitude"):
        base_attributes.add("Constitution", 1)

    # Heavily Armored
    if feat == "Heavily Armored":
        base_attributes.add("Strength", 1)

    # Resilient
    if feat == "Resilient":
        attribute_bonuses = [
            "Strength",
            "Dexterity",
            "Constitution",
            "Intelligence",
            "Wisdom",
            "Charisma",
        ]
        attribute_bonuses = getAdjustableAttributes(attribute_bonuses)
        attribute_bonuses = [
            s for s in attribute_bonuses if s.capitalize() not in oSheet.savingthrows
        ]
        attribute_bonus = Scan(
            message="Choose an attribute to upgrade.",
            selections=attribute_bonuses,
            completer=True,
        )
        base_attributes.add(attribute_bonus, 1)
        oSheet.set("savingthrows", attribute_bonus.capitalize())

    # Skilled
    if feat == "Skilled":
        for _ in range(3):
            bonus_option = Scan(
                message="Choose a feat (Skilled) bonus skill or tool.",
                selections=["Skill", "Tool"],
                completer=True,
            )
            if bonus_option == "Skill":
                oSheet.set(
                    "skills",
                    Scan(
                        message="Choose a bonus skill.",
                        selections=oSRD.getListSkills(oPC.getMySkills()),
                        completer=True,
                    ),
                )
            elif bonus_option == "Tool":
                oSheet.set(
                    "tools",
                    Scan(
                        message="Choose a bonus tool proficiency.",
                        selections=oSRD.getToolProficiencies(oPC.getMyTools()),
                        completer=True,
                    ),
                )

    # Telekinetic
    if feat == "Telekinetic":
        oSheet.set("features", "Mage Hand")

    # Telepathic
    if feat == "Telepathic":
        oSheet.set("features", "Detect Thoughts")

    # Weapon Master
    if feat == "Weapon Master":
        for _ in range(4):
            bonus_weapons = oSRD.getListWeapons(oPC.getMyWeapons())
            oSheet.set(
                "weapons",
                Scan(
                    message="Choose a bonus weapon proficiency.",
                    selections=bonus_weapons,
                    completer=True,
                ),
            )

    oSheet.set({"feats": feat})


def assignRacialTraits() -> None:
    """Assigns racial/subracial traits."""
    full_race = oPC.getMySpecies().split(", ")
    if len(full_race) > 1:
        race, subrace = full_race
    else:
        race, subrace = (oPC.getMySpecies(), "")

    traits = oSRD.getEntryBySpecies(race)
    oSheet.set(
        {
            "bonus": traits["bonus"],
            "languages": traits["languages"],
            "size": traits["size"],
            "skills": traits["skills"],
            "traits": traits["traits"],
            "weapons": traits["weapons"],
        }
    )

    assignTraitsDragonborn()

    if subrace != "":
        traits = oSRD.getEntryByLineage(subrace)
        oSheet.set({"bonus": traits["bonus"], "traits": traits["traits"]})


def assignSpellcastingFeatures() -> None:
    """Assigns character's spellcasting features, if applicable."""
    if not oPC.isSpellcaster():
        return

    def assignSpells() -> None:
        """Select's character's spells."""

        def getArcanumSpellSelections(
            player_spells: List[str], warlock_spells: List[str]
        ) -> List[str]:
            """Removes 6-9 level spells if a spell is already known for that level."""
            for spell_level in range(6, 10):
                for spell in player_spells:
                    level_query = f"(lv. {spell_level})"
                    if level_query in spell:
                        warlock_spells = [
                            s for s in warlock_spells if level_query not in s
                        ]
            return warlock_spells

        for klass in oPC.getMyClasses():
            allotted_spell_total = oSRD.getSpellTotal(
                klass,
                oPC.getClassLevel(klass),
                get_modifier(
                    oPC.getCasterAttribute(klass, oPC.getClassSubclass(klass))
                ),
            )
            spell_selection_counter = allotted_spell_total

            spell_pool = oSRD.getListSpells(
                klass, oPC.getClassSubclass(klass), oPC.getClassLevel(klass)
            )
            my_spell_list = list()

            for _ in range(allotted_spell_total):
                if klass == "Warlock":
                    spell_pool = getArcanumSpellSelections(my_spell_list, spell_pool)

                spell = Scan(
                    message=f"Choose a spell ({spell_selection_counter}).",
                    selections=spell_pool,
                    completer=True,
                )
                my_spell_list.append(spell)
                spell_pool.remove(spell)
                spell_selection_counter -= 1

            my_spell_pool = {}
            my_spell_pool[klass] = my_spell_list

            oSheet.set("spellcasting", my_spell_pool)

    if len(oPC.getSpellSlots()) == 0:
        return

    for klass in oPC.getMyClasses():
        oSheet.set("cantrips", {klass: assignCantrips(klass)})

    assignSpells()


def assignTraitsDragonborn() -> None:
    """Assigns dragonborn features."""
    if "Dragonborn" not in oPC.getMySpecies():
        return

    draconic_ancestors = [
        "Black",
        "Blue",
        "Brass",
        "Bronze",
        "Copper",
        "Gold",
        "Green",
        "Red",
        "Silver",
        "White",
    ]
    draconic_ancestry = Scan(
        message="Choose your dragonborn's ancestry.",
        selections=draconic_ancestors,
        completer=True,
    )
    oSheet.set("ancestry", draconic_ancestry)
    draconic_resistances = {
        "Black": ["Acid"],
        "Blue": ["Lightning"],
        "Brass": ["Fire"],
        "Bronze": ["Lightning"],
        "Copper": ["Acid"],
        "Gold": ["Fire"],
        "Green": ["Poison"],
        "Red": ["Fire"],
        "Silver": ["Cold"],
        "White": ["Cold"],
    }
    oSheet.set("resistances", draconic_resistances[draconic_ancestry])


def hasFeatRequirements(feat: str) -> Union[Literal[False], Literal[True]]:
    """Returns True if character meets feat prerequisites."""
    if feat in oPC.getMyFeats():
        return False

    # If Heavily, Lightly, or Moderately Armored feat selected and is a Monk.
    # Otherwise feat is "Armor Related" or Weapon Master feat but already proficient.
    if (
        feat
        in (
            "Heavily Armored",
            "Lightly Armored",
            "Moderately Armored",
        )
        and "Monk" in oPC.getMyClasses()
    ):
        return False

    if feat in (
        "Heavily Armored",
        "Lightly Armored",
        "Moderately Armored",
        "Weapon Master",
    ):
        if feat == "Heavily Armored" and "Heavy" in oPC.getMyArmors():
            return False
        if feat == "Lightly Armored" and "Light" in oPC.getMyArmors():
            return False
        if feat == "Moderately Armored" and "Medium" in oPC.getMyArmors():
            return False
        if feat == "Weapon Master" and "Martial" in oPC.getMyWeapons():
            return False

    feat_requirements = oSRD.getEntryByFeat(feat)
    for category, _ in feat_requirements.items():
        if feat_requirements[category] is None:
            continue

        if category == "ability":
            for attribute, minimum_score in feat_requirements[category].items():
                if oPC.getAttributeScore(attribute) < minimum_score:
                    return False

        if category == "caster":
            if not oPC.isSpellcaster():
                return False

            if feat == "Magic Initiate":
                applicable_classes = (
                    "Bard",
                    "Cleric",
                    "Druid",
                    "Sorcerer",
                    "Warlock",
                    "Wizard",
                )
                for klass in oPC.getMyClasses():
                    if klass in applicable_classes:
                        return True
                return False

            if feat == "Ritual Caster":
                if not oPC.hasClass("Cleric") or not oPC.hasClass("Wizard"):
                    return False

                if (
                    "Cleric" in oPC.getMyClasses()
                    and oPC.getAttributeScore("Wisdom")
                    < feat_requirements["ability"]["Wisdom"]
                ):
                    return False

                if (
                    "Wizard" in oPC.getMyClasses()
                    and oPC.getAttributeScore("Intelligence")
                    < feat_requirements["ability"]["Intelligence"]
                ):
                    return False

        # Check proficiency requirements
        if category == "proficiency":
            if feat in (
                "Heavy Armor Master",
                "Heavily Armored",
                "Medium Armor Master",
                "Moderately Armored",
            ):
                required_armors = feat_requirements[category]["armors"]
                for armor in required_armors:
                    if armor not in required_armors:
                        return False

    return True


def isPreparedCaster(self) -> bool:
    """Returns True if character is a prepared spellcaster."""
    for klass in self.getMyClasses():
        if klass in ("Cleric", "Druid", "Paladin", "Wizard"):
            return True
    return False


def step1():
    # Choose class/subclass
    # Select level
    klass = utils.stdin("What class are you?", oSRD.getClasses())[0]
    level = int(utils.stdin("What is your level?", 20)[0])
    subclass = ""
    if level >= 3:
        subklass = utils.stdin(
            "What subclass are you?", oSRD.getSubclassesByClass(klass)
        )
        subclass = subklass[0]
    oSheet.set("classes", {klass: {"level": level, "subclass": subclass}})


def step2():
    # Choose a background
    # Choose a species
    # Choose equipment
    background = utils.stdin("What is your background?", oSRD.getBackgrounds())
    oSheet.set("background", background[0])

    # Choose ability bonuses
    ability_bonus_array = utils.stdin(
        "Choose background ability bonus array.", ["2/1", "1/1/1"]
    )
    bonus_array = {
        "Strength": 0,
        "Dexterity": 0,
        "Constitution": 0,
        "Intelligence": 0,
        "Wisdom": 0,
        "Charisma": 0,
    }
    if ability_bonus_array[0] == "2/1":
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
    if ability_bonus_array[0] == "1/1/1":
        for ability in oSRD.getAbilityByBackground(oPC.getMyBackground()):
            bonus_array[ability] = 1
    oSheet.set("bonus", bonus_array)

    feat = utils.stdin(
        "Choose a feat from your background.", oSRD.getFeatsByCategory("Origin")
    )
    oSheet.set("feats", feat)

    skills = utils.stdin(
        "Choose two skills from your background.",
        oSRD.getSkillsByBackground(oPC.getMyBackground()),
        loop_count=2,
    )
    oSheet.set("skills", skills)

    tool = utils.stdin(
        "Choose a tool proficiency from your background.",
        oSRD.getToolsByBackground(oPC.getMyBackground()),
    )
    oSheet.set("tools", tool)

    species = utils.stdin("What is your species?", oSRD.getSpecies())[0]
    lineage = ""
    lineages = oSRD.getLineagesBySpecies(species)
    if len(lineages) != 0:
        lineage = utils.stdin(f"Choose your {species} lineage.", lineages)[0]
        species = f"{species}, {lineage}"
    oSheet.set("species", species)

    languages = utils.stdin(
        "Choose three languages.", oSRD.getStandardLanguages(), loop_count=3
    )
    oSheet.set("languages", languages)


def step3():
    # Generate/Assign ability scores
    pass


def step4():
    pass


def step5():
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