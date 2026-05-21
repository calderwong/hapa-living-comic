#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/backend"
python3 -m living_comic.cli "${1:-Calder, Thor, and the Huemon Trainer build a living comic}" --data runtime --panels 6
