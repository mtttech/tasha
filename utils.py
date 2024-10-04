from typing import Dict, List


def stdin(options: List[str] | int, loop_count=1) -> List[str]:
    """Used to capture user input."""

    def associate_option_indexes() -> Dict[int, str]:
        indexed_options = dict()
        for index, option in enumerate(options):  # pyright: ignore
            indexed_options[index + 1] = option
        return indexed_options

    if isinstance(options, int):
        options = list(str(n + 1) for n in range(options))

    selections = list()
    for _ in range(0, loop_count):
        expanded_options = associate_option_indexes()
        if len(expanded_options) == loop_count:
            return list(expanded_options.values())

        option_keys = list(expanded_options.keys())
        first_option = option_keys[0]
        last_option = option_keys[-1]
        message = f"Make a selection {first_option}-{last_option}.\n\n"
        for index, option in expanded_options.items():
            message += f"\t{index}.) {option}\n"
        message += "\n>> "

        user_input = input(message)
        try:
            chosen_option = expanded_options[int(user_input)]
            # Hax to keep this feat selectable multiple times.
            if chosen_option != "Ability Score Improvement":
                selections.append(chosen_option)
                options.remove(chosen_option)
        except (KeyError, TypeError, ValueError):
            return stdin(options)

    return selections
