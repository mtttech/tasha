from typing import Dict, List


def stdin(message: str, options: List[str]) -> str:
    """Used to captured user input."""

    def expand_options() -> Dict[int, str]:
        expanded_options = dict()
        for index, option in enumerate(options):
            expanded_options[index + 1] = option
        return expanded_options

    expanded_options = expand_options()

    option_keys = list(expanded_options.keys())
    first_option = option_keys[0]
    last_option = option_keys[-1]
    message = f"{message} (Make a selection {first_option}-{last_option}).\n\n"
    for index, option in expanded_options.items():
        message += f"\t{index}.) {option}\n"
    message += "\n>> "

    user_input = input(message)
    try:
        chosen_option = expanded_options[int(user_input)]
    except (KeyError, TypeError):
        return stdin(message, options)
    return chosen_option
