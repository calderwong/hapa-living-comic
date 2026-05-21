#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/backend"
export LIVING_COMIC_DATA="${LIVING_COMIC_DATA:-$PWD/runtime}"
python3 -m uvicorn living_comic.api.server:app --reload --host 127.0.0.1 --port 8766
