from dataclasses import dataclass, field
from math import ceil
from typing import Any, Dict, List, NoReturn


@dataclass
class CharacterSheet:
    alignment: str = field(default="")
    armors: list = field(default_factory=list)
    attributes: dict = field(default_factory=dict)
    cantrips: list = field(default_factory=list)
    gender: str = field(default="")
    hit_die: int = field(default=0)
    hit_points: int = field(default=0)
    initiative: int = field(default=0)
    languages: list = field(default_factory=list)
    level: int = field(default=1)
    name: str = field(default="")
    proficiency_bonus: int = field(default=0)
    savingthrows: list = field(default_factory=list)
    size: str = field(default="")
    skills: list = field(default_factory=list)
    speed: int = field(default=30)
    spell_slots: list = field(default_factory=list)
    spellcasting: dict = field(default_factory=dict)
    tools: list = field(default_factory=list)
    type_: str = field(default="")
    weapons: list = field(default_factory=list)

    def __post_init__(self) -> None:
        self.proficiency_bonus = ceil(self.level / 4) + 1
        try:
            self.initiative = self.attributes["Dexterity"]["modifier"]
        except KeyError:
            self.initiative = 0

    def reset(self) -> None:
        """Resets character sheet values."""
        self.alignment = ""
        self.armors = list()
        self.attributes = dict()
        self.cantrips = list()
        self.gender = ""
        self.hit_die = 0
        self.hit_points = 0
        self.initiative = 0
        self.languages = list()
        self.level = 1
        self.name = ""
        self.proficiency_bonus = 0
        self.savingthrows = list()
        self.size = ""
        self.skills = list()
        self.speed = 30
        self.spell_slots = list()
        self.spellcasting = dict()
        self.tools = list()
        self.type_ = ""
        self.weapons = list()

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


@dataclass
class NonPlayerCharacter:
    character_sheet: CharacterSheet

    def getAttributes(self) -> Dict[str, Dict[str, Any]]:
        """Returns a dictionary of all attributes."""
        return self.character_sheet.attributes

    def getAttributeModifier(self, attribute) -> int:
        """Returns the modifier of a specified attribute."""
        return self.character_sheet.attributes[attribute]["modifier"]

    def getAttributeScore(self, attribute) -> int:
        """Returns the score of a specified attribute."""
        return self.character_sheet.attributes[attribute]["score"]

    def getCasterAttribute(self, klass: str) -> int | NoReturn:
        """Returns caster's primary attribute score by class/subclass."""
        if klass in (
            "Cleric",
            "Druid",
            "Ranger",
        ):
            return self.getAttributeScore("Wisdom")

        if klass in (
            "Bard",
            "Paladin",
            "Sorcerer",
            "Warlock",
        ):
            return self.getAttributeScore("Charisma")

        if klass in ("Artificer", "Wizard"):
            return self.getAttributeScore("Intelligence")

        raise ValueError("Invalid spellcaster class specified.")

    def getMyArmors(self) -> List[str]:
        """Returns the character's armor proficiency list."""
        return self.character_sheet.armors

    def getMyAlignment(self) -> str:
        """Returns the character's alignment."""
        return self.character_sheet.alignment

    def getMyGender(self) -> str:
        """Returns the character's gender."""
        return self.character_sheet.gender

    def getMyHitDie(self) -> int:
        """Returns the character's hit die."""
        return self.character_sheet.hit_die

    def getMyLanguages(self):
        """Returns the character's languages."""
        return self.character_sheet.languages

    def getMyName(self) -> str:
        """Returns the character's name."""
        return self.character_sheet.name

    def getMySavingThrows(self) -> List[str]:
        """Returns the character's saving throw list."""
        return self.character_sheet.savingthrows

    def getMySkills(self) -> List[str]:
        """Returns the character's skill list."""
        return self.character_sheet.skills

    def getMySpeed(self) -> int:
        """Returns the character's speed."""
        return self.character_sheet.speed

    def getMyTools(self) -> List[str]:
        """Returns the character's tool proficiency list."""
        return self.character_sheet.tools

    def getMyWeapons(self) -> List[str]:
        """Returns the character's weapon proficiency list."""
        return self.character_sheet.weapons

    def getSpellSlots(self) -> List[str]:
        """Returns the character's spell slots."""
        return self.character_sheet.spell_slots
