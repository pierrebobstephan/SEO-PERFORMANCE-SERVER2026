#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from electri_city_ops.public_portal import run_public_portal


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the public portal local upstream.")
    parser.add_argument("--config", default="config/settings.toml")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    return run_public_portal(
        args.config,
        workspace_root=WORKSPACE_ROOT,
        host=args.host,
        port=args.port,
    )


if __name__ == "__main__":
    raise SystemExit(main())
