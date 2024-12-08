from pathlib import Path


def init() -> None:
    """Initializes the tasha program. Creates necessary app directories."""
    config_dir = Path.home() / ".config" / "tasha"
    character_dir = config_dir / "characters"

    if not character_dir.exists():
        character_dir.mkdir(parents=True)
        # print("Created the character directory.")

    import toml

    themes_dir = config_dir / "themes"
    if not themes_dir.exists():
        themes_dir.mkdir(parents=True)
        # print("Created the theme directory.")

        with Path(themes_dir, "default.toml").open("w") as default_theme:
            toml.dump(
                {
                    "default": "bold green",
                    "exit": "bold dim red",
                    "menu.index": "bold italic cyan",
                    "menu.option": "bold magenta",
                    "prompt": "bold dim green",
                },
                default_theme,
            )
            # print("Created the default theme TOML file.")

    settings_dir = config_dir / "settings"
    if not settings_dir.exists():
        settings_dir.mkdir(parents=True)
        # print("Created the settings directory.")

        with Path(settings_dir, "default.toml").open("w") as default_settings:
            toml.dump(
                {
                    "default_theme": "default",
                },
                default_settings,
            )


init()
