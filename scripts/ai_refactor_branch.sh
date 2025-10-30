#!/bin/bash
set -euo pipefail

BRANCH="ai-refactor/$(date +%Y%m%d_%H%M%S)-chiron"

echo "[branch] Creating $BRANCH"

git checkout -b "$BRANCH"

echo "[branch] Done. Suggested flow:"
echo "  - One logical change per commit"
echo "  - Run: make repo-map && make lint && make ai-qa"
echo "  - Guard: python3 tools/refactor_guard.py --check public_api"
