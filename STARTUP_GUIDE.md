# Правильный запуск PulseAI

## Быстрый старт

1. **Запустить сервисы:**
   ```bash
   ./start_services.sh
   ```

2. **Запустить Cloudflare Tunnel:**
   ```bash
   ./start_cloudflare.sh
   ```

3. **Обновить WebApp URL везде:**
   - Перезапустить бота (автоматически подхватывает `.env`):
     ```bash
     ./stop_services.sh && sleep 2 && ./start_services.sh
     ```
   - **Опционально**: Обновить Menu Button в Telegram Bot Dashboard:
     - Открыть [@BotFather](https://t.me/BotFather)
     - Bot Settings -> Menu Button
     - Вставить URL из вывода `start_cloudflare.sh`

## Важно

- `start_services.sh` **АВТОМАТИЧЕСКИ** убивает все старые процессы
- Если нужно остановить: `./stop_services.sh`
- Проверить статус: `./check_processes.sh`

## Решение проблем

### Если бот не работает (TelegramConflictError):
```bash
./stop_services.sh && sleep 2 && ./start_services.sh
```

### Если WebApp не открывается:
1. Проверить что Cloudflare работает: `./check_processes.sh`
2. Проверить актуальный URL в `.env`:
   ```bash
   grep WEBAPP_URL .env
   ```
3. Перезапустить Cloudflare: `./start_cloudflare.sh`
4. Перезапустить бота для подхвата нового URL:
   ```bash
   ./stop_services.sh && sleep 2 && ./start_services.sh
   ```
5. **Опционально**: Обновить Menu Button в Telegram Bot Dashboard

### Если процессы не останавливаются:
```bash
# Принудительная остановка всех процессов
pkill -9 -f "Python.*src/webapp.py"
pkill -9 -f "Python.*telegram_bot"
```

## Команды управления

| Команда | Описание |
|---------|----------|
| `./start_services.sh` | Запуск Flask + Telegram Bot |
| `./start_cloudflare.sh` | Запуск Cloudflare Tunnel |
| `./stop_services.sh` | Остановка всех сервисов |
| `./check_processes.sh` | Проверка статуса процессов |

## Workflow для разработки

```bash
# 1. Остановить всё
./stop_services.sh

# 2. Убедиться что ничего не осталось
ps aux | grep -E "Python.*(webapp|telegram)" | grep -v grep
# Должен быть пустой вывод

# 3. Запустить
./start_services.sh

# 4. Проверить что только по 1 экземпляру
./check_processes.sh
# Flask: 1 процесс
# Bot: 1 процесс

# 5. Запустить Cloudflare
./start_cloudflare.sh

# 6. Перезапустить бота для подхвата нового URL
./stop_services.sh && sleep 2 && ./start_services.sh

# 7. (Опционально) Обновить Menu Button в Telegram Bot Dashboard
```

## Логи

- **Сервисы**: `logs/scripts/start_services_*.log`
- **Остановка**: `logs/scripts/stop_services_*.log`
- **Telegram Bot**: `logs/bot.log`
- **Flask**: `logs/app.log`
- **Cloudflare**: `logs/cloudflare.log`

## Обновление URL при смене Cloudflare

### Автоматическое обновление (рекомендуется):
1. Запустить новый Cloudflare: `./start_cloudflare.sh` (обновит `.env`)
2. Перезапустить бота: `./stop_services.sh && sleep 2 && ./start_services.sh`
3. Бот автоматически подхватит новый URL из `.env`

### Ручное обновление (только если автоматика не работает):
1. Открыть `telegram_bot/handlers/start.py`
2. Обновить fallback URL (строка 9):
   ```python
   WEBAPP_URL = os.getenv("WEBAPP_URL", "НОВЫЙ_URL_ЗДЕСЬ")
   ```
3. Перезапустить бота

## Troubleshooting

### Множественные экземпляры процессов
**Симптом**: TelegramConflictError, несколько процессов в `ps aux`

**Решение**:
1. `./stop_services.sh`
2. `./start_services.sh` (автоматически убьет все дубликаты)

### Cloudflare Tunnel не работает
**Симптом**: WebApp не открывается, ошибка 530

**Решение**:
1. Проверить что Flask работает: `curl http://localhost:8001/webapp`
2. Перезапустить Cloudflare: `./start_cloudflare.sh`
3. Обновить Menu Button с новым URL

### Порт 8001 занят
**Симптом**: Flask не запускается

**Решение**:
```bash
# Найти процесс
lsof -i :8001

# Убить процесс
kill <PID>

# Или принудительно
pkill -9 -f "Python.*src/webapp.py"
```

## Безопасность

- **НИКОГДА** не запускайте несколько экземпляров одновременно
- **ВСЕГДА** используйте скрипты управления (`start_services.sh`, `stop_services.sh`)
- **ПРОВЕРЯЙТЕ** статус после изменений (`./check_processes.sh`)

---

**Версия**: 2.0
**Дата**: 2025-10-24
**Автор**: PulseAI Team
