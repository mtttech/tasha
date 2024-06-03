from typing import Any, Dict, Iterable, List, Union


def capitalize(string: Union[List[str], str]) -> str:
    """Capitalize the first letter of all words with the exception of certain words."""
    if isinstance(string, str):
        string = string.split(" ")

    if string[0] == "the":
        string[0] = string[0].capitalize()

    return " ".join(
        [
            (
                w.capitalize()
                if w not in ("and", "of", "or", "the", "to", "via", "with")
                else w
            )
            for w in string
        ]
    )


def populate_completer(options: Iterable[Any]) -> Dict[str, Any]:
    """Returns a dictionary of applicable selections for the NestedCompleter."""
    options = [o.lower() for o in options if isinstance(o, str)]
    filler = [None for _ in options]
    return dict(zip(options, filler))