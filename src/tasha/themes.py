from pathlib import Path
from typing import Dict

import toml


class ThemeLoader:

    @staticmethod
    def loadTheme(theme_file: str | None=None) -> Dict[str, str]:
        theme_dir = Path.home() / ".config" / "tasha" / "themes"
        if theme_file is None:
            default_theme_path = theme_dir / "default.toml"
        else:
            default_theme_path = theme_dir / theme_file

        with default_theme_path.open() as loaded_theme:
            current_theme = loaded_theme.read()
            
        return toml.loads(current_theme)
