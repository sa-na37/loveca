#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_BIN="${PYTHON:-python3}"
exec "$PYTHON_BIN" ./run_loveca_app.py --window-mode app
