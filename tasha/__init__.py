from dataclasses import asdict, replace
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Tuple, Union

from prompt_toolkit import PromptSession, print_formatted_text
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.styles import Style
from prompt_toolkit.validation import Validator, ValidationError
import toml

from tasha.attributes import Attributes, Score, generate_attributes, get_modifier
from tasha.pcutils import Character, PlayerUtils
from tasha.srdutils import SRDUtils

oSheet = Character()
oPC = PlayerUtils(oSheet)
oSRD = SRDUtils()
stylesheet = Style.from_dict(
    {
        "attribute": "#fff bold",
        "bottom-toolbar": "#d8dee9 bg:#000",
        "command": "#ffff00 bold",
        "error": "#880000 bold",
        "number": "#32cd00",
        "prompt": "#aaa bold",
        "success": "#32cd32 bold",
        "title": "#88cccc bold",
    }
)


try:
    pyproject_file = Path(__file__).parents[1] / "pyproject.toml"
    with pyproject_file.open("r") as pyproject:
        try:
            __version__ = toml.load(pyproject)["tool"]["poetry"]["version"]
        except KeyError:
            print(
                "There was an error detecting the {} version number.".format(
                    __package__
                )
            )
            exit(1)
except FileNotFoundError:
    print("Cannot locate the required 'pyproject.toml' file.")
    exit(1)

character_dir = Path("~/.config/{}".format(__package__)).expanduser() / "characters"
if not character_dir.exists():
    character_dir.mkdir(parents=True)


class TashaCmdError(Exception):
    pass


class TashaParserError(Exception):
    pass


class TashaCmd:
    def __init__(self, *args) -> None:
        self.args = args

    @staticmethod
    def _is_action(action: str) -> bool:
        if action not in (
            "add",
            "help",
            "quit",
            "roll",
            "save",
            "set",
        ):
            return False
        return True

    @staticmethod
    def _is_parameter(action: str, parameter: str) -> bool:
        if action == "add" and parameter not in ("class",):
            return False
        elif action == "set" and parameter not in (
            "alignment",
            "name",
        ):
            return False
        return True

    def run(self) -> None:
        def is_complete() -> bool:
            """Returns True if character is completed, False otherwise."""
            try:
                if oPC.getMyAlignment() == "":
                    raise ValueError("An alignment value has not been set.")
                elif oPC.getMyName() == "":
                    raise ValueError("A name value has not been set.")
                elif not oPC.hasClasses():
                    raise ValueError("A class value has not been set.")
            except ValueError as e:
                error(e.__str__())
                return False
            return True

        action = self.args[0]
        if not self._is_action(action):
            raise TashaCmdError(f"Invalid action '{action}' requested.")

        if len(self.args) == 3:
            parameter = self.args[1]
            value = capitalize(self.args[2])

            if action in (
                "add",
                "set",
            ) and not self._is_parameter(action, parameter):
                raise TashaCmdError(f"Invalid action '{action}' parameter.")

            # Action: add
            if action == "add":
                if parameter == "class":
                    if not oPC.hasAttributes():
                        raise TashaCmdError("You must generate your attributes first!")
                    if value not in oSRD.getListClasses():
                        raise ValueError(f"Invalid class '{value}' specified.")
                    if oPC.hasClasses() and value not in oSRD.getListMulticlasses(
                        oPC.getMyClasses(),
                        oPC.getTotalLevel(),
                        oPC.getAttributes(),
                    ):
                        raise TashaCmdError(
                            f"You don't meet the requirements to multiclass to a '{value}'!"
                        )
                    level_allowance = 20
                    level_allowance = level_allowance - oPC.getTotalLevel()
                    if level_allowance == 0:
                        raise TashaCmdError("You cannot select anymore classes.")

                    level = int(
                        read(
                            f"What is your '{value}' level (1-{level_allowance})?",
                            [str(_) for _ in list(range(1, level_allowance + 1))],
                        )
                    )
                    oSheet.classes[value] = {}
                    oSheet.classes[value]["hit_die"] = oSRD.getHitDieByClass(value)
                    oSheet.classes[value]["level"] = level
                    oSheet.classes[value]["subclass"] = ""

            # Action: set
            if action == "set":
                if parameter in (
                    "alignment",
                    "name",
                ):
                    if (
                        parameter == "alignment"
                        and value not in oSRD.getListAlignments()
                    ):
                        raise TashaCmdError(f"Invalid alignment '{value}' specified.")
                    oSheet.set(parameter, value)
                elif parameter == "race":
                    if value not in oSRD.getListRaces():
                        raise ValueError(f"Invalid race '{value}' specified.")
                    subrace_options = oSRD.getListSubraces(value)
                    if len(subrace_options) == 0:
                        oSheet.set(parameter, value)
                    else:
                        subrace = read(
                            f"What is your {value} subrace?",
                            subrace_options,
                        )
                        oSheet.set(parameter, "{}, {}".format(value, subrace))

                    gender = read(
                        "What is your gender?",
                        ("Female", "Male"),
                    )
                    oSheet.set("gender", gender)
                    assignRacialTraits()
        elif len(self.args) == 2:
            value = int(self.args[1])

            if action == "roll" and not isinstance(value, int):
                raise TashaCmdError("This action roll parameter requires an int value.")

            # Action: roll
            elif action == "roll":
                results = assignAttributeValues(generate_attributes(value))
                oSheet.set("attributes", results)
                review_attributes()

                race = read(
                    f"What is your race?",
                    oSRD.getListRaces(),
                )
                subrace_options = oSRD.getListSubraces(race)
                if len(subrace_options) == 0:
                    oSheet.set("race", race)
                else:
                    subrace = read(
                        f"What is your {race} subrace?",
                        subrace_options,
                    )
                    oSheet.set("race", "{}, {}".format(race, subrace))

                gender = read(
                    "What is your gender?",
                    ("Female", "Male"),
                )
                oSheet.set("gender", gender)
                assignRacialTraits()
        elif len(self.args) == 1:
            # Action: help
            if action == "help":
                help_text = [
                    ("", "\n"),
                    ("class:title", "{} {}".format(__package__, __version__)),
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
                echo(help_text)
            # Action: quit
            if action == "quit":
                raise KeyboardInterrupt(
                    f"Exited program. Thanks for using {__package__}!"
                )
            # Action: save
            if action == "save":
                if not is_complete():
                    raise TashaCmdError("You must complete your character first!")
                oSheet.set(
                    {
                        "allotted_asi": oSRD.calculateAllottedAsi(
                            oPC.getMyRawClasses()
                        ),
                        "traits": oSRD.getRacialMagic(
                            oPC.getMyRace(), oPC.getTotalLevel()
                        ),
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

                with Path(character_dir, "{}.toml".format(oPC.getMyName())).open(
                    "w"
                ) as record_sheet:
                    toml.dump(asdict(cs), record_sheet)
                    echo(
                        [
                            (
                                "class:success",
                                "Character created successfully.",
                            ),
                        ],
                    )
                    oSheet.reset()
        else:
            raise TashaCmdError("Unrecognized command string specified.")


class TashaParser:
    def __init__(self, command_str: str) -> None:
        self.command_str = command_str

    def run(self) -> List[str]:
        if len(self.command_str) == 0:
            raise TashaParserError("Empty command string specified.")
        command_list = self.command_str.split(" ")
        # Has more than three items, merge the excess values with the third slice.
        if len(command_list) > 3:
            command_list[2] = " ".join(command_list[2:])
            del command_list[3:]
        return command_list


class TashaPrompt:
    def __init__(self, session: PromptSession) -> None:
        self.session = session

    def select(
        self, message: str, selections: Union[List[str], Tuple[str, ...]]
    ) -> str:
        return capitalize(
            self.session.prompt(
                [("class:prompt", f"> {message} ")],
                completer=NestedCompleter.from_nested_dict(
                    populate_completer(selections)
                ),
                style=stylesheet,
                validator=TashaValidator(selections),
            )
        )


class TashaValidator(Validator):
    def __init__(self, allowed_options: Union[List[str], Tuple[str, ...]]) -> None:
        super().__init__()
        self.allowed_options = [o.lower() for o in allowed_options]

    def validate(self, document):
        if (user_input := document.text) not in self.allowed_options:
            raise ValidationError(
                message=f"This option value '{user_input}' is invalid.",
                cursor_position=0,
            )


def bottom_toolbar() -> List[Tuple[str, ...]]:
    """Returns the prompt_toolkit bottom toolbar."""
    gender = oPC.getMyGender()
    if gender == "Female":
        gender = ""
    elif gender == "Male":
        gender = ""
    else:
        gender = ""

    if len(oPC.getAttributes()) > 0:
        attributes = ""
    else:
        attributes = ""

    return [
        (
            "class:bottom-toolbar",
            f" {__package__} {__version__} - Type 'help' for assistance :: "
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


def echo(text: Iterable) -> None:
    """Wrapper for prompt_toolkit print_formatted_text function."""
    print_formatted_text(FormattedText(text), style=stylesheet)


def error(message: str) -> None:
    """Prints formatted error message."""
    echo([("class:error", message)])


def populate_completer(options: Union[List[str], Tuple[str, ...]]) -> Dict[str, Any]:
    """Returns a dictionary of applicable selections."""
    options = [o.lower() for o in options if isinstance(o, str)]
    filler = [None for _ in options]
    return dict(zip(options, filler))


def read(message: str, selections: Union[List[str], Tuple[str, ...]]) -> str:
    """Captures user input."""
    prompt = TashaPrompt(PromptSession(bottom_toolbar=bottom_toolbar))
    return prompt.select(message, selections)


def review_attributes() -> None:
    for attribute in tuple(oPC.getAttributes().keys()):
        echo(
            [
                ("class:attribute", f"{attribute[0:3].upper()}: "),
                (
                    "class:number",
                    "{} ({})".format(
                        oPC.getAttributeScore(attribute),
                        oPC.getAttributeModifier(attribute),
                    ),
                ),
            ],
        )


def assignAsiUpgrades() -> None:
    """Assigns abilit1y score improvement upgrades."""
    allotted_asi = oPC.getAllottedAsi()
    if allotted_asi == 0:
        return

    def assignAttributeUpgrade() -> None:
        bonus = int(read("How many points do you wish to apply?", ["1", "2"]))
        bonus_attributes = list()
        if bonus == 1:
            num_of_bonuses = 2
        else:
            num_of_bonuses = 1
        for _ in range(0, num_of_bonuses):
            attribute = read(
                "Which attribute do you wish to enhance?",
                [
                    a
                    for a in oPC.getUpgradeableAttributes(bonus)
                    if a not in bonus_attributes
                ],
            )
            bonus_attributes.append(attribute)
            base = Attributes(oPC.getAttributes())
            base.add(attribute, bonus)
            oSheet.attributes = base.attributes

    def assignFeatUpgrade() -> None:
        excluded_feats = list()
        while True:
            feat = read(
                "Choose a feat.", oSRD.getListFeats(oPC.getMyFeats() + excluded_feats)
            )
            if hasFeatRequirements(feat):
                assignFeatEnhancements(feat)
                break
            else:
                excluded_feats.append(feat)
                error(f"You don't meet the requirements for '{feat}'.")

    asi_counter = allotted_asi
    for _ in range(0, allotted_asi):
        option = read(
            f"Would you like to select a feat or increase an ability? ({asi_counter})",
            [
                "ability",
                "feat",
            ],
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
        else:
            attribute = read(
                "Assign {} ({}) to which attribute?".format(
                    results[0], ", ".join([str(d) for d in results])
                ),
                attribute_options,
            )
            setAttributeValue(attribute, results[0])
    return setAttributeOrder(attribute_array)


def assignBackgroundTraits() -> None:
    """Subroutine for determining the character's background features."""
    oSheet.set(
        "background",
        read(
            f"What is your background?",
            oSRD.getListBackground(),
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
                language = read(
                    "Choose a '{}' background bonus language.".format(
                        oPC.getMyBackground()
                    ),
                    bonus_languages,
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
        bonus_skills = [s for s in bonus_skills if s not in oPC.getMySkills()]
        oSheet.set(
            "skills",
            read(
                "Choose a '{}' background bonus skill.".format(oPC.getMyBackground()),
                bonus_skills,
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
            read(
                "Choose a '{}' background bonus tool proficiency.".format(
                    oPC.getMyBackground()
                ),
                tool_options,
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
        cantrip = read(
            f"Choose a cantrip ({cantrip_selection_counter}).",
            cantrip_pool,
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
        """Assigns subclass features."""
        if not oPC.canSubclass(klass):
            return

        subclass = read(
            f"What is your '{klass}' subclass?",
            oSRD.getListSubclasses(klass),
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
            starting_gold = sum(dice.roll(traits["gold"]))

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
    """Subroutine for determining the character's skills features."""
    for _ in range(0, oPC.getAllottedSkills()):
        skill = read(
            "Choose your class skill.",
            oSRD.getClassSkills(oPC.getMyClasses()[0], oPC.getMySkills()),
        )
        oSheet.set("skills", skill.capitalize())


def assignFeatEnhancements(feat: str) -> None:
    """Assigns the proper enhancements by feat."""

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
        attribute_bonus = read(
            "Choose an attribute to upgrade.",
            getAdjustableAttributes(attribute_bonuses),
        )
        base_attributes.add(attribute_bonus, 1)

    # Artificer Initiate
    if feat == "Artificer Initiate":
        oSheet.set("features", assignCantrips("Artificer", 1))
        oSheet.set(
            "tools",
            read(
                f"Choose a '{oPC.getMyBackground()}' background bonus tool proficiency.",
                oSRD.getListTools(oPC.getMyTools(), "Artisan's tools"),
            ),
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
                read(
                    "Choose a bonus language.",
                    oSRD.getListLanguages(oPC.getMyLanguages()),
                ),
            )

    # Mobile
    if feat == "Mobile":
        oSheet.set("speed", oPC.getMySpeed() + 10)

    # Prodigy
    if feat == "Prodigy":
        oSheet.set(
            "languages",
            read(
                "Choose a bonus language.",
                oSRD.getListLanguages(oPC.getMyLanguages()),
            ),
        )
        oSheet.set(
            "skills",
            read(
                "Choose a bonus skill.",
                oSRD.getListSkills(oPC.getMySkills()),
            ),
        )
        oSheet.set(
            "tools",
            read(
                "Choose a bonus skill.",
                oSRD.getListTools(oPC.getMyTools()),
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
        attribute_bonus = read(
            "Choose an attribute to upgrade.",
            attribute_bonuses,
        )
        base_attributes.add(attribute_bonus, 1)
        oSheet.set("savingthrows", attribute_bonus.capitalize())

    # Shadow Touched
    if feat == "Shadow Touched":
        oSheet.set("features", "Invisibility")
    # Skilled
    if feat == "Skilled":
        for _ in range(3):
            bonus_option = read(
                "Choose a feat (Skilled) bonus skill or tool.",
                ["Skill", "Tool"],
            )
            if bonus_option == "Skill":
                oSheet.set(
                    "skills",
                    read(
                        "Choose a bonus skill.",
                        oSRD.getListSkills(oPC.getMySkills()),
                    ),
                )
            elif bonus_option == "Tool":
                oSheet.set(
                    "tools",
                    read(
                        "Choose a bonus tool proficiency.",
                        oSRD.getListTools(oPC.getMyTools()),
                    ),
                )

    # Squat Nimbleness
    if feat == "Squat Nimbleness":
        attribute_bonuses = ["Dexterity", "Strength"]
        attribute_bonus = read(
            "Choose an attribute to upgrade.",
            getAdjustableAttributes(attribute_bonuses),
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
            oSheet.set(
                "weapons",
                read(
                    "Choose a bonus weapon proficiency.",
                    oSRD.getListWeapons(oPC.getMyWeapons()),
                ),
            )

    oSheet.set({"feats": feat})


def assignRacialTraits() -> None:
    """Assigns racial/subracial traits."""

    def assignDragonbornTraits() -> None:
        """Assigns dragonborn features."""
        if "Dragonborn" not in oPC.getMyRace():
            return
        draconic_ancestry = read(
            "Choose your dragonborn's ancestry.",
            (
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
            ),
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

    def assignHalfelfTraits() -> None:
        """Assigns half-elf features."""
        if "Halfelf" not in oPC.getMyRace():
            return
        attribute = read(
            "Choose your racial bonus attribute.",
            [
                "Strength",
                "Dexterity",
                "Constitution",
                "Intelligence",
                "Wisdom",
            ],
        )
        base = Attributes(oPC.getAttributes())
        base.add(attribute, 1)
        oSheet.set("bonus", {attribute: 1})
        oSheet.attributes = base.attributes

        oSheet.set(
            "languages",
            read(
                "Choose your racial bonus language.",
                oSRD.getListLanguages(oPC.getMyLanguages()),
            ),
        )

        for _ in range(2):
            oSheet.set(
                "skills",
                read(
                    "Choose your racial bonus skill.",
                    oSRD.getListSkills(oPC.getMySkills()),
                ),
            )

    def assignHobgoblinTraits() -> None:
        """Assigns hobgoblin features."""
        if "Hobgoblin" not in oPC.getMyRace():
            return
        for _ in range(2):
            bonus_weapons = [
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
                read(
                    "Choose your racial bonus weapon proficiency.",
                    [w for w in bonus_weapons if w not in oPC.getMyWeapons()],
                ),
            )

    def assignHumanTraits() -> None:
        """Assigns human features."""
        if "Human" not in oPC.getMyRace():
            return
        oSheet.set(
            "languages",
            read(
                "Choose your racial bonus language.",
                oSRD.getListLanguages(oPC.getMyLanguages()),
            ),
        )

    def assignKenkuTraits() -> None:
        """Assigns kenku features."""
        if "Kenku" not in oPC.getMyRace():
            return
        for _ in range(2):
            bonus_skills = [
                "Acrobatics",
                "Deception",
                "Stealth",
                "Sleight of Hand",
            ]
            oSheet.set(
                "skills",
                read(
                    "Choose your racial bonus skill.",
                    [s for s in bonus_skills if s not in oPC.getMySkills()],
                ),
            )

    def assignLizardfolkTraits() -> None:
        """Assigns lizardfolk features."""
        if "Lizardfolk" not in oPC.getMyRace():
            return
        for _ in range(2):
            bonus_skills = [
                "Animal Handling",
                "Nature",
                "Perception",
                "Stealth",
                "Survival",
            ]
            oSheet.set(
                "skills",
                read(
                    "Choose your racial bonus skill.",
                    [s for s in bonus_skills if s not in oPC.getMySkills()],
                ),
            )

    def assignRacialBonus() -> None:
        """Assigns racial bonuses to attributes."""
        base_values = oPC.getAttributes()
        bonus_values = oPC.getBonus()
        for attribute, _ in bonus_values.items():
            if attribute in bonus_values:
                base_attr = Attributes(base_values)
                base_attr.add(attribute, bonus_values[attribute])
        review_attributes()

    def assignTabaxiTraits() -> None:
        """Assigns tabaxi features."""
        if "Tabaxi" not in oPC.getMyRace():
            return
        oSheet.set(
            "languages",
            read(
                "Choose your racial bonus language.",
                oSRD.getListLanguages(oPC.getMyLanguages()),
            ),
        )

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

    assignDragonbornTraits()
    assignHobgoblinTraits()
    assignHalfelfTraits()
    assignHumanTraits()
    assignKenkuTraits()
    assignLizardfolkTraits()
    assignTabaxiTraits()
    assignBackgroundTraits()

    if subrace != "":
        traits = oSRD.getEntryBySubrace(subrace)
        oSheet.set({"bonus": traits["bonus"], "traits": traits["traits"]})

    assignRacialBonus()

    from tasha.metrics import Anthropometry

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
            pc_spell_list: List[str], warlock_spell_list: List[str]
        ) -> List[str]:
            """Removes 6-9 level spells if a spell is already known for that level."""
            for spell_level in [6, 7, 8, 9]:
                for spell in pc_spell_list:
                    spell_level_query = f"(lv. {spell_level})"
                    if spell_level_query in spell:
                        warlock_spell_list = [
                            s for s in warlock_spell_list if spell_level_query not in s
                        ]
            return warlock_spell_list

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

                spell = read(
                    f"Choose a spell ({spell_selection_counter}).",
                    spell_pool,
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


def main() -> None:
    nested_completer = NestedCompleter.from_nested_dict(
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

    while True:
        session: PromptSession = PromptSession(
            bottom_toolbar=bottom_toolbar,
            completer=nested_completer,
            refresh_interval=5.0,
        )

        try:
            cmd_str = session.prompt(
                FormattedText([("class:prompt", ">> ")]),
                completer=nested_completer,
                style=stylesheet,
            )
            TashaCmd(*TashaParser(cmd_str).run()).run()
        except (TashaCmdError, TashaParserError, ValueError) as e:
            error(e.__str__())
            pass
        except KeyboardInterrupt as e:
            error(e.__str__())
            exit(1)


if __name__ == "__main__":
    main()
