#!/bin/bash
set -euo pipefail

# Sandbox pytest runner (non-invasive)
# - Uses existing project venv if available
# - Falls back to system python; if pytest missing, exits gracefully

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo "[sandbox] 🧪 Running tests in sandbox..."

run_pytest() {
  if command -v pytest >/dev/null 2>&1; then
    pytest -q --maxfail=1 --disable-warnings || exit 1
  else
    echo "[sandbox] ⚠️ pytest not found; skipping test run"
  fi
}

# Try project venv if exists
if [ -d "venv" ]; then
  # shellcheck disable=SC1091
  source venv/bin/activate || true
  run_pytest
  exit 0
fi

# Try system python
run_pytest

exit 0
