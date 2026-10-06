# 🔄 Пошаговая инструкция: Замена Cloudflare URL

**Дата создания:** 2025-10-16  
**Версия:** 1.0  
**Автор:** PulseAI Assistant

---

## 📋 Краткий чеклист

- [ ] 1. Перезапустить Cloudflare Tunnel
- [ ] 2. Получить новый URL из логов
- [ ] 3. Обновить конфигурационные файлы (5 файлов)
- [ ] 4. Обновить .env файлы (3 файла) ⚠️ КРИТИЧНО
- [ ] 5. Обновить документацию (10+ файлов)
- [ ] 6. Перезапустить Flask WebApp ⚠️ КРИТИЧНО
- [ ] 7. Перезапустить Telegram Bot ⚠️ КРИТИЧНО
- [ ] 8. Проверить работоспособность

---

## 🚀 ШАГ 1: Перезапуск Cloudflare Tunnel

### Команды:

```bash
# Остановить старый туннель
pkill cloudflared

# Запустить новый туннель
cd /home/user/news_ai_bot
cloudflared tunnel --url http://localhost:8001 > logs/cloudflare.log 2>&1 &

# Подождать 5 секунд для установки соединения
sleep 5

# Получить новый URL из логов
tail -30 logs/cloudflare.log | grep -E "(trycloudflare.com|Your quick Tunnel)"
```

### Результат:
Запишите новый URL, например: `https://example.invalid`

---

## 📝 ШАГ 2: Обновление конфигурационных файлов

### 2.1. Python конфигурация

**Файл:** `config/core/cloudflare.py`  
**Строка:** ~18

```python
# Найти и заменить:
CLOUDFLARE_TUNNEL_URL = os.getenv("CLOUDFLARE_TUNNEL_URL", "https://example.invalid")

# На:
CLOUDFLARE_TUNNEL_URL = os.getenv("CLOUDFLARE_TUNNEL_URL", "https://example.invalid")
```

**Команда для замены:**
```bash
# Заменить OLD-URL на ваш старый URL, NEW-URL на новый
OLD_URL="old-url-example"
NEW_URL="new-url-example"

# Обновить config/core/cloudflare.py
sed -i '' "s|$OLD_URL|$NEW_URL|g" config/core/cloudflare.py
```

---

### 2.2. ⚠️ КРИТИЧНО: Обновление .env файлов

**⚠️ ВАЖНО:** Без этого шага бот и Flask загрузят старый URL из переменных окружения!

**Файлы для обновления:**

1. `.env` (корневой)
2. `config_files/environment/.env`
3. `config_files/.env` (если существует как файл)

**Команды:**
```bash
OLD_URL="old-url-example"
NEW_URL="new-url-example"

# 1. Обновить корневой .env
sed -i '' "s|https://$OLD_URL.trycloudflare.com|https://$NEW_URL.trycloudflare.com|g" .env

# 2. Обновить config_files/environment/.env
sed -i '' "s|https://$OLD_URL.trycloudflare.com|https://$NEW_URL.trycloudflare.com|g" config_files/environment/.env

# 3. Проверить результат
echo "=== Проверка .env файлов ==="
echo "1. Корневой .env:"
grep CLOUDFLARE_TUNNEL_URL .env
echo ""
echo "2. config_files/environment/.env:"
grep CLOUDFLARE_TUNNEL_URL config_files/environment/.env
```

**Ожидаемый результат:**
```
CLOUDFLARE_TUNNEL_URL=https://example.invalid
```

---

### 2.3. Cloudflare Tunnel конфигурация (опционально)

**Файл:** `cloudflare-tunnel.yaml`

**Примечание:** Этот файл используется только для named tunnels. Для quick tunnels (temporary) можно пропустить или обновить для документации.

```bash
OLD_URL="old-url-example"
NEW_URL="new-url-example"

sed -i '' "s|$OLD_URL|$NEW_URL|g" cloudflare-tunnel.yaml
```

---

## 📚 ШАГ 3: Обновление документации

### Автоматическое обновление всех документов

```bash
OLD_URL="old-url-example"
NEW_URL="new-url-example"

# Список файлов для обновления
FILES=(
    "README.md"
    "DEPLOYMENT_STATUS.md"
    "CLOUDFLARE_URL_AUDIT_REPORT.md"
    "CHANGELOG.md"
    "FINAL_SESSION_SUMMARY.md"
    "CURRENT_SERVICES_STATUS.md"
    "WEBAPP_FIX_CYRILLIC_HEADERS.md"
    "docs/reports/FINAL_TODO_REPORT.md"
)

# Обновить каждый файл
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        sed -i '' "s|$OLD_URL|$NEW_URL|g" "$file"
        echo "✅ Обновлен: $file"
    else
        echo "⚠️ Не найден: $file"
    fi
done
```

### Проверка обновлений

```bash
# Проверить, остались ли упоминания старого URL
grep -r "$OLD_URL" . --include="*.md" --include="*.py" --exclude-dir=venv --exclude-dir=node_modules --exclude-dir=archive
```

Если команда ничего не выводит → все обновлено успешно ✅

---

## 🔄 ШАГ 4: Перезапуск сервисов

### ⚠️ КРИТИЧНО: Порядок важен!

### 4.1. Перезапуск Flask WebApp

**Почему критично:** Flask кеширует `CLOUDFLARE_TUNNEL_URL` при старте. Без перезапуска продолжит использовать старый URL.

```bash
# Остановить Flask
pkill -f "src/webapp.py"

# Подождать завершения
sleep 2

# Запустить Flask с новыми настройками
cd /home/user/news_ai_bot
python3 src/webapp.py > logs/webapp.log 2>&1 &

# Подождать запуска
sleep 5

# Проверить, что Flask запущен
ps aux | grep "src/webapp.py" | grep -v grep
lsof -i :8001

# Проверить логи
tail -20 logs/webapp.log | grep -E "(запущен|Running|started)"
```

**Ожидаемый результат:**
```
✅ Процесс Flask запущен (должно быть 2 процесса - parent и child)
✅ Порт 8001 слушает
✅ В логах: "🚀 Webapp запущен"
```

---

### 4.2. Перезапуск Telegram Bot

**Почему критично:** Бот загружает `WEBAPP_URL` из `config.core.settings` при старте. Необходимо перезапустить для загрузки нового URL.

```bash
# Остановить бота
pkill -f "telegram_bot/bot.py"

# Подождать завершения
sleep 2

# Запустить бота с новыми настройками
cd /home/user/news_ai_bot
PYTHONPATH=/home/user/news_ai_bot:$PYTHONPATH python3 telegram_bot/bot.py > logs/bot.log 2>&1 &

# Подождать запуска
sleep 5

# Проверить, что бот запущен
ps aux | grep "telegram_bot/bot.py" | grep -v grep

# Проверить логи
tail -20 logs/bot.log | grep -E "(started|Started|запущен)"
```

**Ожидаемый результат:**
```
✅ Процесс бота запущен
✅ В логах: "🚀 Telegram bot started"
✅ В логах: "Run polling for bot @PulseAIDigest_bot"
```

---

### 4.3. Проверка загруженного URL в боте

**⚠️ ОБЯЗАТЕЛЬНАЯ ПРОВЕРКА:**

```bash
# Проверить, какой URL загружен в конфигурации
python3 -c "from config.core.settings import WEBAPP_URL; print(f'✅ WEBAPP_URL: {WEBAPP_URL}')"
```

**Ожидаемый результат:**
```
✅ WEBAPP_URL: https://example.invalid
```

**Если видите старый URL:**
1. Проверьте .env файлы (шаг 2.2)
2. Перезапустите бота снова (шаг 4.2)

---

## ✅ ШАГ 5: Финальная проверка работоспособности

### 5.1. Проверка всех сервисов

```bash
echo "=== ПРОВЕРКА СЕРВИСОВ ==="
echo ""
echo "1. Cloudflare Tunnel:"
ps aux | grep cloudflared | grep -v grep | awk '{print "   PID:", $2, "- ✅ Запущен"}'
echo ""

echo "2. Flask WebApp:"
ps aux | grep "src/webapp.py" | grep -v grep | head -1 | awk '{print "   PID:", $2, "- ✅ Запущен"}'
lsof -i :8001 | grep LISTEN && echo "   Порт 8001 - ✅ Слушает"
echo ""

echo "3. Telegram Bot:"
ps aux | grep "telegram_bot/bot.py" | grep -v grep | head -1 | awk '{print "   PID:", $2, "- ✅ Запущен"}'
echo ""

echo "4. Загруженный URL:"
python3 -c "from config.core.settings import WEBAPP_URL; print('   ' + WEBAPP_URL)"
```

---

### 5.2. Проверка HTTP endpoints

```bash
NEW_URL="new-url-example"  # Замените на ваш URL

echo "=== ПРОВЕРКА ENDPOINTS ==="
echo ""

# Локальный доступ
echo "1. Локальный API Health:"
curl -s "http://localhost:8001/api/health" | python3 -m json.tool | head -10
echo ""

# Через Cloudflare
echo "2. Cloudflare API Health:"
curl -s "https://$NEW_URL.trycloudflare.com/api/health" | python3 -m json.tool | head -10
echo ""

# Статус код WebApp
echo "3. WebApp доступность:"
curl -s -I "https://$NEW_URL.trycloudflare.com/webapp" | head -1
echo ""

# Статус код Admin
echo "4. Admin Panel доступность:"
curl -s -I "https://$NEW_URL.trycloudflare.com/admin" | head -1
```

**Ожидаемые результаты:**
- API Health: `{"status": "success", "message": "PulseAI API is healthy"}`
- WebApp: `HTTP/2 200` или `HTTP/1.1 200`
- Admin: `HTTP/2 200` или `HTTP/1.1 200`

---

### 5.3. Проверка Telegram Bot Dashboard

**Ручная проверка:**

1. Откройте Telegram бота: @PulseAIDigest_bot
2. Отправьте команду: `/dashboard`
3. Нажмите кнопку: **"📱 Открыть Dashboard"**
4. Проверьте, что WebApp загружается с нового URL

**Проверка в браузере:**
```bash
NEW_URL="new-url-example"
echo "Откройте в браузере:"
echo "https://$NEW_URL.trycloudflare.com/webapp"
```

---

## 🐛 Troubleshooting: Частые проблемы

### Проблема 1: 502 Bad Gateway

**Причина:** Flask не запущен или не отвечает

**Решение:**
```bash
# Проверить, запущен ли Flask
ps aux | grep "src/webapp.py" | grep -v grep

# Если не запущен → запустить
cd /home/user/news_ai_bot
python3 src/webapp.py > logs/webapp.log 2>&1 &

# Проверить логи на ошибки
tail -50 logs/webapp.log
```

---

### Проблема 2: Бот открывает старый URL

**Причина:** .env файлы не обновлены ИЛИ бот не перезапущен

**Решение:**
```bash
# 1. Проверить .env файлы
grep CLOUDFLARE_TUNNEL_URL .env
grep CLOUDFLARE_TUNNEL_URL config_files/environment/.env

# 2. Если URL старый → обновить (см. Шаг 2.2)
OLD_URL="old-url"
NEW_URL="new-url"
sed -i '' "s|$OLD_URL|$NEW_URL|g" .env
sed -i '' "s|$OLD_URL|$NEW_URL|g" config_files/environment/.env

# 3. Перезапустить бота
pkill -f "telegram_bot/bot.py"
sleep 2
cd /home/user/news_ai_bot
PYTHONPATH=/home/user/news_ai_bot:$PYTHONPATH python3 telegram_bot/bot.py > logs/bot.log 2>&1 &

# 4. Проверить загруженный URL
python3 -c "from config.core.settings import WEBAPP_URL; print(WEBAPP_URL)"
```

---

### Проблема 3: Cloudflare Tunnel падает с ошибками

**Признаки:**
```
ERR failed to serve tunnel connection error="control stream encountered a failure"
ERR Retrying connection in up to 1m4s
```

**Решение:**
```bash
# Полностью перезапустить туннель
pkill cloudflared
sleep 2
cd /home/user/news_ai_bot
cloudflared tunnel --url http://localhost:8001 > logs/cloudflare.log 2>&1 &
sleep 5

# Получить новый URL и повторить всю процедуру
tail -20 logs/cloudflare.log | grep "trycloudflare.com"
```

---

### Проблема 4: Flask запущен, но не отвечает на запросы

**Решение:**
```bash
# Проверить, слушает ли Flask на порту 8001
lsof -i :8001

# Проверить локальный доступ
curl -v "http://localhost:8001/api/health"

# Проверить последние ошибки в логах
tail -100 logs/webapp.log | grep -i error

# Если есть ошибки → исправить и перезапустить
pkill -f "src/webapp.py"
sleep 2
python3 src/webapp.py > logs/webapp.log 2>&1 &
```

---

## 📋 Полный скрипт автоматизации

**Файл:** `scripts/update_cloudflare_url.sh`

```bash
#!/bin/bash

# Скрипт автоматического обновления Cloudflare URL
# Использование: ./scripts/update_cloudflare_url.sh OLD_URL NEW_URL

set -e  # Остановка при ошибке

OLD_URL=$1
NEW_URL=$2

if [ -z "$OLD_URL" ] || [ -z "$NEW_URL" ]; then
    echo "❌ Использование: $0 OLD_URL NEW_URL"
    echo "   Пример: $0 old-url-example new-url-example"
    exit 1
fi

echo "🔄 Обновление Cloudflare URL"
echo "   Старый: $OLD_URL"
echo "   Новый: $NEW_URL"
echo ""

# 1. Обновить Python конфигурацию
echo "📝 Обновление config/core/cloudflare.py..."
sed -i '' "s|$OLD_URL|$NEW_URL|g" config/core/cloudflare.py

# 2. Обновить .env файлы
echo "📝 Обновление .env файлов..."
sed -i '' "s|$OLD_URL|$NEW_URL|g" .env
sed -i '' "s|$OLD_URL|$NEW_URL|g" config_files/environment/.env

# 3. Обновить cloudflare-tunnel.yaml
echo "📝 Обновление cloudflare-tunnel.yaml..."
sed -i '' "s|$OLD_URL|$NEW_URL|g" cloudflare-tunnel.yaml

# 4. Обновить документацию
echo "📝 Обновление документации..."
FILES=(
    "README.md"
    "DEPLOYMENT_STATUS.md"
    "CLOUDFLARE_URL_AUDIT_REPORT.md"
    "CHANGELOG.md"
    "FINAL_SESSION_SUMMARY.md"
    "CURRENT_SERVICES_STATUS.md"
    "WEBAPP_FIX_CYRILLIC_HEADERS.md"
    "docs/reports/FINAL_TODO_REPORT.md"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        sed -i '' "s|$OLD_URL|$NEW_URL|g" "$file"
        echo "   ✅ $file"
    fi
done

# 5. Перезапустить Flask
echo ""
echo "🔄 Перезапуск Flask WebApp..."
pkill -f "src/webapp.py" || true
sleep 2
python3 src/webapp.py > logs/webapp.log 2>&1 &
sleep 5
echo "   ✅ Flask перезапущен"

# 6. Перезапустить бота
echo ""
echo "🔄 Перезапуск Telegram Bot..."
pkill -f "telegram_bot/bot.py" || true
sleep 2
PYTHONPATH=$(pwd):$PYTHONPATH python3 telegram_bot/bot.py > logs/bot.log 2>&1 &
sleep 5
echo "   ✅ Telegram Bot перезапущен"

# 7. Проверка
echo ""
echo "✅ Проверка результата..."
python3 -c "from config.core.settings import WEBAPP_URL; print(f'   WEBAPP_URL: {WEBAPP_URL}')"

echo ""
echo "🎉 Обновление завершено!"
echo ""
echo "Проверьте работу:"
echo "   • curl -s 'https://$NEW_URL.trycloudflare.com/api/health' | python3 -m json.tool"
echo "   • Telegram Bot: /dashboard"
```

**Использование:**
```bash
chmod +x scripts/update_cloudflare_url.sh
./scripts/update_cloudflare_url.sh old-url-example new-url-example
```

---

## 📊 Финальный чеклист

После выполнения всех шагов:

- [ ] ✅ Cloudflare Tunnel запущен с новым URL
- [ ] ✅ config/core/cloudflare.py обновлен
- [ ] ✅ .env файлы обновлены (корневой + config_files/environment/)
- [ ] ✅ cloudflare-tunnel.yaml обновлен
- [ ] ✅ Документация обновлена (8+ файлов)
- [ ] ✅ Flask WebApp перезапущен
- [ ] ✅ Telegram Bot перезапущен
- [ ] ✅ `WEBAPP_URL` загружает НОВЫЙ URL (проверено командой)
- [ ] ✅ API Health отвечает через Cloudflare
- [ ] ✅ WebApp открывается через бота с нового URL
- [ ] ✅ Нет упоминаний старого URL в коде (проверено grep)

---

## 📝 Примечания

### Источник истины для URL

**Приоритет загрузки:**
1. Переменная окружения `CLOUDFLARE_TUNNEL_URL` из .env
2. Default значение в `config/core/cloudflare.py`

**Цепочка использования:**
```
.env файлы
    ↓
config/core/cloudflare.py → CLOUDFLARE_TUNNEL_URL
    ↓
config/core/settings.py → WEBAPP_URL
    ↓
telegram_bot/handlers/dashboard.py → Открытие WebApp
```

### Quick Tunnel vs Named Tunnel

**Quick Tunnel (temporary):**
- Генерируется автоматически при каждом запуске
- Формат: `https://example.invalid`
- Не требует credentials файла
- Используется командой: `cloudflared tunnel --url http://localhost:8001`
- **Срок действия:** До остановки процесса

**Named Tunnel (permanent):**
- Постоянный URL
- Требует регистрации в Cloudflare Dashboard
- Использует `cloudflare-tunnel.yaml` конфигурацию
- Более стабильный для production

### Когда URL меняется

Quick Tunnel URL меняется при:
- Перезапуске cloudflared процесса
- Перезагрузке системы
- Падении туннеля

**Рекомендация:** Добавить в cron проверку и автообновление URL при изменении.

---

**Версия документа:** 1.0  
**Последнее обновление:** 2025-10-16  
**Следующая ревизия:** При обнаружении новых edge cases

