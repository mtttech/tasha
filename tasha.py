from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

from simple_term_menu import TerminalMenu
import toml

from actor import CharacterSheet, NonPlayerCharacter
from attributes import Attributes, Score, generate_attributes, get_modifier
from exceptions import NoSelectionError, RequiredLimitError
from system import SystemResourceDocument


__author__ = "Marcus T Taylor"
__email__ = "mtaylor9754@hotmail.com"
__version__ = "0.5.2"


oSheet = CharacterSheet()
oNPC = NonPlayerCharacter(oSheet)
oSRD = SystemResourceDocument()
level_range = [str(l) for l in list(range(1, 31))]


character_dir = Path.home() / ".config" / "tasha" / "characters"
if not character_dir.exists():
    character_dir.mkdir(parents=True)
    print("character save directory created.")


def attribute_assign_menu(rolls: List[str]) -> Dict[str, Dict[str, int]]:
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
        score = single_select_menu(rolls, f"Attribute -> {attribute}")
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
    while True:
        threshold_range = [str(t) for t in list(range(60, 91))]
        threshold = single_select_menu(threshold_range, "Attribute Threshold")
        rolls = [str(n) for n in generate_attributes(int(threshold))]
        if not confirm_yesno_menu("Are these scores acceptable? " + " | ".join(rolls)):
            continue
        else:
            return attribute_assign_menu(rolls)


def confirm_upgrade_menu() -> int | Tuple[int, ...] | None:
    menu = TerminalMenu(
        ["Attribute", "Feat"], title="Ability Score Improvement Upgrade"
    )
    return menu.show()


def confirm_yesno_menu(message: str) -> bool:
    menu = TerminalMenu(["No", "Yes"], title=message)
    if menu.show() != 0:
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
    allotted_options: list, title: str, required_num_of_selections: int = 0
) -> Tuple[str, ...] | None:
    while True:
        menu = TerminalMenu(
            allotted_options,
            multi_select=True,
            multi_select_select_on_accept=False,
            multi_select_empty_ok=True,
            show_multi_select_hint=True,
            title=(
                f"{title} Select ({required_num_of_selections})"
                if required_num_of_selections != 0
                else f"{title} Select"
            ),
        )
        menu.show()
        menu_selections = menu.chosen_menu_entries
        if required_num_of_selections != 0:
            if (
                len(menu_selections)  # pyright: ignore[reportArgumentType]
                != required_num_of_selections
            ):
                raise RequiredLimitError  # Less selections than required.

        try:
            if len(menu_selections) == 0:  # pyright: ignore[reportArgumentType]
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
    menu = TerminalMenu(
        allotted_options,
        status_bar=f"Please select your {title}.",
        title=f"{title} Selection",
    )
    return allotted_options[
        menu.show()
    ]  # pyright: ignore[reportArgumentType, reportCallIssue]


def spellcasting_select_menu(klass: str, level: int) -> Dict[str, Any]:
    """Prompt for selecting character spells."""
    # Get the total number of known/prepared spells.
    allotted_spell_total = oSRD.getSpellTotal(
        klass,
        level,
        get_modifier(oNPC.getCasterAttribute(klass)),
    )
    allotted_spell_total = 7
    # Set the selection counter.
    selection_counter = allotted_spell_total
    # Grab a listing of spells the player can pick from.
    available_selections = oSRD.getSpellsByClass(klass, level)

    selected_spells = list()
    for _ in range(0, allotted_spell_total):
        spell = single_select_menu(
            available_selections, f"Choose a known/prepared spell ({selection_counter})"
        )
        selected_spells.append(spell)
        available_selections.remove(spell)
        # Adjust warlock Arcanum spell selections, if warlock.
        if klass == "Warlock":
            available_selections = setArcanumSpells(
                selected_spells, available_selections
            )
        selection_counter -= 1

    return {klass: selected_spells}


def main() -> None:
    oSheet.set("name", name_entry())
    oSheet.set("alignment", single_select_menu(oSRD.getListAlignments(), "Alignment"))
    oSheet.set("type_", single_select_menu(oSRD.getListTypes(), "Type"))
    oSheet.set("gender", single_select_menu(["Female", "Male"], "Gender"))
    oSheet.set("attributes", attribute_generate_menu())

    size = single_select_menu(oSRD.getListSizes(), "Size")
    oSheet.set("size", size)
    oSheet.set("hit_die", oSRD.getHitDieBySize(size))
    oSheet.set("hit_points", hit_dice_menu(size))

    oSheet.set("senses", multi_select_menu(oSRD.getListSenses(), "Senses"))
    oSheet.set("features", multi_select_menu(oSRD.getListFeatures(), "Features"))
    savingthrows = multi_select_menu(
        [
            "Strength",
            "Dexterity",
            "Constitution",
            "Intelligence",
            "Wisdom",
            "Charisma",
        ],
        "Saving Throw Proficiency",
    )
    oSheet.set(
        "savingthrows", list(savingthrows)  # pyright: ignore[reportArgumentType]
    )

    armors = multi_select_menu(oSRD.getListArmors(), "Armor Proficiency")
    oSheet.set("armors", list(armors))  # pyright: ignore[reportArgumentType]

    tools = multi_select_menu(oSRD.getListTools(), "Tool Proficiency")
    oSheet.set("tools", list(tools))  # pyright: ignore[reportArgumentType]

    weapons = multi_select_menu(oSRD.getListWeapons(), "Weapon Proficiency")
    oSheet.set("weapons", list(weapons))  # pyright: ignore[reportArgumentType]

    skills = multi_select_menu(oSRD.getListSkills(), "Skill")
    oSheet.set("skills", list(skills))  # pyright: ignore[reportArgumentType]

    languages = multi_select_menu(oSRD.getListLanguages(), "Language")
    oSheet.set("languages", list(languages))  # pyright: ignore[reportArgumentType]

    if confirm_yesno_menu("Are you a spellcaster?"):
        spellcaster_klass = single_select_menu(
            oSRD.getListClasses(), "Spellcasting Class"
        )
        caster_level = int(
            single_select_menu(level_range, "What is your caster level?")
        )
        oSheet.set(
            "spell_slots", oSRD.getSpellSlotsByClass(spellcaster_klass, caster_level)
        )
        oSheet.set(
            "spellcasting", spellcasting_select_menu(spellcaster_klass, caster_level)
        )

    cs = CharacterSheet(**asdict(oSheet))
    #print(cs)
    fname = f"{oNPC.getMyName()}.toml"
    with Path(character_dir, fname).open("w") as record:
        toml.dump(asdict(cs), record)
        print(f"{fname} created successfully.")
        print(f"{fname} saved to {character_dir}.")


if __name__ == "__main__":
    main()
