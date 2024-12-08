from typing import Dict


class SettingsLoader:

    def __init__(self) -> None:
        """Loads the settings file."""
        from pathlib import Path

        import toml

        settings_path = Path.home() / ".config" / "tasha" / "settings" / "default.toml"
        if settings_path.exists():
            with settings_path.open() as loaded_settings:
                default_settings = toml.loads(loaded_settings.read())

            self.default_theme = default_settings["default_theme"]
