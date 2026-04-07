#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TRIBE_DIR="$ROOT_DIR/third_party/tribev2"
TRIBE_REPO_URL="${TRIBE_REPO_URL:-https://github.com/facebookresearch/tribev2.git}"
TRIBE_REF="${TRIBE_REF:-}"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

require_command git
require_command uv
require_command python3

mkdir -p "$ROOT_DIR/third_party"
mkdir -p "$ROOT_DIR/artifacts/setup"

echo "[bootstrap] syncing project environment"
(
  cd "$ROOT_DIR"
  uv sync --all-groups
)

if [ ! -d "$TRIBE_DIR/.git" ]; then
  echo "[bootstrap] cloning TRIBE v2 into $TRIBE_DIR"
  git clone "$TRIBE_REPO_URL" "$TRIBE_DIR"
else
  echo "[bootstrap] TRIBE v2 already present, fetching latest refs"
  git -C "$TRIBE_DIR" fetch --all --tags
fi

if [ -n "$TRIBE_REF" ]; then
  echo "[bootstrap] checking out TRIBE ref $TRIBE_REF"
  git -C "$TRIBE_DIR" checkout "$TRIBE_REF"
fi

echo "[bootstrap] installing TRIBE v2 in editable mode"
if ! uv pip install --python "$ROOT_DIR/.venv/bin/python" -e "$TRIBE_DIR"; then
  echo "[bootstrap] TRIBE editable install failed; continuing in degraded mode" >&2
fi

echo "[bootstrap] running TRIBE smoke test"
PYTHONPATH="$ROOT_DIR/apps/api/src:$ROOT_DIR/packages/bootstrap/src:$ROOT_DIR/packages/core/src:$ROOT_DIR/packages/llm/src${PYTHONPATH:+:$PYTHONPATH}" \
  "$ROOT_DIR/.venv/bin/python" "$ROOT_DIR/scripts/smoke_test_tribe.py" --repo-root "$ROOT_DIR"

echo "[bootstrap] completed"
