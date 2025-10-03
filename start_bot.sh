#!/bin/bash

# Load environment variables from .env file
export $(grep -v '^#' .env | xargs)

# Activate virtual environment and start bot
source venv/bin/activate
python -m telegram_bot.bot
