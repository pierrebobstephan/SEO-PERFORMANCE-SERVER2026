#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST="${HOST:-127.0.0.1}"
PORT="${PORT:-8781}"

echo "Electri City Public Portal local upstream"
echo "Upstream URL: http://${HOST}:${PORT}/"
echo "Public subdomain target: https://site-optimizer.electri-c-ity-studios-24-7.com"
echo "Note: public reachability requires reverse proxy and TLS; protected routes remain non-public."

cd "${ROOT_DIR}"
exec python3 tools/run_public_portal.py --host "${HOST}" --port "${PORT}" "$@"
