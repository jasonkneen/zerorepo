#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/frontend"

if [[ ! -d node_modules ]]; then
  echo "[start-frontend] Installing frontend dependencies..."
  if ! yarn install; then
    echo "[start-frontend] Initial yarn install failed. Clearing cache and retrying..." >&2
    yarn cache clean --all >/dev/null 2>&1 || true
    yarn install
  fi
fi

export PORT="${PORT:-4000}"
export REACT_APP_BACKEND_URL="${REACT_APP_BACKEND_URL:-http://localhost:8001}"

exec yarn start
