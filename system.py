from collections.abc import Generator
from enum import Enum
import itertools
from typing import Any, Dict, List, Tuple, Union

from d20 import srd5e


class _SRDBuilder(Enum):
    alignments: object = srd5e["alignments"]
    backgrounds: object = srd5e["backgrounds"]
    classes: object = srd5e["classes"]
    feats: object = srd5e["feats"]
    languages: object = srd5e["languages"]
    lineages: object = srd5e["lineages"]
    multiclasses: object = srd5e["multiclasses"]
    proficiencies: object = srd5e["proficiencies"]
    species: object = srd5e["species"]
    skills: object = srd5e["skills"]
    spells: object = srd5e["spells"]
    subclasses: object = srd5e["subclasses"]


class SystemResourceDocument:
    def __init__(self) -> None:
        self.srd = dict(
            zip(
                [
                    "alignments",
                    "backgrounds",
                    "classes",
                    "feats",
                    "languages",
                    "lineages",
                    "multiclasses",
                    "proficiencies",
                    "species",
                    "skills",
                    "spells",
                    "subclasses",
                ],
                [d for d in self._load_definitions()],
            )
        )

    @staticmethod
    def _load_definitions() -> Generator:
        """Loads dnd SRD definitions."""
        for definition in _SRDBuilder:
            value = definition.value
            if isinstance(value, list):
                value = sorted(value)
            yield value

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

    def getAnthropometryBase(self, race: str, subrace: str = "") -> Tuple[str, str]:
        """get the base height/weight metrics using character's race."""
        base_height = self.getAnthropometryBaseHeight(race)
        base_weight = self.getAnthropometryBaseWeight(race)
        if base_height is None or base_weight is None:
            base_height = self.getAnthropometryBaseHeight(subrace)
            base_weight = self.getAnthropometryBaseWeight(subrace)
        if base_height is None or base_weight is None:
            raise ValueError("No racial/subracial base metric data found.")
        return (base_height, base_weight)

    def getAnthropometryBaseHeight(self, race: str) -> Union[str, None]:
        """Returns the base height values by race."""
        try:
            return self.srd["metrics"][race]["height"]
        except KeyError:
            return None

    def getAnthropometryBaseWeight(self, race: str) -> Union[str, None]:
        """Returns the base weight values by race."""
        try:
            return self.srd["metrics"][race]["weight"]
        except KeyError:
            return None

    def getAnthropometryDominantSex(self, race: str) -> str:
        """Returns the 'dominant' gender by race, if applicable."""
        try:
            return self.srd["metrics"][race]["dominant"]
        except KeyError:
            return ""

    def getAnthropometrySource(self, race: str, subrace: str = "") -> str:
        """Returns the name of the race or subrace the metric data belongs to."""
        if (result := self.getMetricsByRace(race)) is None:
            result = self.getMetricsByRace(subrace)
            if result is not None:
                return subrace
            else:
                raise ValueError(
                    "No racial/subracial metric data source could be determined."
                )
        return race

    def getClassSkills(
        self, klass: str, exclusions: Union[List[str], None] = None
    ) -> List[str]:
        """Returns a list of all applicable skills by class."""
        class_skills = self.srd["classes"][klass]["skills"]
        if isinstance(exclusions, list):
            return [s for s in class_skills if s not in exclusions]
        return class_skills

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

    def getEntryByBackground(self, background: str) -> Dict[str, Any]:
        """Returns SRD entries by the chosen background."""
        try:
            return self.srd["backgrounds"][background]
        except KeyError:
            raise ValueError(f"Cannot find an entry for the '{background}' background.")

    def getEntryByClass(self, klass: str) -> Dict[str, Any]:
        """Returns SRD entries by the chosen class."""
        try:
            return self.srd["classes"][klass]
        except KeyError:
            raise ValueError(f"Cannot find an entry for the '{klass}' class.")

    def getEntryByFeat(self, feat: str) -> Dict[str, Any]:
        """Returns SRD entries by the chosen feat."""
        try:
            return self.srd["feats"][feat]
        except KeyError:
            raise ValueError(f"Cannot find an entry for the '{feat}' feat.")

    def getEntryByMulticlass(self, klass: str) -> Dict[str, Any]:
        """Returns SRD entries for multiclassing by the chosen class."""
        try:
            return self.srd["multiclasses"][klass]
        except KeyError:
            raise ValueError(f"Cannot find an entry for the '{klass}' multiclass.")

    def getEntryByProficiency(self, category: str) -> Dict[str, Any]:
        """Returns SRD entries by proficiency category (armors, tools, weapons)."""
        try:
            return self.srd["proficiencies"][category]
        except KeyError:
            raise ValueError(
                f"Cannot find an entry for the '{category}' proficiencies."
            )

    def getEntryBySpecies(self, species: str) -> Dict[str, Any]:
        """Returns SRD entries by the chosen species."""
        try:
            return self.srd["species"][species]
        except KeyError:
            raise ValueError(f"Cannot find an entry for the '{species}' species.")

    def getEntryBySubclass(self, subclass: str) -> Dict[str, Any]:
        """Returns SRD entries by the chosen subclass."""
        try:
            return self.srd["subclasses"][subclass]
        except KeyError:
            raise ValueError(f"Cannot find an entry for the '{subclass}' subclass.")

    def getEntryByLineage(self, lineage: str) -> Dict[str, Any]:
        """Returns SRD entries by the chosen subrace."""
        try:
            return self.srd["lineages"][lineage]
        except KeyError:
            raise ValueError(f"Cannot find an entry for the '{lineage}' lineage.")

    def getFeaturesByClass(self, klass: str, level: int) -> List[str]:
        """Returns features by class/subclass and level."""
        try:
            class_features = self.srd["classes"][klass]["features"]
        except KeyError:
            try:
                class_features = self.srd["classes"][klass]["features"]
            except KeyError:
                return []

        class_features = list(
            {k: v for k, v in class_features.items() if k <= level}.values()
        )

        return list(itertools.chain(*class_features))

    def getHitDieByClass(self, klass: str) -> int:
        """Returns the hit die for the specified class."""
        try:
            return self.srd["classes"][klass]["hit_die"]
        except KeyError:
            return 6

    def getListAlignments(self) -> List[str]:
        """Returns a list of all applicable alignments."""
        return self.srd["alignments"]

    def getBackgrounds(self) -> List[str]:
        """Returns a list of all applicable backgrounds."""
        return list(self.srd["backgrounds"].keys())

    def getListCantrips(
        self, klass: str, subklass: Union[str, None] = None
    ) -> List[str]:
        """Returns a list of cantrips available by class/subclass."""
        return self.getClassSpellList(klass, 0, subklass)

    def getClasses(self) -> List[str]:
        """Returns a tuple of all applicable classes."""
        return list(self.srd["classes"].keys())

    def getListFeats(self, exclusions: Union[List[str], None] = None) -> List[str]:
        """Returns a list of all applicable feats."""
        feat_list = list(self.srd["feats"])
        if isinstance(exclusions, list):
            return [f for f in feat_list if f not in exclusions]
        return feat_list

    def getRareLanguages(self, excl: Union[List[str], None] = None) -> List[str]:
        """Returns all rare languages (minus exclusions, if applicable)."""
        language_list = self.srd["languages"]["rare"]
        if isinstance(excl, list):
            return [l for l in language_list if l not in excl]
        return language_list

    def getStandardLanguages(self, excl: Union[List[str], None] = None) -> List[str]:
        """Returns all standard languages (minus exclusions, if applicable)."""
        language_list = self.srd["languages"]["standard"]
        if isinstance(excl, list):
            return [l for l in language_list if l not in excl]
        return language_list

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

    def getListSubclasses(self, klass=None) -> Tuple[Any, ...]:
        """Returns a tuple of all applicable subclasses."""
        try:
            return tuple(self.srd["classes"][klass]["subclass"])
        except KeyError:
            return tuple(self.srd["subclasses"].keys())

    def getLineages(self, species=None) -> Tuple[str, ...]:
        """Returns a tuple of all applicable lineages."""
        try:
            return tuple(self.srd["species"][species]["lineage"])
        except KeyError:
            return tuple(self.srd["lineages"].keys())

    def getListTools(
        self,
        exclusions: Union[List[str], None] = None,
        startswith: Union[str, None] = None,
    ) -> List[str]:
        """Returns a tuple of all applicable tool proficiencies minus exclusions, if applicable."""
        tool_proficiencies = self.srd["proficiencies"]["tools"]
        if isinstance(exclusions, list):
            tool_proficiencies = [t for t in tool_proficiencies if t not in exclusions]
        if isinstance(startswith, str):
            tool_proficiencies = [
                t for t in tool_proficiencies if t.startswith(startswith)
            ]
        return tool_proficiencies

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

    def getMetricsByRace(self, race: str) -> Union[Dict[str, str], None]:
        """Returns metric data by race."""
        try:
            return self.srd["metrics"][race]
        except KeyError:
            return None

    def getRacialMagic(self, race: str, caster_level: int) -> List[str]:
        """Returns racial magic spells by race/subclass, if applicable."""
        actual_race = race.split(", ")
        if len(actual_race) > 1:
            spells = self.srd["subraces"][actual_race[1]]["spells"]
        else:
            spells = self.srd["races"][actual_race[0]]["spells"]

        if len(spells) == 0:
            return []

        spell_list = list()
        for level, spell_list_by_level in spells.items():
            if level > caster_level:
                break
            if caster_level >= level:
                spell_list += spell_list_by_level
        return spell_list

    def getSkillAbility(self, skill: str) -> str:
        """Returns the associated ability for a skill."""
        try:
            return self.srd["skills"]["ability"]
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
