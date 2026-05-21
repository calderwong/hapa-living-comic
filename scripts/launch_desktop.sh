#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/Users/calderwong/Desktop/hapa-living-comic"
LTX_DIR="/Users/calderwong/Documents/Codex/2026-05-19/thoroughly-review-the-hapa-worldbuilding-wiki/hapa-ltx-node"
LOG_DIR="$APP_DIR/logs"
mkdir -p "$LOG_DIR"

cd "$APP_DIR"
export PYTHONPATH="$APP_DIR/backend"
export LIVING_COMIC_DATA="${LIVING_COMIC_DATA:-$APP_DIR/runtime}"
export LIVING_COMIC_PROVIDER="${LIVING_COMIC_PROVIDER:-hapa-ltx}"
export LIVING_COMIC_TTS_PROVIDER="${LIVING_COMIC_TTS_PROVIDER:-mac-say}"
export HAPA_LTX_URL="${HAPA_LTX_URL:-http://127.0.0.1:8753}"
export HAPA_LTX_NODE_ROOT="${HAPA_LTX_NODE_ROOT:-$LTX_DIR}"
export LIVING_COMIC_PORT="${LIVING_COMIC_PORT:-8776}"

if [ -f "$HAPA_LTX_NODE_ROOT/.node_token" ]; then
  export HAPA_LTX_TOKEN_FILE="${HAPA_LTX_TOKEN_FILE:-$HAPA_LTX_NODE_ROOT/.node_token}"
fi

ensure_ltx_node() {
  if curl -fsS --max-time 2 "$HAPA_LTX_URL/health" >/dev/null 2>&1; then
    echo "Hapa LTX Node already running at $HAPA_LTX_URL"
    return 0
  fi
  if [ ! -d "$HAPA_LTX_NODE_ROOT" ]; then
    echo "Hapa LTX Node folder not found: $HAPA_LTX_NODE_ROOT" >&2
    return 1
  fi
  echo "Starting Hapa LTX Node..."
  (cd "$HAPA_LTX_NODE_ROOT" && ./scripts/launch-local-mlx.sh > "$LOG_DIR/hapa-ltx-node.log" 2>&1) &
  for _ in {1..90}; do
    if curl -fsS --max-time 2 "$HAPA_LTX_URL/health" >/dev/null 2>&1; then
      echo "Hapa LTX Node is ready."
      return 0
    fi
    sleep 2
  done
  echo "Hapa LTX Node did not become ready. See $LOG_DIR/hapa-ltx-node.log" >&2
  return 1
}

ensure_backend() {
  local backend_url="http://127.0.0.1:${LIVING_COMIC_PORT}"
  if curl -fsS --max-time 2 "$backend_url/health" | grep -q 'living-comic-book'; then
    echo "Living Comic backend already running at $backend_url"
    return 0
  fi
  echo "Starting Living Comic backend at $backend_url..."
  if [ ! -d .venv ]; then
    python3 -m venv .venv
    . .venv/bin/activate
    python -m pip install -U pip
    python -m pip install -r requirements.txt
  else
    . .venv/bin/activate
  fi
  python -m uvicorn living_comic.api.server:app --host 127.0.0.1 --port "$LIVING_COMIC_PORT" > "$LOG_DIR/backend.log" 2>&1 &
  for _ in {1..45}; do
    if curl -fsS --max-time 2 "$backend_url/health" | grep -q 'living-comic-book'; then
      echo "Living Comic backend is ready at $backend_url."
      return 0
    fi
    sleep 1
  done
  echo "Backend did not become ready. See $LOG_DIR/backend.log" >&2
  return 1
}

ensure_ltx_node
ensure_backend

echo "Launching SwiftUI Living Comic Book..."
cd "$APP_DIR/swiftui/LivingComicBook"
swift run
