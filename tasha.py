from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Dict, List, Literal, Tuple, Union

import toml

from actor import CharacterSheet, NonPlayerCharacter
from attributes import Attributes, Score, generate_attributes, get_modifier
from system import SystemResourceDocument
import utility

oSheet = CharacterSheet()
oNPC = NonPlayerCharacter(oSheet)
oSRD = SystemResourceDocument()


try:
    pyproject_file = Path(__file__).parents[0] / "pyproject.toml"
    with pyproject_file.open("r") as pyproject:
        try:
            __version__ = toml.load(pyproject)["project"]["version"]
        except KeyError:
            print(f"cannot detect my version number.")
            exit(1)
except FileNotFoundError:
    print("cannot locate 'pyproject.toml'.")
    exit(1)

character_dir = Path.home() / ".config" / "tasha" / "characters"
if not character_dir.exists():
    character_dir.mkdir(parents=True)
    print(f"creating character directory.")


class TashaCommandError(Exception):
    pass


def tasha_cmd_add(value: str) -> None:
    """Performs the add action."""
    if value not in oSRD.getClasses():
        raise TashaCommandError("the add class action requires a valid class.")

    if oNPC.hasClasses() and value not in oSRD.getListMulticlasses(
        oNPC.getMyClasses(),
        oNPC.getTotalLevel(),
        oNPC.getAttributes(),
    ):
        raise TashaCommandError(f"you don't meet the requirements to multiclass.")

    level_allowance = 20
    level_allowance = level_allowance - oNPC.getTotalLevel()
    if level_allowance == 0:
        raise TashaCommandError("you cannot select anymore classes.")

    level = int(
        Scan(
            message=f"What is your '{value}' level (1-{level_allowance})?",
            selections=[str(_) for _ in list(range(1, level_allowance + 1))],
            completer=True,
        )
    )
    oSheet.classes[value] = {}
    oSheet.classes[value]["hit_die"] = oSRD.getHitDieByClass(value)
    oSheet.classes[value]["level"] = level
    oSheet.classes[value]["subclass"] = ""


def tasha_cmd_save() -> None:
    """Performs the save action."""
    if oNPC.getMyName() == "":
        raise TashaCommandError(
            "cannot run save action because you haven't set a name."
        )

    if oNPC.getMyAlignment() == "":
        raise TashaCommandError(
            "cannot run save action because you haven't set an alignment."
        )

    if not oNPC.hasClasses():
        raise TashaCommandError(
            "cannot run save action because you don't have at least one class."
        )

    oSheet.set(
        {
            "allotted_asi": oSRD.calculateAllottedAsi(oNPC.getMyRawClasses()),
            "traits": oSRD.getRacialMagic(oNPC.getMyRace(), oNPC.getTotalLevel()),
            "version": __version__,
        }
    )
    assignClassFeatures()
    assignClassSkills()
    assignAsiUpgrades()
    assignSpellcastingFeatures()
    cs = replace(
        oSheet,
        level=oNPC.getTotalLevel(),
    )

    with Path(character_dir, f"{oNPC.getMyName()}.toml").open("w") as record:
        toml.dump(asdict(cs), record)
        print("Character created successfully.")
        oSheet.reset()


def tasha_cmd_set(parameter: str, value: str) -> None:
    """Performs the set action."""
    if parameter in (
        "alignment",
        "name",
    ):
        if parameter == "alignment" and value not in oSRD.getListAlignments():
            raise TashaCommandError(f"you selected an invalid alignment '{value}'.")

        oSheet.set(parameter, value)


def tasha_toolbar() -> List[Tuple[str, ...]]:
    """Returns the prompt_toolkit bottom toolbar."""
    gender = oNPC.getMyGender()
    if gender == "Female":
        gender = ""
    elif gender == "Male":
        gender = ""
    else:
        gender = ""

    if len(oNPC.getAttributes()) > 0:
        attribute_string = list()
        for a, v in oNPC.getAttributes().items():
            attribute_string.append("{}: {}".format(a[0:3], v["score"]))
        attribute_string = " ".join(attribute_string)
        attributes = f"  {attribute_string}"
    else:
        attributes = ""

    return [
        (
            "class:bottom-toolbar",
            f" tasha {__version__} - Type 'help' for assistance :: "
            f"{oNPC.getMyName()} "
            f"{gender} {oNPC.getMyRace()} "
            f"{'/'.join(oNPC.getMyClasses())} "
            f"{attributes} ",
        )
    ]


def review_attributes() -> None:
    """Prints out all attributes (attribue/score/modifier)."""
    for attribute in tuple(oNPC.getAttributes().keys()):
        print(
            f"{attribute}: {oNPC.getAttributeScore(attribute)} ({oNPC.getAttributeModifier(attribute)})"
        )


def assignAsiUpgrades() -> None:
    """Prompt assigns ability score improvements."""
    allotted_asi = oNPC.getAllottedAsi()
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
                    for a in oNPC.getUpgradeableAttributes(bonus)
                    if a not in bonus_attributes
                ],
                completer=True,
            )
            bonus_attributes.append(attribute)
            base = Attributes(oNPC.getAttributes())
            base.add(attribute, bonus)
            oSheet.attributes = base.attributes

    def assignFeatUpgrade() -> None:
        """Prompt assigns a feat upgrade."""
        excluded_feats = list()
        while True:
            feat = Scan(
                message="Choose a feat.",
                selections=oSRD.getListFeats(oNPC.getMyFeats() + excluded_feats),
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


def assignBackgroundTraits() -> None:
    """Prompt for setting the character's background."""
    oSheet.set(
        "background",
        Scan(
            message=f"What is your background?",
            selections=oSRD.getBackgrounds(),
            completer=True,
        ),
    )

    background_traits = oSRD.getEntryByBackground(oNPC.getMyBackground())
    oSheet.set(
        {
            "equipment": background_traits["equipment"],
            "gold": background_traits["gold"],
            "skills": background_traits["skills"],
            "tools": background_traits["tools"],
        }
    )

    # Backgrounds that have a bonus language(s).
    if oNPC.getMyBackground() in (
        "Acolyte",
        "City Watch",
        "Clan Crafter",
        "Cloistered Scholar",
        "Faction Agent",
        "Far Traveler",
        "Feylost",
        "Guild Artisan",
        "Hermit",
        "Investigator",
        "Noble",
        "Outlander",
        "Sage",
        "Witchlight Hand",
    ):
        if (
            oNPC.getMyBackground() == "Clan Crafter"
            and "Dwarvish" not in oNPC.getMyLanguages()
        ):
            oSheet.set("languages", "Dwarvish")
        else:
            number_of_languages = (
                2
                if oNPC.getMyBackground()
                in (
                    "Acolyte",
                    "City Watch",
                    "Cloistered Scholar",
                    "Faction Agent",
                    "Investigator",
                    "Sage",
                )
                else 1
            )
            if oNPC.getMyBackground() != "Feylost":
                bonus_languages = oSRD.getStandardLanguages(oNPC.getMyLanguages())
            else:
                bonus_languages = ("Elvish", "Gnomish", "Goblin", "Sylvan")
                bonus_languages = [
                    l for l in bonus_languages if l not in oNPC.getMyLanguages()
                ]
            for _ in range(number_of_languages):
                language = Scan(
                    message=f"Choose a '{oNPC.getMyBackground()}' background bonus language.",
                    selections=bonus_languages,
                    completer=True,
                )
                oSheet.set(
                    "languages",
                    language,
                )
                if number_of_languages > 1:
                    bonus_languages.remove(language)

    # Backgrounds that have bonus skills proficiencies.
    if oNPC.getMyBackground() in (
        "Cloistered Scholar",
        "Faction Agent",
    ):
        bonus_skills = []
        if oNPC.getMyBackground() == "Cloistered Scholar":
            bonus_skills = ["Arcana", "Nature", "Religion"]
        elif oNPC.getMyBackground() == "Faction Agent":
            bonus_skills = [
                "Animal Handling",
                "Arcana",
                "Deception",
                "History",
                "Insight",
                "Intimidation",
                "Investigation",
                "Medicine",
                "Nature",
                "Perception",
                "Performance",
                "Persuasion",
                "Religion",
                "Survial",
            ]
        oSheet.set(
            "skills",
            Scan(
                message=f"Choose a '{oNPC.getMyBackground()}' background bonus skill.",
                selections=[s for s in bonus_skills if s not in oNPC.getMySkills()],
                completer=True,
            ),
        )

    # Backgrounds that have bonus tool proficiencies.
    if oNPC.getMyBackground() in (
        "Criminal",
        "Entertainer",
        "Feylost",
        "Folk Hero",
        "Guild Artisan",
        "Noble",
        "Outlander",
        "Soldier",
        "Witchlight Hand",
    ):
        if oNPC.getMyBackground() == "Criminal":
            tool_options = [
                "Gaming set - Dice set",
                "Gaming set - Dragonchess set",
                "Gaming set - Playing card set",
                "Gaming set - Three-Dragon Ante set",
            ]
        elif oNPC.getMyBackground() == "Witchlight Hand":
            tool_options = oSRD.getListTools(oNPC.getMyTools(), "Musical instrument")
            tool_options.append("Disguise kit")
        elif oNPC.getMyBackground() in ("Entertainer", "Feylost", "Outlander"):
            tool_options = oSRD.getListTools(oNPC.getMyTools(), "Musical instrument")
        elif oNPC.getMyBackground() in (
            "Clan Crafter",
            "Folk Hero",
            "Guild Artisan",
        ):
            tool_options = oSRD.getListTools(oNPC.getMyTools(), "Artisan's tools")
        elif oNPC.getMyBackground() == "Noble":
            tool_options = [
                "Gaming set - Dice set",
                "Gaming set - Dragonchess set",
                "Gaming set - Playing card set",
                "Gaming set - Three-Dragon Ante set",
            ]
        else:
            tool_options = [
                "Gaming set - Dice set",
                "Gaming set - Dragonchess set",
                "Gaming set - Playing card set",
                "Gaming set - Three-Dragon Ante set",
            ]
        oSheet.set(
            "tools",
            Scan(
                message=f"Choose a '{oNPC.getMyBackground()}' background bonus tool proficiency.",
                selections=tool_options,
                completer=True,
            ),
        )


def assignCantrips(
    klass: str,
    cantrips_known: Union[int, None] = None,
    subklass: Union[str, None] = None,
) -> List[str]:
    """Selects character's cantrips."""
    if subklass is not None:
        subklass = oNPC.getClassSubclass(klass)

    my_cantrip_list = list()
    cantrip_pool = oSRD.getListCantrips(klass, subklass)
    if len(cantrip_pool) == 0:
        return my_cantrip_list

    if cantrips_known is None:
        cantrips_known = int(oNPC.getSpellSlots()[0])
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
        if not oNPC.canSubclass(klass):
            return

        subclass = Scan(
            message=f"What is your '{klass}' subclass?",
            selections=oSRD.getListSubclasses(klass),
            completer=True,
        )
        oSheet.classes[klass]["subclass"] = subclass
        base_subclass_traits = oSRD.getEntryBySubclass(subclass)
        oSheet.set(
            {
                "armors": base_subclass_traits["armors"],
                "tools": base_subclass_traits["tools"],
                "weapons": base_subclass_traits["weapons"],
                "features": oSRD.getFeaturesByClass(
                    subclass, oNPC.getClassLevel(klass)
                ),
            }
        )

    import dice

    for class_order, klass in enumerate(oNPC.getMyClasses()):
        if class_order == 0:
            traits = oSRD.getEntryByClass(klass)
            starting_gold = sum(
                dice.roll(
                    traits["gold"]
                )  # pyright: ignore[reportArgumentType, reportCallIssue]
            )

            oSheet.set(
                {
                    "allotted_skills": oNPC.getSkillTotal(),
                    "armors": traits["armors"],
                    "languages": traits["languages"],
                    "savingthrows": traits["savingthrows"],
                    "tools": traits["tools"],
                    "weapons": traits["weapons"],
                    "features": oSRD.getFeaturesByClass(
                        klass, oNPC.getClassLevel(klass)
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
        "spell_slots", oSRD.getSpellSlots(oNPC.getMyRawClasses(), oNPC.getTotalLevel())
    )


def assignClassSkills() -> None:
    """Prompt to determining the character's skills features."""
    for _ in range(0, oNPC.getAllottedSkills()):
        skill = Scan(
            message="Choose your class skill.",
            selections=oSRD.getClassSkills(oNPC.getMyClasses()[0], oNPC.getMySkills()),
            completer=True,
        )
        oSheet.set("skills", skill.capitalize())


def assignFeatEnhancements(feat: str) -> None:
    """Prompt assigns the proper enhancements by feat."""

    def getAdjustableAttributes(checked_attributes: List[str]) -> List[str]:
        """Checks the checked_attributes for upgradeable attributes."""
        adjustable_attributes = list()
        for attribute in checked_attributes:
            adjusted_score = oNPC.getAttributeScore(attribute) + 1
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

    base_attributes = Attributes(oNPC.getAttributes())

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
        "Dragon Fear",
        "Dragon Hide",
        "Elven Accuracy",
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

    # Artificer Initiate
    if feat == "Artificer Initiate":
        oSheet.set(
            {
                "features": assignCantrips("Artificer", 1),
                "tools": Scan(
                    message=f"Choose a '{oNPC.getMyBackground()}' background bonus tool proficiency.",
                    selections=oSRD.getListTools(oNPC.getMyTools(), "Artisan's tools"),
                    completer=True,
                ),
            }
        )

    # Dungeon Delver
    if feat == "Dungeon Delver":
        oSheet.set("resistances", "Traps")

    # Durable/Dwarven Fortitude
    if feat in ("Durable", "Dwarven Fortitude"):
        base_attributes.add("Constitution", 1)

    # Heavily Armored
    if feat == "Heavily Armored":
        base_attributes.add("Strength", 1)

    # Infernal Constitution
    if feat == "Infernal Constitution":
        base_attributes.add("Constitution", 1)
        oSheet.set(
            "resistances",
            [
                "Cold",
                "Poison",
            ],
        )

    # Mobile
    if feat == "Mobile":
        oSheet.set("speed", oNPC.getMySpeed() + 10)

    # Prodigy
    if feat == "Prodigy":
        oSheet.set(
            "languages",
            Scan(
                message="Choose a bonus language.",
                selections=oSRD.getStandardLanguages(oNPC.getMyLanguages()),
                completer=True,
            ),
        )
        oSheet.set(
            "skills",
            Scan(
                message="Choose a bonus skill.",
                selections=oSRD.getListSkills(oNPC.getMySkills()),
                completer=True,
            ),
        )
        oSheet.set(
            "tools",
            Scan(
                message="Choose a bonus skill.",
                selections=oSRD.getListTools(oNPC.getMyTools()),
                completer=True,
            ),
        )

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
                        selections=oSRD.getListSkills(oNPC.getMySkills()),
                        completer=True,
                    ),
                )
            elif bonus_option == "Tool":
                oSheet.set(
                    "tools",
                    Scan(
                        message="Choose a bonus tool proficiency.",
                        selections=oSRD.getListTools(oNPC.getMyTools()),
                        completer=True,
                    ),
                )

    # Squat Nimbleness
    if feat == "Squat Nimbleness":
        attribute_bonuses = ["Dexterity", "Strength"]
        attribute_bonus = Scan(
            message="Choose an attribute to upgrade.",
            selections=getAdjustableAttributes(attribute_bonuses),
            completer=True,
        )
        if attribute_bonus == "Dexterity":
            oSheet.set("skills", "Acrobatics")
        if attribute_bonus == "Strength":
            oSheet.set("skills", "Athletics")
        oSheet.set("speed", oNPC.getMySpeed() + 5)
        base_attributes.add(attribute_bonus, 1)

    # Telekinetic
    if feat == "Telekinetic":
        oSheet.set("features", "Mage Hand")

    # Telepathic
    if feat == "Telepathic":
        oSheet.set("features", "Detect Thoughts")

    # Weapon Master
    if feat == "Weapon Master":
        for _ in range(4):
            bonus_weapons = oSRD.getListWeapons(oNPC.getMyWeapons())
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

    def applyRacialBonus() -> None:
        """Applies racial bonuses."""
        base_values = oNPC.getAttributes()
        bonus_values = oNPC.getBonus()
        for attribute, _ in bonus_values.items():
            if attribute in bonus_values:
                base_attr = Attributes(base_values)
                base_attr.add(attribute, bonus_values[attribute])
        review_attributes()

    full_race = oNPC.getMyRace().split(", ")
    if len(full_race) > 1:
        race, subrace = full_race
    else:
        race, subrace = (oNPC.getMyRace(), "")

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
    assignTraitsHuman()
    assignBackgroundTraits()

    if subrace != "":
        traits = oSRD.getEntryByLineage(subrace)
        oSheet.set({"bonus": traits["bonus"], "traits": traits["traits"]})

    applyRacialBonus()

    from metrics import Anthropometry

    height, weight = Anthropometry(
        oSRD.getAnthropometryBase(race, subrace),
        oNPC.getMyGender(),
        oSRD.getAnthropometryDominantSex(oSRD.getAnthropometrySource(race, subrace)),
    ).calculate()
    oSheet.set(
        {
            "height": height,
            "weight": weight,
        }
    )


def assignSpellcastingFeatures() -> None:
    """Assigns character's spellcasting features, if applicable."""
    if not oNPC.isSpellcaster():
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

        for klass in oNPC.getMyClasses():
            allotted_spell_total = oSRD.getSpellTotal(
                klass,
                oNPC.getClassLevel(klass),
                get_modifier(
                    oNPC.getCasterAttribute(klass, oNPC.getClassSubclass(klass))
                ),
            )
            spell_selection_counter = allotted_spell_total

            spell_pool = oSRD.getListSpells(
                klass, oNPC.getClassSubclass(klass), oNPC.getClassLevel(klass)
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

    if len(oNPC.getSpellSlots()) == 0:
        return

    for klass in oNPC.getMyClasses():
        oSheet.set("cantrips", {klass: assignCantrips(klass)})

    assignSpells()


def assignTraitsDragonborn() -> None:
    """Assigns dragonborn features."""
    if "Dragonborn" not in oNPC.getMyRace():
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


def assignTraitsHuman() -> None:
    """Assigns human features."""
    if "Human" not in oNPC.getMyRace():
        return

    oSheet.set(
        "languages",
        Scan(
            message="Choose your racial bonus language.",
            selections=oSRD.getStandardLanguages(oNPC.getMyLanguages()),
            completer=True,
        ),
    )


def hasFeatRequirements(feat: str) -> Union[Literal[False], Literal[True]]:
    """Returns True if character meets feat prerequisites."""
    if feat in oNPC.getMyFeats():
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
        and "Monk" in oNPC.getMyClasses()
    ):
        return False

    if feat in (
        "Heavily Armored",
        "Lightly Armored",
        "Moderately Armored",
        "Weapon Master",
    ):
        if feat == "Heavily Armored" and "Heavy" in oNPC.getMyArmors():
            return False
        if feat == "Lightly Armored" and "Light" in oNPC.getMyArmors():
            return False
        if feat == "Moderately Armored" and "Medium" in oNPC.getMyArmors():
            return False
        if feat == "Weapon Master" and "Martial" in oNPC.getMyWeapons():
            return False

    feat_requirements = oSRD.getEntryByFeat(feat)
    for category, _ in feat_requirements.items():
        if feat_requirements[category] is None:
            continue

        if category == "attribute":
            for attribute, minimum_score in feat_requirements[category].items():
                if oNPC.getAttributeScore(attribute) < minimum_score:
                    return False

        if category == "caster":
            if not oNPC.isSpellcaster():
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
                for klass in oNPC.getMyClasses():
                    if klass in applicable_classes:
                        return True
                return False

            if feat == "Ritual Caster":
                if not oNPC.hasClass("Cleric") or not oNPC.hasClass("Wizard"):
                    return False

                if (
                    "Cleric" in oNPC.getMyClasses()
                    and oNPC.getAttributeScore("Wisdom")
                    < feat_requirements["ability"]["Wisdom"]
                ):
                    return False

                if (
                    "Wizard" in oNPC.getMyClasses()
                    and oNPC.getAttributeScore("Intelligence")
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

        # Check race/subrace requirements
        if category in ("race", "subrace"):
            race = oNPC.getMyRace().split(", ")
            if len(race) != 2:
                race = race[0]
                subrace = ""
            else:
                race = race[0]
                subrace = race[1]

            if category == "race" and race not in feat_requirements[category]:
                return False
            elif category == "subrace" and subrace not in feat_requirements[category]:
                return False

    return True


def isPreparedCaster(self) -> bool:
    """Returns True if character is a prepared spellcaster."""
    for klass in self.getMyClasses():
        if klass in ("Artificer", "Cleric", "Druid", "Paladin", "Wizard"):
            return True
    return False


def step1():
    # Choose class
    # Select level
    step_one_complete = False
    while not step_one_complete:
        klass = utility.stdin("What class are you?", oSRD.getClasses())
        level = input("What is your level? ")
        print(klass, level)
        step_one_complete = True


def step2():
    # Choose a background
    # Choose a species
    step_two_complete = False
    while not step_two_complete:
        background = utility.stdin("What is your background?", oSRD.getBackgrounds())
        # Choose ability bonuses, 1 feat, two skills and one tool proficiency
        ability_scores = input("Choose background ability bonus array.")
        # 2/1
        # 1/1/1s
        feat = utility.stdin(
            "Choose a feat from your background. ", oSRD.getFeatsByCategory("Origin")
        )
        skills = utility.stdin(
            "Choose two skills from your background.",
            oSRD.getSkillsByBackground(background[0]),
            loop_count=2,
        )
        tool = input("Choose a tool proficiency from your background. ")
        # Choose equipment
        species = utility.stdin("What is your species?", oSRD.getSpecies())
        language = utility.stdin(
            "Choose three languages.", oSRD.getStandardLanguages(), loop_count=3
        )
        print(background, species, skills, language)
        step_two_complete = True


def step3():
    # Generate/Assign ability scores
    pass


def step5():
    gender = utility.stdin("What is your gender", ["", ""])


def main() -> None:
    step1()
    step2()
    step3()


if __name__ == "__main__":
    main()
