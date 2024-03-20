from dataclasses import dataclass, field
from math import ceil
from typing import Any, Dict, List, Literal, Tuple, Union


@dataclass
class Character:
    alignment: str = field(default="")
    allotted_asi: int = field(default=0)
    allotted_skills: int = field(default=0)
    armors: list = field(default_factory=list)
    attributes: dict = field(default_factory=dict)
    background: str = field(default="Soldier")
    bonus: dict = field(default_factory=dict)
    cantrips: list = field(default_factory=list)
    classes: dict = field(default_factory=dict)
    equipment: list = field(default_factory=list)
    feats: list = field(default_factory=list)
    features: list = field(default_factory=list)
    gender: str = field(default="")
    gold: int = field(default=0)
    height: int = field(default=0)
    hit_points: int = field(init=False)
    initiative: int = field(default=0)
    languages: list = field(default_factory=list)
    level: int = field(default=1)
    name: str = field(default="Unnamed")
    proficiency_bonus: int = field(default=0)
    race: str = field(default="")
    resistances: list = field(default_factory=list)
    savingthrows: list = field(default_factory=list)
    size: str = field(default="Medium")
    skills: list = field(default_factory=list)
    speed: int = field(default=30)
    spell_slots: list = field(default_factory=list)
    spellcasting: dict = field(default_factory=dict)
    tools: list = field(default_factory=list)
    traits: list = field(default_factory=list)
    version: str = field(default="")
    weapons: list = field(default_factory=list)
    weight: int = field(default=0)

    def __post_init__(self) -> None:
        self.hit_points = self.roll_hit_points()
        self.proficiency_bonus = ceil(self.level / 4) + 1
        try:
            self.initiative = self.attributes["Dexterity"]["modifier"]
        except KeyError:
            self.initiative = 0

    def reset(self) -> None:
        self.alignment = ""
        self.allotted_asi = 0
        self.allotted_skills = 0
        self.armors = list()
        self.attributes = dict()
        self.background = "Soldier"
        self.bonus = dict()
        self.cantrips = list()
        self.classes = dict()
        self.equipment = list()
        self.feats = list()
        self.features = list()
        self.gender = ""
        self.gold = 0
        self.height = 0
        self.initiative = 0
        self.languages = list()
        self.level = 1
        self.name = "Unnamed"
        self.proficiency_bonus = 0
        self.race = ""
        self.resistances = list()
        self.savingthrows = list()
        self.size = "Medium"
        self.skills = list()
        self.speed = 30
        self.spell_slots = list()
        self.spellcasting = dict()
        self.tools = list()
        self.traits = list()
        self.weapons = list()
        self.weight = 0

    def roll_hit_points(self) -> int:
        """Calculates the character's total hit points."""
        try:
            modifier = self.attributes["Constitution"]["modifier"]
        except KeyError:
            modifier = 0

        total_hit_points = 0
        for class_slot, klass in enumerate(tuple(self.classes.keys())):
            max_hit_die = self.classes[klass]["hit_die"]
            avg_hit_die = ceil(max_hit_die / 2) + 1
            if class_slot == 0:
                total_hit_points = max_hit_die + modifier
            else:
                total_hit_points += avg_hit_die + modifier

            if self.classes[klass]["level"] > 1:
                total_hit_points += sum(
                    [
                        avg_hit_die + modifier
                        for _ in range(1, self.classes[klass]["level"])
                    ]
                )

        try:
            return total_hit_points
        except UnboundLocalError:
            return 0

    def __setitem__(self, name: str, value: Any) -> None:
        key_value = eval(f"self.{name}")
        # Append dictionary value to existing dictionary value.
        if isinstance(key_value, dict) and isinstance(value, dict):
            exec(f"self.{name}.update({value})")
        # Append new attribute, assign value of 1. TODO: Investigate usage further
        elif isinstance(key_value, dict) and isinstance(value, str):
            exec(f"self.{name} = 1")
        # Append list value to an existing list value.
        elif isinstance(key_value, list) and isinstance(value, list):
            exec(f"self.{name} = self.{name} + {value}")
        # Append str value to an existing list value.
        elif isinstance(key_value, list) and isinstance(value, str):
            exec(f'self.{name}.append("{value}")')
        else:
            if isinstance(value, str):
                exec(f'self.{name} = "{value}"')
            else:
                exec(f"self.{name} = {value}")

    def set(self, *args) -> None:
        num_of_args = len(args)
        if num_of_args == 1 and isinstance(args[0], dict):
            for key, value in args[0].items():
                self.__setitem__(key, value)
        elif num_of_args == 2:
            key, value = args
            self.__setitem__(key, value)
        else:
            raise ValueError(f"Accepts 1-2 arguments. {num_of_args} given.")


class PlayerUtils:
    def __init__(self, character_sheet: Character) -> None:
        self.character_sheet = character_sheet

    def canSubclass(self, klass: str) -> Union[Literal[False], Literal[True]]:
        """Returns False if character cannot select a subclass. True otherwise."""
        if (
            klass
            in (
                "Artificer",
                "Barbarian",
                "Bard",
                "Fighter",
                "Monk",
                "Paladin",
                "Ranger",
                "Rogue",
            )
            and self.getClassLevel(klass) < 3
        ):
            return False
        if klass in ("Cleric", "Druid", "Wizard") and self.getClassLevel(klass) < 2:
            return False
        return True

    def getAllottedAsi(self) -> int:
        """Returns the character's allotted ability score improvement total."""
        return self.character_sheet.allotted_asi

    def getAllottedSkills(self) -> int:
        """Returns the character's allotted skill total."""
        return self.character_sheet.allotted_skills

    def getAttributes(self) -> Dict[str, Dict[str, Any]]:
        """Returns a dictionary of all attributes."""
        return self.character_sheet.attributes

    def getAttributeModifier(self, attribute) -> int:
        """Returns the modifier of a specified attribute."""
        return self.character_sheet.attributes[attribute]["modifier"]

    def getAttributeScore(self, attribute) -> int:
        """Returns the score of a specified attribute."""
        return self.character_sheet.attributes[attribute]["score"]

    def getBonus(self) -> Dict[str, Dict[str, int]]:
        """Returns the character's racial bonus."""
        return self.character_sheet.bonus

    def getCasterAttribute(self, klass: str, subklass: str) -> int:
        """Return the primary spellcasting attribute by class/subclass."""
        if klass in (
            "Cleric",
            "Druid",
            "Ranger",
        ):
            return self.getAttributeScore("Wisdom")
        elif klass in (
            "Bard",
            "Paladin",
            "Sorcerer",
            "Warlock",
        ):
            return self.getAttributeScore("Charisma")
        elif klass in ("Artificer", "Wizard") or subklass in (
            "Arcane Trickster",
            "Eldritch Knight",
        ):
            return self.getAttributeScore("Intelligence")
        else:
            raise ValueError("Invalid spellcaster class specified.")

    def getClassLevel(self, klass: str) -> int:
        """Returns the specified class' level."""
        return self.character_sheet.classes[klass]["level"]

    def getClassSubclass(self, klass: str) -> str:
        """Returns the specified class' subclass."""
        return self.character_sheet.classes[klass]["subclass"]

    def getMyArmors(self) -> List[str]:
        """Returns the character's armor proficiency list."""
        return self.character_sheet.armors

    def getMyAlignment(self) -> str:
        """Returns the character's alignment."""
        return self.character_sheet.alignment

    def getMyBackground(self):
        """Returns the character's background."""
        return self.character_sheet.background

    def getMyClasses(self) -> Tuple[str, ...]:
        """Returns all the character's class names."""
        return tuple(self.character_sheet.classes.keys())

    def getMyFeats(self) -> List[str]:
        """Returns the character's feat list."""
        return self.character_sheet.feats

    def getMyGender(self) -> str:
        """Returns the character's gender."""
        return self.character_sheet.gender

    def getMyLanguages(self):
        """Returns the character's languages."""
        return self.character_sheet.languages

    def getMyName(self) -> str:
        """Returns the character's name."""
        return self.character_sheet.name

    def getMyRace(self) -> str:
        """Returns the character's race."""
        return self.character_sheet.race

    def getMyRawClasses(self) -> Dict[str, Dict[str, Any]]:
        """Returns all the character's class info."""
        return self.character_sheet.classes

    def getMySavingThrows(self) -> List[str]:
        """Returns the character's saving throw list."""
        return self.character_sheet.savingthrows

    def getMySkills(self) -> List[str]:
        """Returns the character's skill list."""
        return self.character_sheet.skills

    def getMySpeed(self) -> int:
        """Returns the character's speed."""
        return self.character_sheet.speed

    def getMySubclasses(self) -> List[str]:
        """Returns all the character's selected subclasses."""
        return [v["subclass"] for v in tuple(self.character_sheet.classes.values())]

    def getMySubrace(self) -> str:
        """Returns the character's subrace, if applicable."""
        race = self.character_sheet.race.split(", ")
        if len(race) > 1:
            return race[1]
        return ""

    def getMyTools(self) -> List[str]:
        """Returns the character's tool proficiency list."""
        return self.character_sheet.tools

    def getMyWeapons(self) -> List[str]:
        """Returns the character's weapon proficiency list."""
        return self.character_sheet.weapons

    def getSkillTotal(self) -> int:
        """Returns the total number of allotted skills by class."""
        klass = self.getMyClasses()[0]
        if klass in (
            "Bard",
            "Ranger",
        ):
            skill_total = 3
        elif klass in ("Rogue",):
            skill_total = 4
        else:
            skill_total = 2
        return skill_total

    def getSpellSlots(self) -> List[str]:
        """Returns the character's spell slots."""
        return self.character_sheet.spell_slots

    def getTotalLevel(self) -> int:
        """Returns the total level for all selected classes."""
        return sum([v["level"] for v in tuple(self.character_sheet.classes.values())])

    def getUpgradeableAttributes(self, bonus: int) -> List[str]:
        upgradeable_attributes = list()
        for attribute, values in self.getAttributes().items():
            if (values["score"] + bonus) > 20:
                continue
            upgradeable_attributes.append(attribute)
        return upgradeable_attributes

    def hasAttributes(self) -> bool:
        return len(self.getAttributes()) > 0

    def hasClass(self, klass: str) -> bool:
        """Returns True if character has classes. False otherwise."""
        return klass in self.getMyClasses()

    def hasClasses(self) -> bool:
        """Returns True if character has classes. False otherwise."""
        return len(self.getMyClasses()) > 0

    def hasRace(self) -> bool:
        """Returns True if character has a race. False otherwise."""
        return self.getMyRace() != ""

    def isSpellcaster(self) -> bool:
        """Returns True if the character is a spellcaster. False otherwise."""
        if any(
            klass in self.getMyClasses()
            for klass in (
                "Artificer",
                "Bard",
                "Cleric",
                "Druid",
                "Paladin",
                "Sorcerer",
                "Ranger",
                "Warlock",
                "Wizard",
            )
        ) or any(
            subklass in self.getMySubclasses()
            for subklass in (
                "Arcane Trickster",
                "Eldritch Knight",
            )
        ):
            return True
        return False
