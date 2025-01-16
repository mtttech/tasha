from typing import Any, Dict, List, Optional

from . import (
    alignments,
    backgrounds,
    classes,
    feats,
    languages,
    multiclasses,
    proficiencies,
    skills,
    species,
    spells,
)


class SystemResourceDocument:
    """Class to reference d20 rule guidelines."""

    def __init__(self) -> None:
        srd5e: Dict[str, Any] = dict()
        srd5e.update(alignments.alignments)
        srd5e.update(backgrounds.backgrounds)
        srd5e.update(classes.classes)
        srd5e.update(feats.feats)
        srd5e.update(languages.languages)
        srd5e.update(multiclasses.multiclasses)
        srd5e.update(proficiencies.proficiencies)
        srd5e.update(species.species)
        srd5e.update(skills.skills)
        srd5e.update(spells.spells)
        self.srd = dict(
            zip(
                [
                    "alignments",
                    "backgrounds",
                    "classes",
                    "feats",
                    "languages",
                    "multiclasses",
                    "proficiencies",
                    "species",
                    "skills",
                    "spells",
                ],
                list(srd5e.values()),
            )
        )

    def getAbilitiesByBackground(self, background: str) -> List[str]:
        """Returns a list of abilities by background.

        Args:
            background (str): Background to get the abilities for.

        Returns:
            List[str]: Returns a list of background abilities."""
        return self.srd["backgrounds"][background]["ability"]

    def getAbilityRequirementsByFeat(self, feat: str) -> Dict[str, int]:
        """Returns ability score requirements by feat.

        Args:
            feat (str): Name of the feat to get requirements for.

        Returns:
            Dict[str, int]: Returns a dict of ability requirements."""
        return self.srd["feats"][feat]["ability"]

    def getAlignments(self) -> List[str]:
        """Returns a list of alignments.

        Returns:
            List[str]: Returns a list of all applicable DnD alignments."""
        return self.srd["alignments"]

    def getArmorProficienciesByClass(
        self, klass: str, primary_class: bool
    ) -> List[str]:
        """Returns armor proficiencies by class.

        Args:
            klass (str): Name of the class to get armor proficiencies for.

        Returns:
            List[str]: Returns a list of armor proficiencies by klass."""
        if primary_class:
            return self.srd["classes"][klass]["armors"]

        return self.srd["multiclasses"][klass]["armors"]

    def getArmorRequirementsByFeat(self, feat: str) -> List[str]:
        """Returns armor proficiency requirements by feat.

        Args:
            feat (str): Name of the feat to get requirements for.

        Returns:
            List[str]: Returns a list of armor proficiency requirements."""
        return self.srd["feats"][feat]["armors"]

    def getBackgrounds(self) -> List[str]:
        """Returns a list of backgrounds.

        Returns:
            List[str]: Returns a list of applicable backgrounds."""
        return list(self.srd["backgrounds"].keys())

    def getCantripsKnownByClass(self, klass: str, level: int) -> int:
        """Returns the total number of cantrips known by class and level.

        Args:
            klass (str): Class to get the number of cantrips known for.
            level (int): Level of the class to get the number of cantrips known for.

        Returns:
            int: Returns a count of cantrips spells known."""
        try:
            return self.srd["classes"][klass]["cantrips"][level]
        except KeyError:
            return 0

    def getClasses(self) -> List[str]:
        """Returns a list of classes.

        Returns:
            List[str]: Returns a list of applicable classes."""
        return list(self.srd["classes"].keys())

    def getFeats(self) -> List[str]:
        """Returns all feats.

        Returns:
            List[str]: Returns a list of applicable feats."""
        return list(self.srd["feats"])

    def getFeatsByCategory(self, category: str) -> List[str]:
        """Returns a list of feats by category.

        Args:
            category (str): Category of the feats requested: General, Epic Boon, Fighting Style, or Origin.

        Returns:
            List[str]: Returns a list of feats for the specified category."""
        feats_by_category = list()
        for feat, params in self.srd["feats"].items():
            if params["category"] == category:
                feats_by_category.append(feat)
        return feats_by_category

    def getFeatureRequirementsByFeat(self, feat: str) -> List[str]:
        """Returns feature requirements by feat.

        Args:
            feat (str): Name of feat to get feature requirements for.

        Returns:
            List[str]: Returns a list of feature requirements."""
        return self.srd["feats"][feat]["features"]

    def getFeaturesByClass(self, klass: str, class_level: int) -> List[str]:
        """Returns all features based on the specified class and level.

        Args:
            klass (str): Name of the class to get features for.
            class_level (int): Level of the class to get features for.

        Returns:
            List[str]: Returns a list of features by class."""
        class_features = list()
        for level, features in self.srd["classes"][klass]["features"].items():
            if class_level >= level:
                class_features = class_features + features
        return class_features

    def getHitDieByClass(self, klass: str) -> int:
        """Returns hit die type by class.

        Args:
            klass (str): Name of the class to get hit die type of.

        Returns:
            int: Returns the class' hit die value."""
        return self.srd["classes"][klass]["hit_die"]

    def getLevelRequirementByFeat(self, feat: str) -> int:
        """Returns level requirement by feat.

        Args:
            feat (str): Name of the feat to get level requirements for.

        Returns:
            int: Returns the level requirement of the feat."""
        return self.srd["feats"][feat]["level"]

    def getPreparedSpellCountByClass(self, klass: str, level: int) -> int:
        """Returns number of prepared spells by class and level.

        Args:
            klass (str): Name of the class to get the prepared spell count for.
            level (int): Level of the class to get the prepared spell count for.

        Returns:
            int: Returns the applicable number of prepared spells."""
        try:
            return self.srd["classes"][klass]["prepared_spells"][level]
        except KeyError:
            return 0

    def getRareLanguages(self, excl: Optional[List[str]] = None) -> List[str]:
        """Returns all rare languages (minus exclusions, if applicable).

        Args:
            excl (Optional[List[str]]): List of languages to exclude, if applicable.

        Returns:
            List[str]: Returns a list of applicable languages."""
        language_list = self.srd["languages"]["rare"]
        if isinstance(excl, list):
            return [l for l in language_list if l not in excl]
        return language_list

    def getSavingThrowsByClass(self, klass: str) -> List[str]:
        """Returns saving throw proficiencies by class.

        Args:
            klass (str): Name of the class to get saving throws for.

        Returns:
            List[str]: Returns a list applicable saving throws."""
        return self.srd["classes"][klass]["savingthrows"]

    def getSizeBySpecies(self, species: str) -> str:
        """Returns size by species.

        Args:
            species (str): Name of the species to get the size for.

        Returns:
            str: Returns the size type of the species."""
        return self.srd["species"][species]["size"]

    def getSkillAbility(self, skill: str) -> str:
        """Returns the associated ability for a skill."""
        try:
            return self.srd["skills"][skill]["ability"]
        except KeyError:
            return ""

    def getSkillsByBackground(self, background: str) -> List[str]:
        """Returns a list of skills by background.

        Args:
            background (str): Background to get the skills for.

        Returns:
            List[str]: Returns a list of background skills."""
        return self.srd["backgrounds"][background]["skills"]

    def getSkillsByClass(
        self, klass: str, excl: Optional[List[str]] = None
    ) -> List[str]:
        """Returns skills by class, minus exclusions (if applicable).

        Args:
            klass (str): Name of the class to get skills for.
            excl (Optional[List[str]]): List of skills to exclude.

        Returns:
            List[str]: Returns the list of applicable skills."""
        class_skills = self.srd["classes"][klass]["skills"]
        if isinstance(excl, list):
            return [s for s in class_skills if s not in excl]
        return class_skills

    def getSpecies(self) -> List[str]:
        """Returns a list of species.

        Returns:
            List[str]: Returns a list of all applicable DnD species."""
        return list(self.srd["species"].keys())

    def getSpeedBySpecies(self, species: str) -> int:
        """Returns speed (in feet) by species.

        Args:
            species (str): Name of the species to get the speed for.

        Returns:
            int: Returns the base speed value of the species."""
        return self.srd["species"][species]["speed"]

    def getSpellsByLevel(self, spell_level: int, klass: str) -> Dict[int, List[str]]:
        """Returns spell list by level and class.

        Args:
            spell_level (int): Level to get spell list for.
            klass (str): Class to get spell list for.

        Returns:
            Dict[int, List[str]]: Returns a dict of level with spells for the specified level.
        """
        if klass in ("Fighter", "Rogue"):
            klass = "Wizard"

        try:
            spell_list = dict()
            for level, spells in self.srd["spells"][klass].items():
                if level <= spell_level:
                    spell_list[level] = spells
            return spell_list
        except KeyError:
            return dict()

    def getSpellslotsByClass(self, klass: str, level: int) -> List[int]:
        """Returns spell slots by class and level.

        Args:
            klass (str): Class to get spell slots for.
            level (int): Level to get spell slots for.

        Returns:
            List[str]: Returns a list of spell slots per level."""
        try:
            return self.srd["classes"][klass]["spell_slots"][level]
        except KeyError:
            return [0]

    def getStandardLanguages(self, excl: Optional[List[str]] = None) -> List[str]:
        """Returns all standard languages (minus exclusions, if applicable).

        Args:
            excl (Optional[List[str]]): List of languages to exclude.

        Returns:
            List[str]: Returns a list of applicable languages."""
        language_list = self.srd["languages"]["standard"]
        if isinstance(excl, list):
            return [l for l in language_list if l not in excl]
        return language_list

    def getToolProficienciesByBackground(self, background: str) -> List[str]:
        """Returns tool proficiencies by background.

        Args:
            background (str): Background to get tool proficiencies for.

        Returns:
            List[str]: Returns a list of tool proficiencies."""
        return self.srd["backgrounds"][background]["tools"]

    def getToolProficienciesByClass(
        self, klass: str, excl: Optional[List[str]] = None
    ) -> List[str]:
        """Returns a list of all tool proficiencies by class.

        Args:
            klass (str): Class to get tool proficiencies for.
            excl (Optional[List[str]]): List of tool proficiencies to exclude.

        Returns:
            List[str]: Returns a list of applicable tool proficiencies."""
        tool_proficiencies = self.srd["classes"][klass]["tools"]
        if isinstance(excl, list):
            return [t for t in tool_proficiencies if t not in excl]
        return tool_proficiencies

    def getSubclassesByClass(self, klass: str) -> List[str]:
        """Returns a list of subclasses by class."""
        return list(self.srd["classes"][klass]["subclasses"])

    def getTraitsBySpecies(self, species: str) -> List[str]:
        """Returns a list of traits by species."""
        return list(self.srd["species"][species]["traits"])

    def getWeaponProficienciesByClass(
        self, klass: str, primary_class: bool
    ) -> List[str]:
        """Returns weapon proficiencies by class."""
        if primary_class:
            return self.srd["classes"][klass]["weapons"]

        return self.srd["multiclasses"][klass]["weapons"]

    def hasAbilityRequirementsByClass(
        self, klass: str, attributes: Dict[str, Dict[str, Any]]
    ) -> bool:
        """Determines if character meets ability requirements to multiclass.

        Args:
            klass (str): Name of the class to check ability requirements for.
            attributes (Dict[str, Dict[str, Any]]): Attributes to use in the requirements check.

        Returns:
            bool: Returns True if character meets ability requirements or False otherwise.
        """
        if klass != "Fighter":
            for ability in self.srd["multiclasses"][klass]["ability"]:
                if attributes[ability]["score"] < 13:
                    return False
        else:
            if (
                attributes["Strength"]["score"] < 13
                and attributes["Dexterity"]["score"] < 13
            ):
                return False

        return True
