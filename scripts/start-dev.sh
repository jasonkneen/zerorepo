#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_SCRIPT="$ROOT_DIR/scripts/start-backend.sh"
FRONTEND_SCRIPT="$ROOT_DIR/scripts/start-frontend.sh"

if [[ ! -x "$BACKEND_SCRIPT" ]]; then
  echo "[start-dev] Backend script missing at $BACKEND_SCRIPT" >&2
  exit 1
fi

if [[ ! -x "$FRONTEND_SCRIPT" ]]; then
  echo "[start-dev] Frontend script missing at $FRONTEND_SCRIPT" >&2
  exit 1
fi

"$BACKEND_SCRIPT" &
BACK_PID=$!

"$FRONTEND_SCRIPT" &
FRONT_PID=$!

cleanup() {
  trap - INT TERM EXIT
  echo "\n[start-dev] Shutting down..."
  kill "$BACK_PID" "$FRONT_PID" >/dev/null 2>&1 || true
}

trap cleanup INT TERM EXIT

# Wait for either process to exit (portable)
EXIT_CODE=0
while true; do
  if ! kill -0 "$BACK_PID" >/dev/null 2>&1; then
    wait "$BACK_PID" >/dev/null 2>&1 || EXIT_CODE=$?
    break
  fi
  if ! kill -0 "$FRONT_PID" >/dev/null 2>&1; then
    wait "$FRONT_PID" >/dev/null 2>&1 || EXIT_CODE=$?
    break
  fi
  sleep 1
done

cleanup
wait "$BACK_PID" >/dev/null 2>&1 || true
wait "$FRONT_PID" >/dev/null 2>&1 || true
exit "$EXIT_CODE"
