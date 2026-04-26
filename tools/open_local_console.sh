#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8765}"

echo "Electri City Ops Local Console"
echo "Local only / no external effect"
echo "URL: http://${HOST}:${PORT}/"
echo "Health: http://${HOST}:${PORT}/healthz"

cd "${ROOT_DIR}"
exec python3 tools/run_local_console.py --host "${HOST}" --port "${PORT}" "$@"
