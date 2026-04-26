#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys


WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = WORKSPACE_ROOT / "packages" / "wp-plugin" / "hetzner-seo-ops"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run php -l across the Site Optimizer Bridge plugin.")
    parser.add_argument("--plugin-root", default=str(PLUGIN_ROOT))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plugin_root = Path(args.plugin_root).resolve()
    php = shutil.which("php")
    if php is None:
        print(
            json.dumps(
                {
                    "status": "tooling_missing",
                    "ok": False,
                    "issue": "PHP CLI is not available; install it in CI or the validation host before claiming PHP syntax validation.",
                },
                indent=2,
            )
        )
        return 2

    files = sorted(plugin_root.rglob("*.php"))
    issues: list[dict[str, str]] = []
    for path in files:
        result = subprocess.run([php, "-l", str(path)], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            issues.append(
                {
                    "path": str(path.relative_to(WORKSPACE_ROOT)),
                    "stdout": result.stdout.strip(),
                    "stderr": result.stderr.strip(),
                }
            )

    print(
        json.dumps(
            {
                "status": "passed" if not issues else "failed",
                "ok": not issues,
                "checked_files": len(files),
                "issues": issues,
            },
            indent=2,
        )
    )
    return 0 if not issues else 1


if __name__ == "__main__":
    raise SystemExit(main())
