#!/bin/bash

# Pre-push script for PulseAI
# Runs linters in correct order before pushing

set -e  # Exit on any error

echo "🔍 Running pre-push checks..."

# 1. Black formatting
echo "📝 Running Black formatter..."
black .
echo "✅ Black formatting completed"

# 2. Flake8 linting (excluding tools and non-critical files)
echo "🔍 Running Flake8 linter..."
flake8 . \
    --exclude=venv,__pycache__,.git,tools,parsers/advanced_parser.py \
    --max-line-length=120 \
    --ignore=E402,E501,W293,F401,F841,F541,E722 \
    --select=F821,F811

echo "✅ Flake8 linting completed"

# 3. Run tests (optional - can be skipped if takes too long)
echo "🧪 Running critical tests..."
python -m pytest tests/test_cache.py tests/test_http_client.py -v --tb=short

echo "✅ Critical tests passed"

echo "🎉 All pre-push checks completed successfully!"
