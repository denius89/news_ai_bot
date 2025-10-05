#!/bin/bash

# Setup convenient aliases for PulseAI development

echo "🔧 Setting up PulseAI development aliases..."

# Detect shell
SHELL_CONFIG=""
if [ -n "$ZSH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
else
    echo "⚠️  Unknown shell. Please add aliases manually."
    exit 1
fi

# Aliases to add
ALIASES="
# PulseAI Development Aliases
alias push='./scripts/dev-push.sh'
alias check='make pre-push'
alias fmt='make format'
alias lint='make lint'
alias bot='make run-bot'
alias web='make run-web'
alias dev='make dev'
alias test='make test'
alias db-check='make db-check'
alias ports='make check-ports'
alias free='make free-ports'
"

# Add aliases if they don't exist
if ! grep -q "PulseAI Development Aliases" "$SHELL_CONFIG" 2>/dev/null; then
    echo "$ALIASES" >> "$SHELL_CONFIG"
    echo "✅ Aliases added to $SHELL_CONFIG"
    echo "🔄 Please run: source $SHELL_CONFIG"
    echo ""
    echo "📋 Available aliases:"
    echo "  push     - Smart push with checks (./scripts/dev-push.sh)"
    echo "  check    - Run pre-push checks (make pre-push)"
    echo "  fmt      - Format code (make format)"
    echo "  lint     - Lint code (make lint)"
    echo "  bot      - Run Telegram bot (make run-bot)"
    echo "  web      - Run WebApp (make run-web)"
    echo "  dev      - Run both bot and web (make dev)"
    echo "  test     - Run tests (make test)"
    echo "  db-check - Check database (make db-check)"
    echo "  ports    - Check ports (make check-ports)"
    echo "  free     - Free ports (make free-ports)"
else
    echo "✅ Aliases already exist in $SHELL_CONFIG"
fi
