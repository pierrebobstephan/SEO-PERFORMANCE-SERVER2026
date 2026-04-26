#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from electri_city_ops.backup_foundation import post_restore_validation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run local post-restore validation preview.")
    parser.add_argument("--run-tests", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = post_restore_validation(WORKSPACE_ROOT, run_tests=args.run_tests)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
