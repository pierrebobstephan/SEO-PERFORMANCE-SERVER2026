#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = WORKSPACE_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from electri_city_ops.backup_foundation import collect_backup_inventory


def main() -> int:
    payload = collect_backup_inventory(WORKSPACE_ROOT)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
