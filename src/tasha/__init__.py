from pathlib import Path


def init() -> None:
    """Initializes the tasha program. Creates necessary app directories."""
    config_dir = Path.home() / ".config" / "tasha"
    character_dir = config_dir / "characters"

    if not character_dir.exists():
        character_dir.mkdir(parents=True)
        print("Created the characters save directory.")


init()
