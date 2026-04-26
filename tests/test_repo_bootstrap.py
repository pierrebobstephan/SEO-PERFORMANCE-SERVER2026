import os
from pathlib import Path
import subprocess
import sys
import unittest


class RepoBootstrapTests(unittest.TestCase):
    def test_plain_python_from_repo_root_imports_src_package(self) -> None:
        root = Path(__file__).resolve().parents[1]
        env = dict(os.environ)
        env.pop("PYTHONPATH", None)

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from electri_city_ops import config; print(config.__file__)",
            ],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(str(root / "src" / "electri_city_ops" / "config.py"), result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
