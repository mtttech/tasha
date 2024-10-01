from dataclasses import dataclass, field
from math import ceil
from typing import Any, Dict, List, Literal, NoReturn, Tuple, Union


@dataclass
class CharacterSheet:
    alignment: str = field(default="")
    armors: list = field(default_factory=list)
    attributes: dict = field(default_factory=dict)
    background: str = field(default="")
    bonus: dict = field(default_factory=dict)
    cantrips: int = field(default=0)
    classes: dict = field(default_factory=dict)
    feats: list = field(default_factory=list)
    features: list = field(default_factory=list)
    gender: str = field(default="")
    gold: int = field(default=0)
    hit_die: int = field(default=0)
    hit_points: int = field(init=False)
    initiative: int = field(default=0)
    languages: list = field(default_factory=list)
    level: int = field(default=1)
    name: str = field(default="")
    prepared_spells: int = field(default=0)
    proficiency_bonus: int = field(default=0)
    savingthrows: list = field(default_factory=list)
    size: str = field(default="Medium")
    skills: list = field(default_factory=list)
    species: str = field(default="")
    speed: int = field(default=30)
    spell_slots: list = field(default_factory=list)
    tools: list = field(default_factory=list)
    traits: list = field(default_factory=list)
    weapons: list = field(default_factory=list)

    def __post_init__(self) -> None:
        self.hit_points = self.roll_hit_points()
        self.proficiency_bonus = ceil(self.level / 4) + 1
        try:
            self.initiative = self.attributes["Dexterity"]["modifier"]
        except KeyError:
            self.initiative = 0

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


@dataclass
class PlayerCharacter:
    character_sheet: CharacterSheet

    def canSubclass(self, klass: str) -> Union[Literal[False], Literal[True]]:
        """Returns False if character cannot select a subclass. True otherwise."""
        if (
            klass
            in (
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

    def getAttributes(self) -> Dict[str, Dict[str, Any]]:
        """Returns a dictionary of all attributes."""
        return self.character_sheet.attributes

    def getAttributeModifier(self, attribute) -> int:
        """Returns the modifier of a specified attribute."""
        return self.character_sheet.attributes[attribute]["modifier"]

    def getAttributeScore(self, attribute) -> int:
        """Returns the score of a specified attribute."""
        return self.character_sheet.attributes[attribute]["score"]

    def getCasterAttribute(self, klass: str, subklass: str) -> int | NoReturn:
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

        if klass in ("Artificer", "Wizard") or subklass in (
            "Arcane Trickster",
            "Eldritch Knight",
        ):
            return self.getAttributeScore("Intelligence")

        raise ValueError("Invalid spellcaster class specified.")

    def getClassLevel(self, klass: str) -> int:
        """Returns the specified level by klass."""
        return self.character_sheet.classes[klass]["level"]

    def getClassSubclass(self, klass: str) -> str:
        """Returns the specified subclass by klass."""
        return self.character_sheet.classes[klass]["subclass"]

    def getMyArmorProficiencies(self) -> List[str]:
        """Returns the character's armor proficiency list."""
        return self.character_sheet.armors

    def getMyAlignment(self) -> str:
        """Returns the character's alignment."""
        return self.character_sheet.alignment

    def getMyBackground(self):
        """Returns the character's background."""
        return self.character_sheet.background

    def getMyBonus(self):
        """Returns the character's bonus."""
        return self.character_sheet.bonus

    def getMyClasses(self) -> Tuple[str, ...]:
        """Returns all the character's class names."""
        return tuple(self.character_sheet.classes.keys())

    def getMyFeats(self) -> List[str]:
        """Returns the character's feat list."""
        return self.character_sheet.feats

    def getMyFeatures(self) -> List[str]:
        """Returns the character's class features."""
        return self.character_sheet.features

    def getMyGender(self) -> str:
        """Returns the character's gender."""
        return self.character_sheet.gender

    def getMyLanguages(self):
        """Returns the character's languages."""
        return self.character_sheet.languages

    def getMyName(self) -> str:
        """Returns the character's name."""
        return self.character_sheet.name

    def getMySpecies(self) -> str:
        """Returns the character's species."""
        return self.character_sheet.species

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

    def getMyToolProficiencies(self) -> List[str]:
        """Returns the character's tool proficiency list."""
        return self.character_sheet.tools

    def getMyWeaponProficiencies(self) -> List[str]:
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

    def getTotalLevel(self) -> int:
        """Returns the total level for all character classes."""
        return sum([v["level"] for v in tuple(self.character_sheet.classes.values())])

    def getUpgradeableAttributes(self, bonus: int) -> List[str]:
        """Returns a list of all upgradeable attributes."""
        upgradeable_attributes = list()
        for attribute, values in self.getAttributes().items():
            if (values["score"] + bonus) > 20:
                continue
            upgradeable_attributes.append(attribute)
        return upgradeable_attributes

    def hasAttributes(self) -> bool:
        """Returns True if attributes have been set. False otherwise."""
        return len(self.getAttributes()) > 0

    def hasClass(self, klass: str) -> bool:
        """Returns True if character is a member of klass. False otherwise."""
        return klass in self.getMyClasses()

    def hasClasses(self) -> bool:
        """Returns True if character has classes set. False otherwise."""
        return len(self.getMyClasses()) > 0

    def hasSpecies(self) -> bool:
        """Returns True if character has a set race. False otherwise."""
        return self.getMySpecies() != ""

    def isSpellcaster(self) -> bool:
        """Returns True if the character is a spellcaster. False otherwise."""
        if any(
            klass in self.getMyClasses()
            for klass in (
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
