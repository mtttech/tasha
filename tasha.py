from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Iterable, Tuple

from simple_term_menu import TerminalMenu
import toml

from actor import CharacterSheet, NonPlayerCharacter
from attributes import Attributes, Score, generate_attributes, get_modifier
from exceptions import NoSelectionError, SelectionLimitError
from system import SystemResourceDocument


__author__ = "Marcus T Taylor"
__email__ = "mtaylor9754@hotmail.com"
__version__ = "0.5.3"


oSheet = CharacterSheet()
oNPC = NonPlayerCharacter(oSheet)
oSRD = SystemResourceDocument()
level_range = [str(l) for l in list(range(1, 31))]


character_dir = Path.home() / ".config" / "tasha" / "characters"
if not character_dir.exists():
    character_dir.mkdir(parents=True)
    print("character save directory created.")


class TashaMultiMenu(TerminalMenu):
    def __init__(self, options: Iterable[str], message: str) -> None:
        super().__init__(
            options,
            clear_screen=True,
            multi_select=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True,
            raise_error_on_interrupt=True,
            status_bar=message,
            title=f"  Tasha {__version__}\n  {message}\n",
        )


class TashaSingleMenu(TerminalMenu):
    def __init__(self, options: Iterable[str], message: str) -> None:
        super().__init__(
            options,
            clear_screen=True,
            raise_error_on_interrupt=True,
            status_bar=message,
            title=f"  Tasha {__version__}\n  {message}\n",
        )


def attribute_assign_menu(rolls: List[str]) -> Dict[str, Dict[str, int]]:
    """Prompt for assigning the six character attributes."""
    attributes = [
        "Strength",
        "Dexterity",
        "Constitution",
        "Intelligence",
        "Wisdom",
        "Charisma",
    ]
    assigned_attributes = dict()
    for attribute in attributes:
        score = single_select_menu(
            rolls, f"Please assign a value to your '{attribute}' attribute."
        )
        attr_pair = asdict(Score(attribute, int(score)))
        del attr_pair["attribute"]
        del attr_pair["bonus"]
        assigned_attributes[attribute] = attr_pair
        rolls.remove(score)

    if confirm_yesno_menu("Would you like to adjust your attributes?"):
        while True:
            attribute = single_select_menu(attributes, "Adjust Attribute")
            current_value = assigned_attributes[attribute]["score"]
            print(f"Your current {attribute} score is {current_value}.")

            if current_value == 30:
                raise ValueError  # Can't upgrade value anymore!

            adjustable_value = 30 - current_value
            adjustable_threshold = list(range(1, adjustable_value + 1))
            adjustable_threshold = [str(t) for t in adjustable_threshold]

            adjustment_value = single_select_menu(
                adjustable_threshold, f"Adjust Attribute -> {attribute}"
            )
            Attributes(assigned_attributes).add(attribute, int(adjustment_value))
            print(assigned_attributes)

            if confirm_yesno_menu("Are you finished adjusting your attributes?"):
                break

    return assigned_attributes


def attribute_generate_menu() -> Dict[str, Dict[str, int]]:
    """Prompt for randomly generating the six attributes."""
    while True:
        threshold_range = [str(t) for t in list(range(60, 91))]
        threshold = single_select_menu(
            threshold_range, "Please select your attribute threshold."
        )
        rolls = [str(n) for n in generate_attributes(int(threshold))]
        if not confirm_yesno_menu(
            "Are these scores acceptable: {}?".format(", ".join(rolls))
        ):
            continue
        else:
            return attribute_assign_menu(rolls)


def confirm_upgrade_menu() -> int | Tuple[int, ...] | None:
    upgrade_menu = TashaSingleMenu(
        ["Attribute", "Feat"],
        "Ability Score Improvement Upgrade",
    )
    return upgrade_menu.show()


def confirm_yesno_menu(message: str) -> bool:
    yesno_menu = TashaSingleMenu(
        ["No", "Yes"],
        message,
    )
    if yesno_menu.show() != 0:
        return True
    return False


def hit_dice_menu(size: str) -> int:
    import math

    hit_dice = int(single_select_menu(level_range, "# of Hit Dice"))
    hit_die = (oSRD.getHitDieBySize(size) / 2) + 0.5
    modifier = oNPC.getAttributeModifier("Constitution")
    oSheet.set("level", hit_dice)
    return int(math.floor((hit_die * hit_dice) + (modifier * hit_dice)))


def multi_select_menu(
    allotted_options: list, message: str, required_num_of_selections: int = 0
) -> Tuple[str, ...] | None:
    while True:
        menu = TashaMultiMenu(
            allotted_options,
            (
                f"{message} ({required_num_of_selections})\n"
                if required_num_of_selections != 0
                else f"{message}\n"
            ),
        )
        menu.show()
        menu_selections = menu.chosen_menu_entries
        if required_num_of_selections != 0:
            if len(menu_selections) != required_num_of_selections:  # pyright: ignore
                raise SelectionLimitError  # Less selections than required.

        try:
            if len(menu_selections) == 0:  # pyright: ignore
                raise NoSelectionError  # No selections made.
        except TypeError:
            return tuple()

        return menu_selections


def name_entry() -> str:
    try:
        while True:
            name = input("Name ")
            if name != "":
                return name
    except KeyboardInterrupt:
        print()
        exit(1)


def setArcanumSpells(
    players_spell_list: List[str], warlock_spells: List[str]
) -> List[str]:
    """Returns available warlock arcanum spells."""
    for spell_level in range(6, 10):
        for spell in players_spell_list:
            level_query = f"(lv. {spell_level})"
            if level_query in spell:
                warlock_spells = [s for s in warlock_spells if level_query not in s]

    return warlock_spells


def single_select_menu(allotted_options: list, title: str) -> str:
    select_menu = TashaSingleMenu(
        allotted_options,
        title,
    )
    return allotted_options[select_menu.show()]  # pyright: ignore


def spellcasting_select_menu(klass: str, class_level: int) -> Dict[str, Any]:
    """Prompt for selecting character spellcasting features."""
    allotted_spell_total = oSRD.getSpellTotal(
        klass,
        class_level,
        get_modifier(oNPC.getCasterAttribute(klass)),
    )
    spell_selection_counter = allotted_spell_total
    prepared_spells = list()

    while len(prepared_spells) < allotted_spell_total:
        spell_levels = [
            str(l + 1)
            for l, _ in enumerate(oSRD.getSpellSlotsByClass(klass, class_level)[1:])
        ]
        main_menu = TashaSingleMenu(spell_levels, "Spell Level Menu")
        main_menu_sel = main_menu.show()
        chosen_spell_level = int(spell_levels[main_menu_sel])  # pyright: ignore

        chosen_spell = None
        while chosen_spell is None:
            magic_spells = [
                s
                for s in oSRD.getSpellsByLevel(klass, chosen_spell_level)
                if s not in prepared_spells
            ]
            spell_menu = TashaSingleMenu(
                magic_spells,
                f"Level {chosen_spell_level} Spells ({spell_selection_counter})",
            )
            spell_menu_sel = spell_menu.show()

            chosen_spell = magic_spells[spell_menu_sel]  # pyright: ignore
            prepared_spells.append(chosen_spell)
            spell_selection_counter -= 1

    return {klass: prepared_spells}


def main() -> None:
    oSheet.set("name", name_entry())
    oSheet.set(
        "alignment",
        single_select_menu(oSRD.getListAlignments(), "Please select your alignment."),
    )
    oSheet.set(
        "type_",
        single_select_menu(oSRD.getListTypes(), "Please select your monster type."),
    )
    oSheet.set(
        "gender", single_select_menu(["Female", "Male"], "Please select your gender.")
    )
    oSheet.set("attributes", attribute_generate_menu())

    size = single_select_menu(oSRD.getListSizes(), "Please select your size.")
    oSheet.set("size", size)
    oSheet.set("hit_die", oSRD.getHitDieBySize(size))
    oSheet.set("hit_points", hit_dice_menu(size))

    oSheet.set(
        "senses", multi_select_menu(oSRD.getListSenses(), "Please select your senses.")
    )
    oSheet.set(
        "features",
        multi_select_menu(oSRD.getListFeatures(), "Please select your features."),
    )
    savingthrows = multi_select_menu(
        [
            "Strength",
            "Dexterity",
            "Constitution",
            "Intelligence",
            "Wisdom",
            "Charisma",
        ],
        "Please select your proficient saving throws.",
    )
    oSheet.set(
        "savingthrows", list(savingthrows)  # pyright: ignore[reportArgumentType]
    )

    armors = multi_select_menu(
        oSRD.getListArmors(), "Please select your armor proficiencies."
    )
    oSheet.set("armors", list(armors))  # pyright: ignore[reportArgumentType]

    tools = multi_select_menu(
        oSRD.getListTools(), "Please select your tool proficiencies."
    )
    oSheet.set("tools", list(tools))  # pyright: ignore[reportArgumentType]

    weapons = multi_select_menu(
        oSRD.getListWeapons(), "Please select your weapon proficiencies."
    )
    oSheet.set("weapons", list(weapons))  # pyright: ignore[reportArgumentType]

    skills = multi_select_menu(
        oSRD.getListSkills(), "Please select your proficient skills."
    )
    oSheet.set("skills", list(skills))  # pyright: ignore[reportArgumentType]

    languages = multi_select_menu(
        oSRD.getListLanguages(), "Please select your known languages."
    )
    oSheet.set("languages", list(languages))  # pyright: ignore[reportArgumentType]

    if confirm_yesno_menu("Are you a spellcaster?"):
        spellcaster_klass = single_select_menu(
            oSRD.getListClasses(), "Please select your spellcasting class."
        )
        caster_level = int(
            single_select_menu(level_range, "What is your spellcaster level?")
        )
        oSheet.set(
            "spell_slots", oSRD.getSpellSlotsByClass(spellcaster_klass, caster_level)
        )
        oSheet.set(
            "spellcasting", spellcasting_select_menu(spellcaster_klass, caster_level)
        )

    cs = CharacterSheet(**asdict(oSheet))
    # print(cs)
    fname = f"{oNPC.getMyName()}.toml"
    with Path(character_dir, fname).open("w") as record:
        toml.dump(asdict(cs), record)
        print(f"{fname} created successfully.")
        print(f"{fname} saved to {character_dir}.")


if __name__ == "__main__":
    main()
