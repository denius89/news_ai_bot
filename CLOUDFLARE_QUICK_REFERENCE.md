# ⚡ Cloudflare URL - Быстрая справка

**Полная инструкция:** [docs/CLOUDFLARE_URL_UPDATE_GUIDE.md](docs/CLOUDFLARE_URL_UPDATE_GUIDE.md)

---

## 🚀 Быстрый старт

### Вариант 1: Автоматический скрипт (РЕКОМЕНДУЕТСЯ)

```bash
# Запустить скрипт автоматического обновления
./scripts/update_cloudflare_url.sh OLD_URL NEW_URL

# Пример:
./scripts/update_cloudflare_url.sh founded-shopper-miss-kruger new-random-words
```

Скрипт автоматически:
- ✅ Обновит все конфигурационные файлы
- ✅ Обновит .env файлы
- ✅ Обновит документацию
- ✅ Перезапустит Flask и Telegram Bot
- ✅ Проверит результат

---

### Вариант 2: Ручное обновление

```bash
# 1. Перезапустить Cloudflare Tunnel
pkill cloudflared
cloudflared tunnel --url http://localhost:8001 > logs/cloudflare.log 2>&1 &
sleep 5
tail -20 logs/cloudflare.log | grep "trycloudflare.com"

# 2. Обновить конфиги (замените OLD и NEW на ваши URL)
OLD="old-url"
NEW="new-url"
sed -i '' "s|$OLD|$NEW|g" config/core/cloudflare.py
sed -i '' "s|https://$OLD.trycloudflare.com|https://$NEW.trycloudflare.com|g" .env
sed -i '' "s|https://$OLD.trycloudflare.com|https://$NEW.trycloudflare.com|g" config_files/environment/.env

# 3. Перезапустить Flask
pkill -f "src/webapp.py"
python3 src/webapp.py > logs/webapp.log 2>&1 &

# 4. Перезапустить бота
pkill -f "telegram_bot/bot.py"
PYTHONPATH=$(pwd):$PYTHONPATH python3 telegram_bot/bot.py > logs/bot.log 2>&1 &

# 5. Проверить
python3 -c "from config.core.settings import WEBAPP_URL; print(WEBAPP_URL)"
```

---

## ⚠️ КРИТИЧНЫЕ МОМЕНТЫ

### 1. Обязательно обновить .env файлы!

```bash
# Без этого бот и Flask загрузят старый URL
.env
config_files/environment/.env
```

### 2. Обязательно перезапустить сервисы!

```bash
# Без перезапуска сервисы продолжат использовать старый URL из памяти
Flask WebApp
Telegram Bot
```

### 3. Проверить загруженный URL

```bash
# Эта команда покажет, какой URL реально загружен в системе
python3 -c "from config.core.settings import WEBAPP_URL; print(WEBAPP_URL)"

# Должно вывести новый URL!
```

---

## 🐛 Быстрое исправление проблем

### Проблема: 502 ошибка

```bash
# Flask не запущен → запустить
python3 src/webapp.py > logs/webapp.log 2>&1 &
```

### Проблема: Бот открывает старый URL

```bash
# 1. Обновить .env
sed -i '' "s|OLD|NEW|g" .env
sed -i '' "s|OLD|NEW|g" config_files/environment/.env

# 2. Перезапустить бота
pkill -f "telegram_bot/bot.py"
PYTHONPATH=$(pwd):$PYTHONPATH python3 telegram_bot/bot.py > logs/bot.log 2>&1 &

# 3. Проверить
python3 -c "from config.core.settings import WEBAPP_URL; print(WEBAPP_URL)"
```

### Проблема: Cloudflare падает

```bash
# Перезапустить туннель
pkill cloudflared
cloudflared tunnel --url http://localhost:8001 > logs/cloudflare.log 2>&1 &
```

---

## 📋 Финальная проверка (1 команда)

```bash
echo "=== ПРОВЕРКА ===" && \
echo "Flask:" && ps aux | grep "src/webapp.py" | grep -v grep | head -1 | awk '{print $2}' && \
echo "Bot:" && ps aux | grep "telegram_bot/bot.py" | grep -v grep | head -1 | awk '{print $2}' && \
echo "URL:" && python3 -c "from config.core.settings import WEBAPP_URL; print(WEBAPP_URL)"
```

---

## 🔗 Полезные ссылки

- **Полная инструкция:** [docs/CLOUDFLARE_URL_UPDATE_GUIDE.md](docs/CLOUDFLARE_URL_UPDATE_GUIDE.md)
- **Скрипт автоматизации:** [scripts/update_cloudflare_url.sh](scripts/update_cloudflare_url.sh)
- **Текущий статус:** [DEPLOYMENT_STATUS.md](DEPLOYMENT_STATUS.md)

