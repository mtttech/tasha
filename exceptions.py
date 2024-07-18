class NoSelectionError(Exception):
    """Raised if the user makes no selection when required."""


class SelectionLimitError(Exception):
    """Raised if the user doesn't select the required number of selections."""
