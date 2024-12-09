from pathlib import Path

import toml


class SettingsLoader:

    def __init__(self) -> None:
        """Loads the settings file."""
        settings_path = Path.home() / ".config" / "tasha" / "settings" / "default.toml"
        if settings_path.exists():
            with settings_path.open() as loaded_settings:
                default_settings = toml.loads(loaded_settings.read())

            self.default_theme = default_settings["default_theme"]
