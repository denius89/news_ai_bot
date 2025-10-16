#!/bin/bash
# Автоматический парсинг новостей с переобучением моделей
# Запускается по расписанию (рекомендуется: каждые 6-12 часов)

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Автоматический парсинг + переобучение${NC}"
echo "=================================================="
echo "Время запуска: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Переходим в корневую директорию проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "📂 Рабочая директория: $PROJECT_ROOT"
echo ""

# Активируем виртуальное окружение (если есть)
if [ -d "venv" ]; then
    echo "🐍 Активация виртуального окружения..."
    source venv/bin/activate
fi

# Проверяем наличие .env файла
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Файл .env не найден!${NC}"
    exit 1
fi

# Загружаем переменные окружения
export $(grep -v '^#' .env | xargs)

# Создаем директорию для логов если её нет
mkdir -p logs

# Имя лог-файла с датой
LOG_FILE="logs/auto_fetch_train_$(date '+%Y%m%d_%H%M%S').log"

echo "📝 Лог-файл: $LOG_FILE"
echo ""

# Запускаем парсинг с переобучением
echo -e "${YELLOW}⏳ Запуск парсинга и переобучения...${NC}"
echo ""

python3 tools/news/fetch_and_train.py \
    --max-concurrent 10 \
    2>&1 | tee "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "=================================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Парсинг и переобучение завершены успешно!${NC}"
    
    # Опционально: отправить уведомление об успехе
    # curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    #     -d chat_id="$ADMIN_CHAT_ID" \
    #     -d text="✅ Автоматический парсинг успешно выполнен"
    
    exit 0
else
    echo -e "${RED}❌ Ошибка при выполнении парсинга (код: $EXIT_CODE)${NC}"
    
    # Опционально: отправить уведомление об ошибке
    # curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    #     -d chat_id="$ADMIN_CHAT_ID" \
    #     -d text="❌ Ошибка автоматического парсинга. Проверьте логи."
    
    exit $EXIT_CODE
fi


