#!/bin/bash
# Скрипт для безопасного backup .env файлов PulseAI
# Использование: ./tools/backup_env.sh

set -e

BACKUP_DIR="$HOME/.pulseai-secrets"
PROJECT_NAME="news_ai_bot"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔒 PulseAI Backup утилита${NC}"
echo "================================"

# Создаем защищенную папку для backup'ов
mkdir -p "$BACKUP_DIR/$PROJECT_NAME"
chmod 700 "$BACKUP_DIR"

# Проверяем наличие .env
if [ ! -f .env ]; then
    echo -e "${RED}❌ Файл .env не найден в текущей директории${NC}"
    exit 1
fi

# Копируем .env с timestamp
cp .env "$BACKUP_DIR/$PROJECT_NAME/.env.$TIMESTAMP"
chmod 600 "$BACKUP_DIR/$PROJECT_NAME/.env.$TIMESTAMP"

echo -e "${GREEN}✅ Backup создан:${NC}"
echo "   $BACKUP_DIR/$PROJECT_NAME/.env.$TIMESTAMP"
echo ""

# Показываем последние backup'ы
echo -e "${BLUE}📋 Последние backup'ы:${NC}"
ls -lht "$BACKUP_DIR/$PROJECT_NAME/" | head -6

# Автоматическая очистка старых backup'ов (хранить последние 10)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR/$PROJECT_NAME/" | wc -l)
if [ "$BACKUP_COUNT" -gt 10 ]; then
    echo ""
    echo -e "${BLUE}🧹 Удаление старых backup'ов (хранятся последние 10)...${NC}"
    ls -t "$BACKUP_DIR/$PROJECT_NAME/" | tail -n +11 | xargs -I {} rm "$BACKUP_DIR/$PROJECT_NAME/{}"
    echo -e "${GREEN}✅ Очистка завершена${NC}"
fi

echo ""
echo -e "${GREEN}💡 Для восстановления:${NC}"
echo "   cp $BACKUP_DIR/$PROJECT_NAME/.env.$TIMESTAMP .env"


