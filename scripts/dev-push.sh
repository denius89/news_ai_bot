#!/bin/bash

# Development push script for PulseAI
# Runs all checks and pushes with proper commit message

set -e

echo "🚀 PulseAI Development Push Script"
echo "=================================="

# Check if we're in git repo
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository"
    exit 1
fi

# Check if there are changes to commit
if git diff --quiet && git diff --cached --quiet; then
    echo "ℹ️  No changes to commit"
    exit 0
fi

# Run pre-push checks
echo "🔍 Running pre-push checks..."
make pre-push

if [ $? -ne 0 ]; then
    echo "❌ Pre-push checks failed"
    exit 1
fi

# Stage all changes
echo "📝 Staging changes..."
git add .

# Generate commit message
COMMIT_MSG=""
if [ $# -gt 0 ]; then
    # Use provided message
    COMMIT_MSG="$1"
else
    # Generate automatic message
    CHANGED_FILES=$(git diff --cached --name-only | head -5 | tr '\n' ', ' | sed 's/,$//')
    COMMIT_MSG="feat: update $CHANGED_FILES

- Code formatted with Black
- Critical flake8 issues resolved
- Ready for review"
fi

# Commit changes
echo "💾 Committing changes..."
git commit -m "$COMMIT_MSG"

# Push to origin
echo "🚀 Pushing to origin..."
git push origin main

echo "✅ Push completed successfully!"
echo "🎉 Your changes are now live on GitHub!"
