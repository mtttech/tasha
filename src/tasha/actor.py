from dataclasses import dataclass, field
from math import ceil
from typing import Any


@dataclass
class PlayerCharacter:
    """Stores/retrieves player character information."""

    alignment: str = field(default="")
    armors: list[str] = field(default_factory=list)
    attributes: dict[str, dict[str, int]] = field(default_factory=dict)
    background: str = field(default="")
    bonus: dict[str, int] = field(default_factory=dict)
    cantrips: dict[str, dict[str, int]] = field(default_factory=dict)
    classes: dict[str, dict[str, Any]] = field(default_factory=dict)
    feats: list[str] = field(default_factory=list)
    features: dict[str, list[str]] = field(default_factory=dict)
    gender: str = field(default="")
    hit_points: int = field(init=False)
    languages: list[str] = field(default_factory=list)
    level: int = field(default=1)
    name: str = field(default="")
    prepared_spells: dict[str, list[str]] = field(default_factory=dict)
    proficiency_bonus: int = field(default=0)
    savingthrows: list[str] = field(default_factory=list)
    size: str = field(default="Medium")
    skills: list[str] = field(default_factory=list)
    species: str = field(default="")
    speed: int = field(default=30)
    spell_slots: list[int] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    traits: list[str] = field(default_factory=list)
    weapons: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        # Calculate hit points/proficiency bonus.
        self.hit_points = self._rollHitPoints()
        self.proficiency_bonus = ceil(self.level / 4) + 1

    def __setitem__(self, name: str, value: Any) -> None:
        key_value = eval(f"self.{name}")
        # Dict: Append dictionary value to existing dictionary value.
        if isinstance(key_value, dict) and isinstance(value, dict):
            exec(f"self.{name}.update({value})")
        # List: Append list value to an existing list value.
        elif isinstance(key_value, list) and isinstance(value, list):
            exec(f"self.{name} = self.{name} + {value}")
            exec(f"self.{name} = list(set(self.{name}))")
        # List: Append str value to an existing list value.
        elif isinstance(key_value, list) and isinstance(value, str):
            exec(f'self.{name}.append("{value}")')
        # Str, Int: Literal values.
        else:
            if isinstance(value, str):
                exec(f'self.{name} = "{value}"')
            else:
                exec(f"self.{name} = {value}")

    def _rollHitPoints(self) -> int:
        """Calculates the character's total hit points.

        Returns:
            int: Returns the calculated hit point total."""
        modifier = self.getModifierByAbility("Constitution")
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
                        for _ in range(1, self.getLevelByClass(klass))
                    ]
                )

        try:
            return total_hit_points
        except UnboundLocalError:
            return 0

    def getLevelByClass(self, klass: str) -> int:
        """Returns the specified level by klass.

        Args:
            klass (str): Class to get the level for.

        Returns:
            int: Returns the level of the specified class."""
        try:
            return self.classes[klass]["level"]
        except KeyError:
            return 0

    def getModifierByAbility(self, attribute: str) -> int:
        """Returns the modifier of a specified attribute.

        Args:
            attribute (str): Name of the attribute to get the modifier for.

        Returns:
            int: Returns the modifier."""
        try:
            return self.attributes[attribute]["modifier"]
        except KeyError:
            return 0

    def getMyArmorProficiencies(self) -> list[str]:
        """Returns the character's armor proficiency list.

        Returns:
            list[str]: Returns a list of the character's armor proficiencies."""
        return self.armors

    def getMyAttributes(self) -> dict[str, dict[str, int]]:
        """Returns a dictionary of all attributes.

        Returns:
            dict[str, dict[str, int]]: Returns character abilities/scores/modifiers."""
        return self.attributes

    def getMyBackground(self) -> str:
        """Returns the character's background.

        Returns:
            str: Returns the character's background."""
        return self.background

    def getMyBonus(self) -> dict[str, int]:
        """Returns the character's bonus.

        Returns:
            dict[str, int]: Returns the character's ability score bonuses."""
        return self.bonus

    def getMyClasses(self) -> list[str]:
        """Returns the character's classes.

        Returns:
            list[str]: Returns a list of the character's classes."""
        return list(self.classes.keys())

    def getMyFeats(self) -> list[str]:
        """Returns the character's feats.

        Returns:
            list[str]: Returns a list of all the character's feats."""
        return self.feats

    def getMyFeatures(self) -> dict[str, list[str]]:
        """Returns the character's class features.

        Returns:
            list[str]: Returns a list of all the character's class features."""
        return self.features

    def getMyLanguages(self) -> list[str]:
        """Returns the character's languages.

        Returns:
            list[str]: Returns a list of the character's languages."""
        return self.languages

    def getMyName(self) -> str:
        """Returns the character's name.

        Returns:
            str: Returns the character's name."""
        return self.name

    def getMySavingThrows(self) -> list[str]:
        """Returns the character's saving throw list."""
        return self.savingthrows

    def getMySkills(self) -> list[str]:
        """Returns the character's skill list.

        Returns:
            list[str]: Returns a list of the character's skills."""
        return self.skills

    def getMySpecies(self) -> str:
        """Returns the character's species.

        Returns:
            str: Returns the character's species."""
        return self.species

    def getMySpeed(self) -> int:
        """Returns the character's speed.

        Returns:
            int: Returns the character's speed value."""
        return self.speed

    def getMySpellslots(self) -> list[int]:
        """Returns the character's spell slots.

        Returns:
            list[int]: Returns a list of the character's spell slots."""
        return self.spell_slots

    def getMySubclassByClass(self, klass: str) -> str:
        """Returns the character's subclass by class.

        Returns:
            str: Returns a list of the character's subclasses."""
        return self.classes[klass]["subclass"]

    def getMyToolProficiencies(self) -> list[str]:
        """Returns the character's tool proficiency list.

        Returns:
            list[str]: Returns a list of the character's tool proficiencies."""
        return self.tools

    def getMyWeaponProficiencies(self) -> list[str]:
        """Returns the character's weapon proficiency list.

        Returns:
            list[str]: Returns a list of the character's weapon proficiencies."""
        return self.weapons

    def getScoreByAbility(self, attribute: str) -> int:
        """Returns the score of a specified attribute.

        Args:
            attribute (str): Name of the attribute to get the score for.

        Returns:
            int: Returns the score."""
        return self.attributes[attribute]["score"]

    def getSpellcastingLevel(self, klass: str) -> int:
        """Returns spell slots by class and level.

        Args:
            klass (str): Class to get the spellcasting level for.

        Returns:
            int: Returns the spellcasting level for the specified class."""
        if not self.isMulticlassSpellcaster():
            return self.getLevelByClass(klass)
        else:
            level = 0
            for klass in self.getMyClasses():
                if klass in ("Bard", "Cleric", "Druid", "Sorcerer", "Wizard"):
                    level += self.getLevelByClass(klass)
                elif klass in ("Paladin", "Ranger"):
                    level += ceil(self.getLevelByClass(klass) / 2)
                elif self.getMySubclassByClass(klass) in (
                    "Arcane Trickster",
                    "Eldritch Knight",
                ):
                    level += ceil(self.getLevelByClass(klass) / 3)
            return level

    def getSubclassByClass(self, klass: str) -> str:
        """Returns the specified subclass by klass.

        Args:
            klass (str): Class to get the subclass for.

        Returns:
            str: Returns the subclass of the specified class."""
        return self.classes[klass]["subclass"]

    def getTotalLevel(self) -> int:
        """Returns the total level for all character classes.

        Returns:
            int: Returns the total level of all applicable classes."""
        return sum([v["level"] for v in tuple(self.classes.values())])

    def hasClass(self, klass: str) -> bool:
        """Determines if character is a member of the specified class.

        Returns:
            bool: Returns True if character is a member of klass or False otherwise."""
        return klass in self.getMyClasses()

    def hasClasses(self) -> bool:
        """Determines if character is a member of at least one class.

        Returns:
            bool: Returns True if the character has classes or False otherwise."""
        return len(self.getMyClasses()) > 0

    def isMulticlassSpellcaster(self) -> bool:
        """Determines if character has more than one spellcasting class.

        Returns:
            bool: Returns True if character has more than one spellcasting class."""
        for klass in self.getMyClasses():
            if not self.isSpellcastingClass(klass):
                return False

        return True

    def isSpellcastingClass(self, klass: str) -> bool:
        """Determines if character is of a spellcasting class.

        Returns:
            bool: Returns True if spellcaster or False otherwise."""
        if klass in (
            "Bard",
            "Cleric",
            "Druid",
            "Paladin",
            "Sorcerer",
            "Ranger",
            "Warlock",
            "Wizard",
        ) or self.getMySubclassByClass(klass) in (
            "Arcane Trickster",
            "Eldritch Knight",
        ):
            return True
        return False

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
