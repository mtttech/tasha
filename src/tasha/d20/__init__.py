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

    def getAbilityRequirementsByFeat(self, feat: str) -> Dict[str, int]:
        """Returns ability score requirements by feat.

        Args:
            feat (str): Name of the feat to get requirements for.

        Returns:
            Dict[str, int]: Returns dict of ability requirements."""
        return self.srd["feats"][feat]["ability"]

    def getAlignments(self) -> List[str]:
        """Returns a list of alignments."""
        return self.srd["alignments"]

    def getArmorProficienciesByClass(self, klass: str) -> List[str]:
        """Returns armor proficiencies by class.

        Args:
            klass (str): Name of the class to get armor proficiencies for.

        Returns:
            List[str]: Returns list of armor proficiencies by klass."""
        return self.srd["classes"][klass]["armors"]

    def getArmorProficiencyRequirementByFeat(self, feat: str) -> List[str]:
        """Returns armor proficiency requirements by feat.

        Args:
            feat (str): Name of the feat to get requirements for.

        Returns:
            List[str]: Returns a list of armor proficiency requirements."""
        return self.srd["feats"][feat]["armors"]

    def getBackgroundAbilityScores(self, background: str) -> List[str]:
        """Returns a list of abilities by background."""
        return self.srd["backgrounds"][background]["ability"]

    def getBackgroundSkills(self, background: str) -> List[str]:
        """Returns a list of skills by background."""
        return self.srd["backgrounds"][background]["skills"]

    def getBackgroundToolProficiencies(self, background: str) -> List[str]:
        """Returns tool proficiencies by background."""
        return self.srd["backgrounds"][background]["tools"]

    def getBackgrounds(self) -> List[str]:
        """Returns a list of backgrounds."""
        return list(self.srd["backgrounds"].keys())

    def getCantripsKnownByClass(self, klass: str, level: int) -> int:
        """Returns the total number of cantrips known by class and level."""
        try:
            return self.srd["classes"][klass]["cantrips"][level]
        except KeyError:
            return 0

    def getClassFeatures(self, klass: str, class_level: int) -> List[str]:
        """Returns features by class and level."""
        class_features = list()
        for level, features in self.srd["classes"][klass]["features"].items():
            if class_level >= level:
                class_features = class_features + features
        return class_features

    def getClassSkills(self, klass: str, excl: Optional[List[str]] = None) -> List[str]:
        """Returns skills by class, minus exclusions (if applicable)."""
        class_skills = self.srd["classes"][klass]["skills"]
        if isinstance(excl, list):
            return [s for s in class_skills if s not in excl]
        return class_skills

    def getClassSpellSlots(self, klass: str, level: int) -> List[int]:
        """Returns spell slots by class and level."""
        try:
            return self.srd["classes"][klass]["spell_slots"][level]
        except KeyError:
            return [0]

    def getClasses(self) -> List[str]:
        """Returns a list of classes."""
        return list(self.srd["classes"].keys())

    def getFeats(self) -> List[str]:
        """Returns all feats."""
        return list(self.srd["feats"])

    def getFeatsByCategory(self, category: str) -> List[str]:
        """Returns a list of feats by category."""
        feats_by_category = list()
        for feat, params in self.srd["feats"].items():
            if params["category"] == category:
                feats_by_category.append(feat)
        return feats_by_category

    def getFeatureRequirementsByFeat(self, feat: str) -> List[str]:
        """Returns feature requirements by feat."""
        return self.srd["feats"][feat]["features"]

    def getHitDieByClass(self, klass: str) -> int:
        """Returns hit die type by class."""
        return self.srd["classes"][klass]["hit_die"]

    def getLevelRequirementByFeat(self, feat: str) -> int:
        """Returns level requirement by feat."""
        return self.srd["feats"][feat]["level"]

    def getPreparedSpellCountByClass(self, klass: str, level: int) -> int:
        """Returns number of prepared spells by class and level."""
        try:
            return self.srd["classes"][klass]["prepared_spells"][level]
        except KeyError:
            return 0

    def getRareLanguages(self, excl: Optional[List[str]] = None) -> List[str]:
        """Returns all rare languages (minus exclusions, if applicable)."""
        language_list = self.srd["languages"]["rare"]
        if isinstance(excl, list):
            return [l for l in language_list if l not in excl]
        return language_list

    def getSavingThrowsByClass(self, klass: str) -> List[str]:
        """Returns saving throw proficiencies by class."""
        return self.srd["classes"][klass]["savingthrows"]

    def getSizeBySpecies(self, species: str) -> List[str]:
        """Returns size type by species."""
        return self.srd["species"][species]["size"]

    def getSkillAbility(self, skill: str) -> str:
        """Returns the associated ability for a skill."""
        try:
            return self.srd["skills"][skill]["ability"]
        except KeyError:
            return ""

    def getSpecies(self) -> List[str]:
        """Returns a list of species."""
        return list(self.srd["species"].keys())

    def getSpeedBySpecies(self, species: str) -> List[str]:
        """Returns speed (in feet) by species."""
        return self.srd["species"][species]["speed"]

    def getSpellListByClass(self, klass: str, spell_level: int) -> Dict[int, List[str]]:
        try:
            spell_list = dict()
            for level, spells in self.srd["spells"][klass].items():
                if level <= spell_level:
                    spell_list[level] = spells
            return spell_list
        except KeyError:
            return dict()

    def getStandardLanguages(self, excl: Optional[List[str]] = None) -> List[str]:
        """Returns all standard languages (minus exclusions, if applicable)."""
        language_list = self.srd["languages"]["standard"]
        if isinstance(excl, list):
            return [l for l in language_list if l not in excl]
        return language_list

    def getToolProficienciesByClass(
        self, klass: str, excl: Optional[List[str]] = None
    ) -> List[str]:
        """Returns a list of all tool proficiencies by class."""
        tool_proficiencies = self.srd["classes"][klass]["tools"]
        if isinstance(excl, list):
            return [t for t in tool_proficiencies if t not in excl]
        return tool_proficiencies

    def getListSpells(self, klass: str, level: int) -> List[str]:
        """Returns a list of spells by available spell slots."""
        max_spell_level = self.srd["classes"][klass]["spell_slots"][level].split(",")
        spell_list = []

        for spell_level in range(0, len(max_spell_level)):
            if spell_level == 0:
                continue

            spell_list += self.getSpellListByClass(klass, spell_level)

        return spell_list

    def getSubclassesByClass(self, klass: str) -> List[str]:
        """Returns a list of subclasses by class."""
        return list(self.srd["classes"][klass]["subclasses"])

    def getTraitsBySpecies(self, species: str) -> List[str]:
        """Returns a list of traits by species."""
        return list(self.srd["species"][species]["traits"])

    def getWeaponProficienciesByClass(self, klass: str) -> List[str]:
        """Returns weapon proficiencies by class."""
        return self.srd["classes"][klass]["weapons"]

    @staticmethod
    def isPreparedCaster(klass: str) -> bool:
        """Returns True if caster is a member of a prepared spells class."""
        if klass in ("Artificer", "Cleric", "Druid", "Paladin", "Wizard"):
            return True
        return False
