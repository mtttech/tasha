from dataclasses import dataclass, field
from math import ceil
from typing import Any, Dict, List, Tuple


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
    hit_die: int = field(default=0)
    hit_points: int = field(init=False)
    initiative: int = field(default=0)
    languages: list = field(default_factory=list)
    level: int = field(default=1)
    name: str = field(default="")
    prepared_spells: dict = field(default_factory=dict)
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
        """Calculates the character's total hit points.

        Returns:
            int: Returns the calculated hit point total."""
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
    chst: CharacterSheet

    def getAttributes(self) -> Dict[str, Dict[str, Any]]:
        """Returns a dictionary of all attributes.

        Returns:
            Dict[str, Dict[str, Any]]: Returns character abilities/scores/modifiers."""
        return self.chst.attributes

    def getLevelByClass(self, klass: str) -> int:
        """Returns the specified level by klass.

        Args:
            klass (str): Class to get the level for.

        Returns:
            int: Returns the level of the specified class."""
        try:
            return self.chst.classes[klass]["level"]
        except KeyError:
            return 0

    def getModifierByAbility(self, attribute: str) -> int:
        """Returns the modifier of a specified attribute.

        Args:
            attribute (str): Name of the attribute to get the modifier for.

        Returns:
            int: Returns the modifier."""
        return self.chst.attributes[attribute]["modifier"]

    def getMyArmorProficiencies(self) -> List[str]:
        """Returns the character's armor proficiency list."""
        return self.chst.armors

    def getMyAlignment(self) -> str:
        """Returns the character's alignment."""
        return self.chst.alignment

    def getMyBackground(self) -> str:
        """Returns the character's background.

        Returns:
            str: Returns the character's background."""
        return self.chst.background

    def getMyBonus(self) -> Dict[str, int]:
        """Returns the character's bonus.

        Returns:
            Dict[str, int]: Returns a dict of applicable ability score bonuses."""
        return self.chst.bonus

    def getMyClasses(self) -> Tuple[str, ...]:
        """Returns all the character's class names."""
        return tuple(self.chst.classes.keys())

    def getMyFeats(self) -> List[str]:
        """Returns the character's feat list.

        Returns:
            List[str]: Returns a list of all possessed feats."""
        return self.chst.feats

    def getMyFeatures(self) -> List[str]:
        """Returns the character's class features.

        Returns:
            List[str]: Returns a list of all possessed features."""
        return self.chst.features

    def getMyGender(self) -> str:
        """Returns the character's gender.

        Returns:
            str: Returns the character's gender."""
        return self.chst.gender

    def getMyLanguages(self):
        """Returns the character's languages."""
        return self.chst.languages

    def getMyName(self) -> str:
        """Returns the character's name.

        Returns:
            str: Returns the character's name."""
        return self.chst.name

    def getMyPreparedSpellCount(self):
        """Returns the character's number of prepared spells."""
        return self.chst.prepared_spells

    def getMySpecies(self) -> str:
        """Returns the character's species.

        Returns:
            str: Returns the character's species."""
        return self.chst.species

    def getMyRawClasses(self) -> Dict[str, Dict[str, Any]]:
        """Returns all the character's class info."""
        return self.chst.classes

    def getMySavingThrows(self) -> List[str]:
        """Returns the character's saving throw list."""
        return self.chst.savingthrows

    def getMySkills(self) -> List[str]:
        """Returns the character's skill list."""
        return self.chst.skills

    def getMySpeed(self) -> int:
        """Returns the character's speed."""
        return self.chst.speed

    def getMySpellSlots(self) -> List[int]:
        """Returns the character's spell slots."""
        return self.chst.spell_slots

    def getMySubclasses(self) -> List[str]:
        """Returns all the character's selected subclasses."""
        return [v["subclass"] for v in tuple(self.chst.classes.values())]

    def getMyToolProficiencies(self) -> List[str]:
        """Returns the character's tool proficiency list."""
        return self.chst.tools

    def getMyWeaponProficiencies(self) -> List[str]:
        """Returns the character's weapon proficiency list."""
        return self.chst.weapons

    def getScoreByAbility(self, attribute: str) -> int:
        """Returns the score of a specified attribute.

        Args:
            attribute (str): Name of the attribute to get the score for.

        Returns:
            int: Returns the score."""
        return self.chst.attributes[attribute]["score"]

    def getSubclassByClass(self, klass: str) -> str:
        """Returns the specified subclass by klass.

        Args:
            klass (str): Class to get the subclass for.

        Returns:
            str: Returns the subclass of the specified class."""
        return self.chst.classes[klass]["subclass"]

    def getTotalLevel(self) -> int:
        """Returns the total level for all character classes."""
        return sum([v["level"] for v in tuple(self.chst.classes.values())])

    def getUpgradeableAttributes(self, bonus: int) -> List[str]:
        """Returns a list of all upgradeable attributes."""
        upgradeable_attributes = list()
        for attribute, values in self.getAttributes().items():
            if (values["score"] + bonus) > 20:
                continue
            upgradeable_attributes.append(attribute)
        return upgradeable_attributes

    def hasClass(self, klass: str) -> bool:
        """Returns True if character is a member of klass. False otherwise."""
        return klass in self.getMyClasses()

    def hasClasses(self) -> bool:
        """Returns True if character has classes set. False otherwise."""
        return len(self.getMyClasses()) > 0

    def isSpellcaster(self) -> bool:
        """Determines if character is of a spellcasting class.

        Returns:
            bool: Returns True if spellcaster or False otherwise."""
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
