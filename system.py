from enum import Enum
import itertools
from typing import Any, Dict, Generator, List, Union

from d20 import srd5e


class _SRDBuilder(Enum):
    alignments: object = srd5e["alignments"]
    classes: object = srd5e["classes"]
    features: object = srd5e["features"]
    languages: object = srd5e["languages"]
    metrics: object = srd5e["metrics"]
    proficiencies: object = srd5e["proficiencies"]
    senses: object = srd5e["senses"]
    sizes: object = srd5e["sizes"]
    skills: object = srd5e["skills"]
    spells: object = srd5e["spells"]
    types: object = srd5e["types"]


class SystemResourceDocument:
    def __init__(self) -> None:
        self.srd = dict(
            zip(
                [
                    "alignments",
                    "classes",
                    "features",
                    "languages",
                    "metrics",
                    "proficiencies",
                    "senses",
                    "sizes",
                    "skills",
                    "spells",
                    "types",
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

    def getCantripsByClass(self, klass: str) -> List[str]:
        """Returns all cantrips available to a class."""
        return self.getSpellsByLevel(klass, 0)

    def getEntryByClass(self, klass: str) -> Dict[str, Any]:
        """Returns SRD entries by the chosen class."""
        try:
            return self.srd["classes"][klass]
        except KeyError:
            raise ValueError(f"Cannot find an entry for the '{klass}' class.")

    def getEntryByProficiency(self, category: str) -> Dict[str, Any]:
        """Returns SRD entries by proficiency category (armors, tools, weapons)."""
        try:
            return self.srd["proficiencies"][category]
        except KeyError:
            raise ValueError(
                f"Cannot find an entry for the '{category}' proficiencies."
            )

    def getHitDieBySize(self, size: str) -> int:
        """Returns the hit die for the specified class."""
        try:
            return self.srd["sizes"][size]["hit_die"]
        except KeyError:
            return 6

    def getListAlignments(self) -> List[str]:
        """Returns a list of all applicable alignments."""
        return self.srd["alignments"]

    def getListArmors(
        self,
        exclusions: Union[List[str], None] = None,
        startswith: Union[str, None] = None,
    ) -> List[str]:
        """Returns a tuple of all applicable armor proficiencies minus exclusions, if applicable."""
        armor_proficiencies = self.srd["proficiencies"]["armors"]
        if isinstance(exclusions, list):
            armor_proficiencies = [
                a for a in armor_proficiencies if a not in exclusions
            ]
        if isinstance(startswith, str):
            armor_proficiencies = [
                a for a in armor_proficiencies if a.startswith(startswith)
            ]
        return armor_proficiencies

    def getListCantrips(self, klass: str) -> List[str]:
        """Returns a list of cantrips available by class/subclass."""
        return self.getSpellsByLevel(klass, 0)

    def getListClasses(self) -> List[str]:
        """Returns a tuple of all applicable classes."""
        return list(self.srd["classes"].keys())

    def getListFeatures(self) -> List[str]:
        """Returns a list of all applicable features."""
        return list(self.srd["features"].keys())

    def getListLanguages(self, exclusions: Union[List[str], None] = None) -> List[str]:
        """Returns a tuple of all applicable languages minus exclusions, if applicable."""
        if isinstance(exclusions, list):
            return [l for l in self.srd["languages"] if l not in exclusions]
        return self.srd["languages"]

    def getListSenses(self) -> List[str]:
        """Returns a list of all applicable senses."""
        return self.srd["senses"]

    def getListSizes(self) -> List[str]:
        """Returns a list of all applicable backgrounds."""
        return list(self.srd["sizes"].keys())

    def getListSkills(
        self, excluded_skills: Union[List[str], None] = None
    ) -> List[str]:
        """Returns a list of all skills, excluding any specified exclusions."""
        all_skills = list(self.srd["skills"].keys())
        if isinstance(excluded_skills, list):
            all_skills = [s for s in all_skills if s not in excluded_skills]
        return all_skills

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

    def getListTypes(self) -> List[str]:
        """Returns all available monster types."""
        return self.srd["types"]

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
            return self.srd["skills"]["ability"]
        except KeyError:
            return ""

    def getSpellsByLevel(self, klass: str, spell_level: int) -> List[str]:
        """Returns all spells available by klass and spell level."""
        try:
            spells_by_level = self.srd["spells"][klass][spell_level]
            return [f"{s} (lv. {spell_level})" for s in spells_by_level]
        except KeyError:
            return list()

    def getSpellSlotsByClass(self, klass: str, caster_level: int) -> List[int]:
        """Returns a list of allotted spell slots by klass and level."""
        from math import ceil

        if caster_level > 20:
            caster_level = 20

        spell_slots = []
        actual_level = 0
        if klass in ("Bard", "Cleric", "Druid", "Sorcerer", "Wizard"):
            actual_level += caster_level
        elif klass in ("Artificer", "Paladin", "Ranger"):
            actual_level += ceil(caster_level / 2)
        else:
            actual_level += ceil(caster_level / 3)
        spell_slots = self.srd["classes"][klass]["spell_slots"][actual_level].split(",")

        return [int(s) for s in spell_slots] if len(spell_slots) > 0 else spell_slots

    def getSpellTotal(self, klass: str, level: int, modifier: int) -> int:
        """Returns the allotted total number of availble known/prepared spells."""
        if self.isPreparedCaster(klass):
            number_of_prepared_spells = level + modifier
            return 1 if number_of_prepared_spells < 1 else number_of_prepared_spells
        else:
            return self.getSpellsKnown(klass, level)

    def getSpellsByClass(self, klass: str, caster_level: int) -> List[str]:
        """Returns all spells (1st - 9th) available to a class by its level."""
        if caster_level > 20:
            caster_level = 20

        spell_list = []
        spell_slots = self.srd["classes"][klass]["spell_slots"][caster_level].split(",")
        for level, _ in enumerate(spell_slots):
            if (
                level == 0
                or level == 0
                and klass
                in (
                    "Paladin",
                    "Ranger",
                )
            ):
                continue
            spell_list += self.getSpellsByLevel(klass, level)
        return spell_list

    def getSpellsKnown(self, klass: str, level: int) -> int:
        """Returns the allotted number of available known/prepared spells, if applicable."""
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
