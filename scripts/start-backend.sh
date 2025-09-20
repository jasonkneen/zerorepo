#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$ROOT_DIR/.venv/bin/activate"

if [[ ! -f "$VENV_PATH" ]]; then
  echo "[start-backend] Expected virtualenv at $ROOT_DIR/.venv. Run 'uv venv --python 3.11 .venv' first." >&2
  exit 1
fi

source "$VENV_PATH"

if [[ -f "$ROOT_DIR/.env" ]]; then
  set -o allexport
  # shellcheck disable=SC1090
  source "$ROOT_DIR/.env"
  set +o allexport
fi

if [[ -z "${PYTHONPATH:-}" ]]; then
  export PYTHONPATH="$ROOT_DIR/backend"
else
  export PYTHONPATH="$ROOT_DIR/backend:$PYTHONPATH"
fi

if [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "[start-backend] Warning: OPENAI_API_KEY is not set. LLM endpoints will fail." >&2
fi

cd "$ROOT_DIR/backend"

PORT="${PORT:-8001}"
HOST="${HOST:-0.0.0.0}"

exec uvicorn server:app --reload --host "$HOST" --port "$PORT"
