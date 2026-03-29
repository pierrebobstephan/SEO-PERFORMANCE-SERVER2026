from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from electri_city_ops.config import load_config


class ConfigTests(unittest.TestCase):
    def test_invalid_mode_falls_back_to_observe_only(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "config"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "settings.toml"
            config_path.write_text("[system]\nmode = 'unknown'\n", encoding="utf-8")

            config, notes = load_config(config_path, root)

            self.assertEqual(config.mode, "observe_only")
            self.assertTrue(any("Falling back to observe_only" in note for note in notes))

    def test_storage_paths_cannot_escape_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            config_dir = root / "config"
            config_dir.mkdir(parents=True)
            config_path = config_dir / "settings.toml"
            config_path.write_text("[storage]\ndatabase = '../outside.sqlite3'\n", encoding="utf-8")

            with self.assertRaises(ValueError):
                load_config(config_path, root)


if __name__ == "__main__":
    unittest.main()

