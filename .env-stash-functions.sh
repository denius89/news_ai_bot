#!/usr/bin/env zsh
# Git Stash функции для безопасной работы с .env
# Добавьте в ~/.zshrc: source /home/user/news_ai_bot/.env-stash-functions.sh

# Цвета
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Функция: Сохранить .env
function env-save() {
    local message="${1:-manual backup}"
    local timestamp=$(date '+%Y-%m-%d %H:%M')
    
    echo -e "${BLUE}💾 Сохранение .env...${NC}"
    
    # Проверяем наличие .env
    if [ ! -f .env ]; then
        echo -e "${RED}❌ Файл .env не найден${NC}"
        return 1
    fi
    
    # Добавляем в индекс, создаем stash, убираем из индекса
    git add -f .env 2>/dev/null
    git stash push .env -m "$timestamp - $message"
    git reset HEAD .env 2>/dev/null
    
    echo -e "${GREEN}✅ Backup создан: $timestamp - $message${NC}"
}

# Функция: Восстановить последний .env
function env-restore() {
    echo -e "${BLUE}🔄 Восстановление последнего .env...${NC}"
    
    # Проверяем наличие stash
    if ! git stash list | grep -q "\.env"; then
        echo -e "${RED}❌ Нет сохраненных backup'ов .env${NC}"
        return 1
    fi
    
    # Показываем что будем восстанавливать
    local last_stash=$(git stash list | head -1)
    echo -e "${YELLOW}Восстанавливаем:${NC} $last_stash"
    
    # Восстанавливаем
    git stash pop
    
    echo -e "${GREEN}✅ .env восстановлен${NC}"
}

# Функция: Показать список всех backup'ов
function env-list() {
    echo -e "${BLUE}📋 Список backup'ов .env:${NC}"
    echo ""
    git stash list
    echo ""
    echo -e "${YELLOW}💡 Для восстановления конкретного:${NC} git stash apply stash@{N}"
}

# Функция: Показать содержимое последнего backup'а
function env-show() {
    local stash_id="${1:-stash@{0}}"
    echo -e "${BLUE}👀 Содержимое $stash_id:${NC}"
    echo ""
    git stash show -p "$stash_id"
}

# Функция: Сравнить текущий .env с последним backup'ом
function env-diff() {
    local stash_id="${1:-stash@{0}}"
    
    if [ ! -f .env ]; then
        echo -e "${RED}❌ Файл .env не найден${NC}"
        return 1
    fi
    
    echo -e "${BLUE}🔍 Сравнение текущего .env с $stash_id:${NC}"
    echo ""
    
    # Получаем .env из stash и сравниваем
    git show "$stash_id:.env" > /tmp/.env.stash 2>/dev/null || {
        echo -e "${RED}❌ Не удалось получить .env из stash${NC}"
        return 1
    }
    
    diff -u /tmp/.env.stash .env || {
        echo ""
        echo -e "${GREEN}Легенда: ${RED}- строки из backup${NC}, ${GREEN}+ текущие строки${NC}"
    }
    
    rm /tmp/.env.stash
}

# Функция: Удалить старые backup'ы (оставить последние N)
function env-cleanup() {
    local keep="${1:-5}"
    
    echo -e "${BLUE}🧹 Очистка старых backup'ов (оставляем последние $keep)...${NC}"
    
    local total=$(git stash list | wc -l)
    
    if [ "$total" -le "$keep" ]; then
        echo -e "${GREEN}✅ Всего $total backup'ов, очистка не требуется${NC}"
        return 0
    fi
    
    local to_delete=$((total - keep))
    echo -e "${YELLOW}Будет удалено $to_delete старых backup'ов${NC}"
    
    # Удаляем с конца
    for i in $(seq $keep $((total - 1))); do
        git stash drop "stash@{$keep}" 2>/dev/null
    done
    
    echo -e "${GREEN}✅ Очистка завершена. Осталось: $keep backup'ов${NC}"
}

# Функция: Быстрое редактирование .env с авто-backup
function env-edit() {
    local editor="${EDITOR:-nano}"
    
    echo -e "${BLUE}📝 Редактирование .env с автоматическим backup...${NC}"
    
    # Создаем backup
    env-save "auto backup before edit"
    
    # Открываем редактор
    $editor .env
    
    echo ""
    echo -e "${GREEN}✅ Редактирование завершено${NC}"
    echo -e "${YELLOW}💡 Для отката: env-restore${NC}"
}

# Функция: Показать помощь
function env-help() {
    echo -e "${BLUE}🔧 Git Stash команды для .env:${NC}"
    echo ""
    echo -e "${GREEN}env-save [описание]${NC}      - Сохранить текущий .env"
    echo -e "${GREEN}env-restore${NC}               - Восстановить последний backup"
    echo -e "${GREEN}env-list${NC}                  - Показать все backup'ы"
    echo -e "${GREEN}env-show [stash@{N}]${NC}     - Показать содержимое backup'а"
    echo -e "${GREEN}env-diff [stash@{N}]${NC}     - Сравнить текущий с backup'ом"
    echo -e "${GREEN}env-edit${NC}                  - Редактировать с авто-backup"
    echo -e "${GREEN}env-cleanup [N]${NC}           - Оставить последние N backup'ов (по умолчанию 5)"
    echo -e "${GREEN}env-help${NC}                  - Показать эту справку"
    echo ""
    echo -e "${YELLOW}Примеры:${NC}"
    echo "  env-save \"before testing new API key\""
    echo "  env-diff stash@{1}"
    echo "  env-cleanup 10"
    echo ""
    echo -e "${BLUE}📖 Полное руководство:${NC} .env-stash-guide.md"
}

echo -e "${GREEN}✅ Git Stash функции для .env загружены${NC}"
echo -e "${YELLOW}💡 Используйте 'env-help' для справки${NC}"

