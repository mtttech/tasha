from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Tuple, Union

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator, ValidationError
import toml

from actor import CharacterSheet, NonPlayerCharacter
from attributes import Attributes, Score, generate_attributes, get_modifier
from system import SystemResourceDocument

oSheet = CharacterSheet()
oPC = NonPlayerCharacter(oSheet)
oSRD = SystemResourceDocument()
stylesheet = Style.from_dict(
    {
        "attribute": "#fff bold",
        "bottom-toolbar": "#d8dee9 bg:#000",
        "command": "#ffff00 bold",
        "error": "#880000 bold",
        "info": "#32cd32 bold",
        "number": "#32cd00",
        "prompt": "#aaa bold",
        "title": "#88cccc bold",
        "warn": "#ffea00 bold",
    }
)


def text_color_router(message: str, message_level: int) -> None:
    color_routes = {
        0: [("class:info", message)],
        1: [("class:error", message)],
        2: [("class:warn", message)],
    }
    print_formatted_text(FormattedText(color_routes[message_level]), style=stylesheet)


def error(message: str) -> None:
    text_color_router(message, 1)


def info(message: str) -> None:
    text_color_router(message, 0)


def warn(message: str) -> None:
    text_color_router(message, 2)


try:
    pyproject_file = Path(__file__).parents[0] / "pyproject.toml"
    with pyproject_file.open("r") as pyproject:
        try:
            __version__ = toml.load(pyproject)["project"]["version"]
        except KeyError:
            error(f"cannot detect my version number.")
            exit(1)
except FileNotFoundError:
    error("cannot locate 'pyproject.toml'.")
    exit(1)

character_dir = Path.home() / ".config" / "tasha" / "characters"
if not character_dir.exists():
    character_dir.mkdir(parents=True)
    warn(f"'{character_dir}' not found. Directory created.")


class TashaCommandError(Exception):
    pass


class TashaPrompt:
    def __init__(self, session: PromptSession) -> None:
        self.session = session

    def select(
        self,
        message: Union[str, Literal[None]] = None,
        selections: Union[Iterable[Any], Literal[None]] = None,
    ) -> str:
        if message is not None:
            prompt_prefix = FormattedText([("class:prompt", f">> {message} ")])
        else:
            prompt_prefix = FormattedText([("class:prompt", ">> ")])

        if selections is None:
            response = self.session.prompt(
                prompt_prefix,
                style=stylesheet,
            )
        else:
            response = self.session.prompt(
                prompt_prefix,
                completer=NestedCompleter.from_nested_dict(
                    populate_completer(selections)
                ),
                style=stylesheet,
                validator=TashaValidator(selections),
            )

        return capitalize(response)


class TashaValidator(Validator):
    def __init__(self, allowed_options: Iterable[Any]) -> None:
        super().__init__()
        self.allowed_options = [o.lower() for o in allowed_options]

    def validate(self, document):
        if document.text not in self.allowed_options:
            raise ValidationError(
                message=f"option not found.",
                cursor_position=0,
            )


def tasha_main(command: str) -> None:
    """Tasha program gateway."""
    if len(command) == 0:
        tasha_cmd_help()

    args = command.split(" ")
    if len(args) > 3:
        args[2] = " ".join(args[2:])
        del args[3:]

    action = args[0]
    if len(args) == 3:
        parameter = args[1]
        value = capitalize(args[2])
        if action == "add":
            if not oPC.hasAttributes():
                raise TashaCommandError(
                    "the add action requires you to run the roll action first!"
                )
            tasha_cmd_add(value)

        if action == "set":
            tasha_cmd_set(parameter, value)

    if len(args) == 2:
        if action == "roll":
            if not args[1].isnumeric():
                raise TashaCommandError(
                    "the roll action threshold requires a numeric value."
                )
            tasha_cmd_roll(int(args[1]))

    if len(args) == 1:
        if action == "help":
            tasha_cmd_help()
        if action == "quit":
            raise KeyboardInterrupt("thank you for using tasha!")
        if action == "save":
            tasha_cmd_save()


def tasha_cmd_add(value: str) -> None:
    """Performs the add action."""
    if value not in oSRD.getListClasses():
        raise TashaCommandError("the add class action requires a valid class.")

    if oPC.hasClasses() and value not in oSRD.getListMulticlasses(
        oPC.getMyClasses(),
        oPC.getTotalLevel(),
        oPC.getAttributes(),
    ):
        raise TashaCommandError(f"you don't meet the requirements to multiclass.")

    level_allowance = 20
    level_allowance = level_allowance - oPC.getTotalLevel()
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


def tasha_cmd_help() -> None:
    """Performs the help action."""
    help_text = [
        ("", "\n"),
        ("class:title", f"tasha {__version__}"),
        ("", "\n\n\t"),
        (
            "",
            "A program for creating 5th edition Dungeons & Dragons characters.",
        ),
        ("", "\n\n"),
        ("class:title", "Command Help:"),
        ("", "\n\n\t"),
        (
            "class:command",
            "add (class) [value]: ",
        ),
        ("", "Sets character class(es)."),
        ("", "\n\t"),
        ("class:command", "roll [threshold]: "),
        (
            "",
            "Roll up a character - sets attributes|race|subrace|gender|background.",
        ),
        ("", "\n\t"),
        (
            "class:command",
            "set (alignment|name) [value]: ",
        ),
        ("", "Sets character values."),
        ("", "\n\t"),
        (
            "class:command",
            "save: ",
        ),
        ("", "Finalizes and saves the character."),
        ("", "\n\t"),
        ("class:command", "quit: "),
        ("", "Exits the program."),
        ("", "\n"),
    ]
    print_formatted_text(FormattedText(help_text), style=stylesheet)


def tasha_cmd_roll(threshold: int) -> None:
    """Performs the roll action."""
    if not threshold in range(60, 91):
        raise TashaCommandError(
            "the roll action threshold value must be between 60-90."
        )

    if len(oSheet.classes) > 0:
        oSheet.bonus = dict()
        oSheet.classes = dict()
        oSheet.gender = ""
        oSheet.languages = list()
        oSheet.race = ""
        oSheet.size = "Medium"
        oSheet.skills = list()
        oSheet.traits = list()
        oSheet.weapons = list()
        raise TashaCommandError("the roll action has been previously run.")

    oSheet.set("attributes", assignAttributeValues(generate_attributes(threshold)))
    review_attributes()

    race = Scan(
        message="What is your race?",
        selections=oSRD.getListRaces(),
        completer=True,
    )
    subrace_options = oSRD.getListSubraces(race)
    if len(subrace_options) == 0:
        oSheet.set("race", race)
    else:
        subrace = Scan(
            message=f"What is your {race} subrace?",
            selections=subrace_options,
            completer=True,
        )
        oSheet.set("race", f"{race}, {subrace}")

    oSheet.set(
        "gender",
        Scan(
            message="What is your gender?",
            selections=["Female", "Male"],
            completer=True,
        ),
    )
    assignRacialTraits()


def tasha_cmd_save() -> None:
    """Performs the save action."""
    if oPC.getMyName() == "":
        raise TashaCommandError(
            "cannot run save action because you haven't set a name."
        )

    if oPC.getMyAlignment() == "":
        raise TashaCommandError(
            "cannot run save action because you haven't set an alignment."
        )

    if not oPC.hasClasses():
        raise TashaCommandError(
            "cannot run save action because you don't have at least one class."
        )

    oSheet.set(
        {
            "allotted_asi": oSRD.calculateAllottedAsi(oPC.getMyRawClasses()),
            "traits": oSRD.getRacialMagic(oPC.getMyRace(), oPC.getTotalLevel()),
            "version": __version__,
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
        info("Character created successfully.")
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
    gender = oPC.getMyGender()
    if gender == "Female":
        gender = ""
    elif gender == "Male":
        gender = ""
    else:
        gender = ""

    if len(oPC.getAttributes()) > 0:
        attribute_string = list()
        for a, v in oPC.getAttributes().items():
            attribute_string.append("{}: {}".format(a[0:3], v["score"]))
        attribute_string = " ".join(attribute_string)
        attributes = f"  {attribute_string}"
    else:
        attributes = ""

    return [
        (
            "class:bottom-toolbar",
            f" tasha {__version__} - Type 'help' for assistance :: "
            f"{oPC.getMyName()} "
            f"{gender} {oPC.getMyRace()} "
            f"{'/'.join(oPC.getMyClasses())} "
            f"{attributes} ",
        )
    ]


def capitalize(string: Union[List[str], str]) -> str:
    """Capitalize the first letter of all words with the exception of certain words."""
    if isinstance(string, str):
        string = string.split(" ")

    if string[0] == "the":
        string[0] = string[0].capitalize()

    return " ".join(
        [
            (
                w.capitalize()
                if w not in ("and", "of", "or", "the", "to", "via", "with")
                else w
            )
            for w in string
        ]
    )


def populate_completer(options: Iterable[Any]) -> Dict[str, Any]:
    """Returns a dictionary of applicable selections for the NestedCompleter."""
    options = [o.lower() for o in options if isinstance(o, str)]
    filler = [None for _ in options]
    return dict(zip(options, filler))


def review_attributes() -> None:
    """Prints out all attributes (attribue/score/modifier)."""
    for attribute in tuple(oPC.getAttributes().keys()):
        info(
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
                selections=oSRD.getListFeats(oPC.getMyFeats() + excluded_feats),
                completer=True,
            )
            if hasFeatRequirements(feat):
                assignFeatEnhancements(feat)
                break
            else:
                excluded_feats.append(feat)
                warn(f"You don't meet the requirements for '{feat}'.")

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
            selections=oSRD.getListBackground(),
            completer=True,
        ),
    )

    background_traits = oSRD.getEntryByBackground(oPC.getMyBackground())
    oSheet.set(
        {
            "equipment": background_traits["equipment"],
            "gold": background_traits["gold"],
            "skills": background_traits["skills"],
            "tools": background_traits["tools"],
        }
    )

    # Backgrounds that have a bonus language(s).
    if oPC.getMyBackground() in (
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
            oPC.getMyBackground() == "Clan Crafter"
            and "Dwarvish" not in oPC.getMyLanguages()
        ):
            oSheet.set("languages", "Dwarvish")
        else:
            number_of_languages = (
                2
                if oPC.getMyBackground()
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
            if oPC.getMyBackground() != "Feylost":
                bonus_languages = oSRD.getListLanguages(oPC.getMyLanguages())
            else:
                bonus_languages = ("Elvish", "Gnomish", "Goblin", "Sylvan")
                bonus_languages = [
                    l for l in bonus_languages if l not in oPC.getMyLanguages()
                ]
            for _ in range(number_of_languages):
                language = Scan(
                    message=f"Choose a '{oPC.getMyBackground()}' background bonus language.",
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
    if oPC.getMyBackground() in (
        "Cloistered Scholar",
        "Faction Agent",
    ):
        bonus_skills = []
        if oPC.getMyBackground() == "Cloistered Scholar":
            bonus_skills = ["Arcana", "Nature", "Religion"]
        elif oPC.getMyBackground() == "Faction Agent":
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
                message=f"Choose a '{oPC.getMyBackground()}' background bonus skill.",
                selections=[s for s in bonus_skills if s not in oPC.getMySkills()],
                completer=True,
            ),
        )

    # Backgrounds that have bonus tool proficiencies.
    if oPC.getMyBackground() in (
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
        if oPC.getMyBackground() == "Criminal":
            tool_options = [
                "Gaming set - Dice set",
                "Gaming set - Dragonchess set",
                "Gaming set - Playing card set",
                "Gaming set - Three-Dragon Ante set",
            ]
        elif oPC.getMyBackground() == "Witchlight Hand":
            tool_options = oSRD.getListTools(oPC.getMyTools(), "Musical instrument")
            tool_options.append("Disguise kit")
        elif oPC.getMyBackground() in ("Entertainer", "Feylost", "Outlander"):
            tool_options = oSRD.getListTools(oPC.getMyTools(), "Musical instrument")
        elif oPC.getMyBackground() in (
            "Clan Crafter",
            "Folk Hero",
            "Guild Artisan",
        ):
            tool_options = oSRD.getListTools(oPC.getMyTools(), "Artisan's tools")
        elif oPC.getMyBackground() == "Noble":
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
                message=f"Choose a '{oPC.getMyBackground()}' background bonus tool proficiency.",
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
            selections=oSRD.getClassSkills(oPC.getMyClasses()[0], oPC.getMySkills()),
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
                    message=f"Choose a '{oPC.getMyBackground()}' background bonus tool proficiency.",
                    selections=oSRD.getListTools(oPC.getMyTools(), "Artisan's tools"),
                    completer=True,
                ),
            }
        )

    # Dungeon Delver
    if feat == "Dungeon Delver":
        oSheet.set("resistances", "Traps")

    # Drow High Magic/Svirfneblin Magic/Wood Elf Magic
    if feat in ("Drow High Magic", "Svirfneblin Magic", "Wood Elf Magic"):
        if feat == "Drow High Magic":
            oSheet.set(
                "features",
                [
                    "Detect Magic",
                    "Dispel Magic",
                    "Levitate",
                ],
            )
        elif feat == "Svirfneblin Magic":
            oSheet.set(
                "features",
                [
                    "Blindness/Deafness",
                    "Blur",
                    "Disguise",
                    "Nondetection",
                ],
            )
        elif feat == "Wood Elf Magic":
            oSheet.set("features", assignCantrips("Druid", 1))
            oSheet.set(
                "features",
                [
                    "Longstrider",
                    "Pass Without Trace",
                ],
            )

    # Durable/Dwarven Fortitude
    if feat in ("Durable", "Dwarven Fortitude"):
        base_attributes.add("Constitution", 1)

    # Fey Teleportation
    if feat == "Fey Teleportation":
        oSheet.set({"languages": "Sylvan", "features": "Misty Step"})

    # Fey Touched
    if feat == "Fey Touched":
        oSheet.set("features", "Misty Step")

    # Gunner
    if feat == "Gunner":
        base_attributes.add("Dexterity", 1)
        oSheet.set("weapons", "Firearms")

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

    # Linguist
    if feat == "Linguist":
        base_attributes.add("Intelligence", 1)
        for _ in range(3):
            oSheet.set(
                "languages",
                Scan(
                    message="Choose a bonus language.",
                    selections=oSRD.getListLanguages(oPC.getMyLanguages()),
                    completer=True,
                ),
            )

    # Mobile
    if feat == "Mobile":
        oSheet.set("speed", oPC.getMySpeed() + 10)

    # Prodigy
    if feat == "Prodigy":
        oSheet.set(
            "languages",
            Scan(
                message="Choose a bonus language.",
                selections=oSRD.getListLanguages(oPC.getMyLanguages()),
                completer=True,
            ),
        )
        oSheet.set(
            "skills",
            Scan(
                message="Choose a bonus skill.",
                selections=oSRD.getListSkills(oPC.getMySkills()),
                completer=True,
            ),
        )
        oSheet.set(
            "tools",
            Scan(
                message="Choose a bonus skill.",
                selections=oSRD.getListTools(oPC.getMyTools()),
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

    # Shadow Touched
    if feat == "Shadow Touched":
        oSheet.set("features", "Invisibility")
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
                        selections=oSRD.getListTools(oPC.getMyTools()),
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
        oSheet.set("speed", oPC.getMySpeed() + 5)
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

    def applyRacialBonus() -> None:
        """Applies racial bonuses."""
        base_values = oPC.getAttributes()
        bonus_values = oPC.getBonus()
        for attribute, _ in bonus_values.items():
            if attribute in bonus_values:
                base_attr = Attributes(base_values)
                base_attr.add(attribute, bonus_values[attribute])
        review_attributes()

    full_race = oPC.getMyRace().split(", ")
    if len(full_race) > 1:
        race, subrace = full_race
    else:
        race, subrace = (oPC.getMyRace(), "")

    traits = oSRD.getEntryByRace(race)
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
    assignTraitsHobgoblin()
    assignTraitsHalfelf()
    assignTraitsHuman()
    assignTraitsKenku()
    assignTraitsLizardfolk()
    assignTraitsTabaxi()
    assignTraitsWitchlight()
    assignBackgroundTraits()

    if subrace != "":
        traits = oSRD.getEntryBySubrace(subrace)
        oSheet.set({"bonus": traits["bonus"], "traits": traits["traits"]})

    applyRacialBonus()

    from metrics import Anthropometry

    height, weight = Anthropometry(
        oSRD.getAnthropometryBase(race, subrace),
        oPC.getMyGender(),
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
    if "Dragonborn" not in oPC.getMyRace():
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


def assignTraitsHalfelf() -> None:
    """Assigns half-elf features."""
    if "Halfelf" not in oPC.getMyRace():
        return

    attribute_bonuses = [
        "Strength",
        "Dexterity",
        "Constitution",
        "Intelligence",
        "Wisdom",
    ]
    attribute = Scan(
        message="Choose your racial bonus attribute.",
        selections=attribute_bonuses,
        completer=True,
    )
    Attributes(oPC.getAttributes()).add(attribute, 1)
    oSheet.set("bonus", {attribute: 1})

    oSheet.set(
        "languages",
        Scan(
            message="Choose your racial bonus language.",
            selections=oSRD.getListLanguages(oPC.getMyLanguages()),
            completer=True,
        ),
    )

    for _ in range(2):
        oSheet.set(
            "skills",
            Scan(
                message="Choose your racial bonus skill.",
                selections=oSRD.getListSkills(oPC.getMySkills()),
                completer=True,
            ),
        )


def assignTraitsHobgoblin() -> None:
    """Assigns hobgoblin features."""
    if "Hobgoblin" not in oPC.getMyRace():
        return

    for _ in range(2):
        hobgoblin_weapons = [
            "Battleaxe",
            "Blowgun",
            "Flail",
            "Greataxe",
            "Greatsword",
            "Halberd",
            "Hand Crossbow",
            "Heavy Crossbow",
            "Lance",
            "Longbow",
            "Longsword",
            "Maul",
            "Morningstar",
            "Net",
            "Pike",
            "Rapier",
            "Scimitar",
            "Shortsword",
            "Trident",
            "War pick",
            "Warhammer",
            "Whip",
        ]
        oSheet.set(
            "weapons",
            Scan(
                message="Choose your racial bonus weapon proficiency.",
                selections=[
                    w for w in hobgoblin_weapons if w not in oPC.getMyWeapons()
                ],
                completer=True,
            ),
        )


def assignTraitsHuman() -> None:
    """Assigns human features."""
    if "Human" not in oPC.getMyRace():
        return

    oSheet.set(
        "languages",
        Scan(
            message="Choose your racial bonus language.",
            selections=oSRD.getListLanguages(oPC.getMyLanguages()),
            completer=True,
        ),
    )


def assignTraitsKenku() -> None:
    """Assigns kenku features."""
    if "Kenku" not in oPC.getMyRace():
        return

    for _ in range(2):
        kenku_skills = [
            "Acrobatics",
            "Deception",
            "Stealth",
            "Sleight of Hand",
        ]
        oSheet.set(
            "skills",
            Scan(
                message="Choose your racial bonus skill.",
                selections=[s for s in kenku_skills if s not in oPC.getMySkills()],
                completer=True,
            ),
        )


def assignTraitsLizardfolk() -> None:
    """Assigns lizardfolk features."""
    if "Lizardfolk" not in oPC.getMyRace():
        return

    for _ in range(2):
        lizardfolk_skills = [
            "Animal Handling",
            "Nature",
            "Perception",
            "Stealth",
            "Survival",
        ]
        oSheet.set(
            "skills",
            Scan(
                message="Choose your racial bonus skill.",
                selections=[s for s in lizardfolk_skills if s not in oPC.getMySkills()],
                completer=True,
            ),
        )


def assignTraitsTabaxi() -> None:
    """Assigns tabaxi features."""
    if "Tabaxi" not in oPC.getMyRace():
        return

    oSheet.set(
        "languages",
        Scan(
            message="Choose your racial bonus language.",
            selections=oSRD.getListLanguages(oPC.getMyLanguages()),
            completer=True,
        ),
    )


def assignTraitsWitchlight() -> None:
    """Assigns fairy or harengon features."""
    if "Fairy" not in oPC.getMyRace() or "Harengon" not in oPC.getMyRace():
        return

    base = Attributes(oPC.getAttributes())
    bonus_values = [2, 1]
    bonus_attributes = [
        "Strength",
        "Dexterity",
        "Constitution",
        "Intelligence",
        "Wisdom",
        "Charisma",
    ]
    for bonus in bonus_values:
        attribute = Scan(
            message="Choose your racial bonus attribute.",
            selections=bonus_attributes,
            completer=True,
        )
        bonus_attributes.remove(attribute)
        base.add(attribute, bonus)
        oSheet.set("bonus", {attribute: bonus})

    oSheet.set(
        "languages",
        Scan(
            message="Choose your racial bonus language.",
            selections=oSRD.getListLanguages(oPC.getMyLanguages()),
            completer=True,
        ),
    )


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

        if category == "attribute":
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

        # Check race/subrace requirements
        if category in ("race", "subrace"):
            race = oPC.getMyRace().split(", ")
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


def Scan(**args) -> str:
    """Captures/filters user input sends to Tasha prompt."""
    if "completer" not in args:
        args["completer"] = None

    if args["completer"] == True:
        args["completer"] = NestedCompleter.from_nested_dict(
            populate_completer(args["selections"])
        )

    if "main_menu" in args and args["main_menu"] == True:
        args["completer"] = NestedCompleter.from_nested_dict(
            {
                "add": {
                    "class": populate_completer(oSRD.getListClasses()),
                },
                "help": None,
                "quit": None,
                "roll": None,
                "save": None,
                "set": {
                    "alignment": populate_completer(oSRD.getListAlignments()),
                    "name": None,
                },
            }
        )

    session = PromptSession(
        bottom_toolbar=tasha_toolbar,
        completer=None if args["completer"] is None else args["completer"],
        style=stylesheet,
    )
    prompt = TashaPrompt(session)
    message = None if "message" not in args else args["message"]

    if "selections" in args and isinstance(args["selections"], list):
        return prompt.select(message, args["selections"])

    return prompt.select(message)


def main() -> None:
    while True:
        try:
            command = Scan(main_menu=True)
            tasha_main(command.lower())
        except TashaCommandError as e:
            warn(e.__str__())
            pass
        except KeyboardInterrupt as e:
            error(e.__str__())
            exit(1)


if __name__ == "__main__":
    main()
