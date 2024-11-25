from typing import Dict


class ThemeLoader:

    def __init__(self, theme_file: str | None = None) -> None:
        """Loads the requested theme file.

        Args:
            theme_file (str): Theme file to load."""
        from pathlib import Path

        theme_dir = Path.home() / ".config" / "tasha" / "themes"
        self.current_theme_path = theme_dir / "default.toml"

        if theme_file is not None:
            check_theme_path = theme_dir / f"{theme_file}.toml"
            if check_theme_path.exists():
                self.current_theme_path = check_theme_path

    def loadTheme(self) -> Dict[str, str]:
        """Loads the set theme file.

        Returns:
            Dict[str, str]: Toml theme file loaded in dict format."""
        import toml

        with self.current_theme_path.open() as loaded_theme:
            return toml.loads(loaded_theme.read())
