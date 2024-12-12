from pathlib import Path
from typing import Dict

import toml


class ThemeLoader:

    def __init__(self, theme_file: str | None = None) -> None:
        """Handles the loading of tasha's themes.

        Args:
            theme_file (str): Theme file to load."""
        theme_dir = Path.home() / ".config" / "tasha" / "themes"
        if not theme_dir.exists():
            raise FileNotFoundError("Cannot locate tasha's theme directory.")

        if theme_file is not None:
            theme_path = theme_dir / f"{theme_file}.toml"
            if theme_path.exists():
                self.current_theme_path = theme_path
        else:
            self.current_theme_path = theme_dir / "default.toml"

    def load(self) -> Dict[str, str]:
        """Loads the set theme file.

        Returns:
            Dict[str, str]: Toml theme file loaded in dict format."""
        with self.current_theme_path.open() as loaded_theme:
            return toml.loads(loaded_theme.read())
