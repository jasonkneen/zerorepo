#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PATH="$ROOT_DIR/.venv/bin/activate"

if [[ ! -f "$VENV_PATH" ]]; then
  echo "[run-tests] Expected virtualenv at $ROOT_DIR/.venv. Run 'uv venv --python 3.11 .venv' first." >&2
  exit 1
fi

source "$VENV_PATH"
cd "$ROOT_DIR"

exec pytest "$@"
