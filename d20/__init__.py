import itertools
from typing import Any, Dict, List, Tuple, Union

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

    def calculateAllottedAsi(self, klasses: Dict[str, Any]) -> int:
        """Returns the number of allotted ability score improvements."""
        allotted_asi = 0
        for klass in tuple(klasses.keys()):
            class_features = self.getEntryByClass(klass)["features"]
            for level, _ in class_features.items():
                if level > klasses[klass]["level"]:
                    break
                if "Ability Score Improvement" in class_features[level]:
                    allotted_asi += 1
        return allotted_asi

    def getClassSpellList(
        self, klass: str, spell_level: int, subklass=None
    ) -> List[str]:
        try:
            if subklass in (
                "Arcane Trickster",
                "Eldritch Knight",
            ):
                spell_list_by_level = self.srd["spells"][subklass][spell_level]
            else:
                spell_list_by_level = self.srd["spells"][klass][spell_level]
            if len(spell_list_by_level) == 0:
                raise KeyError

            return [f"{s} (lv. {spell_level})" for s in spell_list_by_level]
        except KeyError:
            return list()

    def getEntryByClass(self, klass: str) -> Dict[str, Any]:
        """Returns SRD entries by the chosen class."""
        try:
            return self.srd["classes"][klass]
        except KeyError:
            raise ValueError(f"Cannot find an entry for the '{klass}' class.")

    def getEntryByMulticlass(self, klass: str) -> Dict[str, Any]:
        """Returns SRD entries for multiclassing by the chosen class."""
        try:
            return self.srd["multiclasses"][klass]
        except KeyError:
            raise ValueError(f"Cannot find an entry for the '{klass}' multiclass.")

    def getHitDieByClass(self, klass: str) -> int:
        """Returns the hit die for the specified class."""
        try:
            return self.srd["classes"][klass]["hit_die"]
        except KeyError:
            return 6

    def getAlignments(self) -> List[str]:
        """Returns a list of all applicable alignments."""
        return self.srd["alignments"]

    def getAbilityByBackground(self, background: str) -> List[str]:
        """Returns a list of abilities by background."""
        return self.srd["backgrounds"][background]["ability"]

    def getBackgrounds(self) -> List[str]:
        """Returns a list of all applicable backgrounds."""
        return list(self.srd["backgrounds"].keys())

    def getListCantrips(
        self, klass: str, subklass: Union[str, None] = None
    ) -> List[str]:
        """Returns a list of cantrips available by class/subclass."""
        return self.getClassSpellList(klass, 0, subklass)

    def getArmorProficienciesByClass(self, klass: str) -> List[str]:
        """Returns armor proficiencies by class."""
        return self.srd["classes"][klass]["armors"]

    def getClasses(self) -> List[str]:
        """Returns a tuple of all applicable classes."""
        return list(self.srd["classes"].keys())

    def getFeats(self, exclusions: Union[List[str], None] = None) -> List[str]:
        """Returns a list of all applicable feats."""
        feat_list = list(self.srd["feats"])
        if isinstance(exclusions, list):
            return [f for f in feat_list if f not in exclusions]
        return feat_list

    def getFeatsByCategory(self, category: str) -> List[str]:
        """Returns a list of all applicable feats."""
        requested_feats = list()
        for feat, params in self.srd["feats"].items():
            if params["category"] == category:
                requested_feats.append(feat)
        return requested_feats

    def getFeaturesByClass(self, klass: str, class_level: int) -> List[str]:
        """Returns class features by class."""
        class_features = list()
        for level, features in self.srd["classes"][klass]["features"].items():
            if class_level >= level:
                class_features = class_features + features
        return class_features

    def getRareLanguages(self, excl: Union[List[str], None] = None) -> List[str]:
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

    def getSkillsByBackground(self, background: str) -> List[str]:
        """Returns a list of skills by background."""
        return self.srd["backgrounds"][background]["skills"]

    def getSkillsByClass(
        self, klass: str, excl: Union[List[str], None] = None
    ) -> List[str]:
        """Returns all skills by class."""
        class_skills = self.srd["classes"][klass]["skills"]
        if isinstance(excl, list):
            return [s for s in class_skills if s not in excl]
        return class_skills

    def getSpeedBySpecies(self, species: str) -> List[str]:
        """Returns speed (in feet) by species."""
        return self.srd["species"][species]["speed"]

    def getStandardLanguages(self, excl: Union[List[str], None] = None) -> List[str]:
        """Returns all standard languages (minus exclusions, if applicable)."""
        language_list = self.srd["languages"]["standard"]
        if isinstance(excl, list):
            return [l for l in language_list if l not in excl]
        return language_list

    def getToolsByBackground(self, background: str) -> List[str]:
        """Returns a list of all tool proficiencies by background."""
        return self.srd["backgrounds"][background]["tools"]

    def getListMulticlasses(
        self,
        klasses: Tuple[str, ...],
        level: int,
        attributes: Dict[str, Dict[str, int]],
    ) -> Union[List[str], Tuple[str, ...]]:
        """Returns a list of available classes for multiclassing."""

        def is_selectable_class(klass: str) -> bool:
            if klass not in klasses:
                required_attributes = self.getEntryByMulticlass(klass)["requirements"]
                for attribute in tuple(required_attributes.keys()):
                    if attributes[attribute]["score"] < required_attributes[attribute]:
                        return False
            return True

        if level == 20:
            return ()

        return tuple([k for k in self.getClasses() if is_selectable_class(k)])

    def getSpecies(self) -> List[str]:
        """Returns a tuple of all applicable races."""
        return list(self.srd["species"].keys())

    def getListSkills(self, excl: Union[List[str], None] = None) -> List[str]:
        """Returns a list of all skills, excluding any specified exclusions."""
        all_skills = list(self.srd["skills"].keys())
        if isinstance(excl, list):
            all_skills = [s for s in all_skills if s not in excl]
        return all_skills

    def getListSpells(self, klass: str, subklass: str, level: int) -> List[str]:
        """Returns a list of available spells by available spell slots."""
        max_spell_level = self.srd["classes"][klass]["spell_slots"][level].split(",")
        spell_list = []

        for spell_level in range(0, len(max_spell_level)):
            if spell_level == 0:
                continue

            spell_list += self.getClassSpellList(klass, spell_level, subklass)

        return spell_list

    def getSubclassesByClass(self, klass: str) -> List[str]:
        """Returns a list of subclasses by class."""
        return list(self.srd["classes"][klass]["subclasses"])

    def getToolProficiencies(
        self,
        excl: Union[List[str], None] = None,
        startswith: Union[str, None] = None,
    ) -> List[str]:
        """Returns all tool proficiencies minus exclusions, if applicable."""
        tool_proficiencies = self.srd["proficiencies"]["tools"]
        if isinstance(excl, list):
            tool_proficiencies = [t for t in tool_proficiencies if t not in excl]
        if isinstance(startswith, str):
            tool_proficiencies = [
                t for t in tool_proficiencies if t.startswith(startswith)
            ]
        return tool_proficiencies

    def getTraitsBySpecies(self, species: str) -> List[str]:
        """Returns a list of traits by species."""
        return list(self.srd["species"][species]["traits"])

    def getListWeapons(self, excluded: Union[List[str], None] = None) -> List[str]:
        """Returns a list of weapons, ignoring those in the excluded list."""
        weapons_as_dict = self.srd["proficiencies"]["weapons"]
        martial, simple = weapons_as_dict.values()
        all_weapons = sorted(itertools.chain(martial, simple))

        if isinstance(excluded, list):
            if "Simple" in excluded:
                all_weapons = [
                    w for w in all_weapons if w not in weapons_as_dict["Simple"]
                ]

            if "Martial" in excluded:
                all_weapons = [
                    w for w in all_weapons if w not in weapons_as_dict["Martial"]
                ]

            all_weapons = [
                w
                for w in all_weapons
                if w not in excluded and w not in ("Martial", "Simple")
            ]

        return all_weapons

    def getSkillAbility(self, skill: str) -> str:
        """Returns the associated ability for a skill."""
        try:
            return self.srd["skills"][skill]["ability"]
        except KeyError:
            return ""

    def getSpellSlots(
        self, klasses: Dict[str, Dict[str, Any]], total_level: int
    ) -> List[int]:
        """Returns a list of allotted spell slots by klass and level."""
        from math import ceil

        classes = tuple(klasses.keys())
        spell_slots = []
        if len(classes) == 1:
            spell_slots = self.srd["classes"][classes[0]]["spell_slots"][
                total_level
            ].split(",")
        elif len(classes) > 1:
            actual_level = 0
            for klass in classes:
                if klass in ("Bard", "Cleric", "Druid", "Sorcerer", "Wizard"):
                    actual_level += klasses[klass]["level"]
                elif klass in ("Artificer", "Paladin", "Ranger"):
                    actual_level += ceil(klasses[klass]["level"] / 2)
                elif klass in ("Fighter", "Rogue"):
                    actual_level += ceil(klasses[klass]["level"] / 3)

            spell_slots = self.srd["classes"]["Bard"]["spell_slots"][
                actual_level
            ].split(",")

        return [int(s) for s in spell_slots] if len(spell_slots) > 0 else spell_slots

    def getSpellTotal(self, klass: str, level: int, modifier: int) -> int:
        """Returns the total number of known or prepared spells."""
        if self.isPreparedCaster(klass):
            number_of_prepared_spells = level + modifier
            return 1 if number_of_prepared_spells < 1 else number_of_prepared_spells
        else:
            return self.getSpellsKnown(klass, level)

    def getSpellsKnown(self, klass: str, level: int) -> int:
        """Returns the number of known spells, if applicable."""
        try:
            return self.srd["classes"][klass]["spells_known"][level]
        except KeyError:
            return 0

    @staticmethod
    def isPreparedCaster(klass: str) -> bool:
        """Returns True if caster is a member of a prepared spells class."""
        if klass in ("Artificer", "Cleric", "Druid", "Paladin", "Wizard"):
            return True
        return False
