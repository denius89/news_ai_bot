# 🌐 PulseAI Infrastructure Guide

*Объединенное руководство по инфраструктуре и конфигурации*  
*Обновлено: 2025-10-08 09:38:39*

## 📋 Содержание

- [Cloudflare Configuration](#cloudflare-configuration)
- [Deployment](#deployment)
- [Database Maintenance](#database-maintenance)
- [Monitoring](#monitoring)
- [Security](#security)

## 🌐 Cloudflare Configuration

### Централизованная конфигурация
Все настройки Cloudflare Tunnel управляются через единый файл `config/cloudflare.py`.

### Основные компоненты:
- **CLOUDFLARE_TUNNEL_URL** - Публичный URL туннеля
- **CLOUDFLARE_LOCAL_URL** - Локальный URL для разработки
- **Автоматическое обновление** конфигураций

### Команды управления:
```bash
# Показать текущую конфигурацию
make cloudflare-config

# Обновить все конфигурации
make update-config
```

## 🚀 Deployment

### Локальная разработка:
```bash
# Установка зависимостей
pip install -r requirements.txt
npm install --prefix webapp

# Запуск сервисов
make start
```

### Production развертывание:
```bash
# Настройка Cloudflare Tunnel
make cloudflare-config

# Обновление конфигураций
make update-config

# Запуск в production режиме
APP_ENV=production make start
```

### Архитектура развертывания:
```
Cloudflare Tunnel → Flask:8001 → React Static + API
```

## 🗄️ Database Maintenance

### Миграции:
- Автоматические миграции при запуске
- Ручные миграции через скрипты
- Откат изменений при необходимости

### Бэкапы:
- Регулярные автоматические бэкапы
- Ручные бэкапы перед важными изменениями
- Восстановление из бэкапов

### Мониторинг:
- Отслеживание производительности
- Мониторинг использования ресурсов
- Алерты при проблемах

## 📊 Monitoring

### Метрики:
- Производительность API
- Использование ресурсов
- Ошибки и исключения
- Пользовательская активность

### Логирование:
- Структурированные логи
- Различные уровни логирования
- Централизованный сбор логов

## 🔒 Security

### Telegram WebApp Authentication Flow

PulseAI использует безопасную аутентификацию через Telegram WebApp с HMAC SHA256 проверкой:

```python
# 1. Получение initData от Telegram WebApp
init_data = request.headers.get('X-Telegram-Init-Data')

# 2. Проверка подлинности через HMAC SHA256
verified_data = verify_telegram_webapp_data(init_data, bot_token)

# 3. Извлечение данных пользователя
if verified_data:
    user_data = extract_user_from_verified_data(verified_data)
```

### Name Normalization System

Система нормализации имён защищает от:
- Emoji-only имён: `🔥🔥🔥` → `User #<user_id>`
- Невидимых символов: `John\u200bDoe` → `JohnDoe`
- Стилизованных Unicode: `𝕀𝕧𝕒𝕟` → `Ivan`
- Испорченной кодировки: `ÐÐ°Ð½` → `Иван`

### Основные принципы безопасности:
- **HMAC SHA256** - криптографическая проверка данных Telegram
- **HTTPS everywhere** - все соединения зашифрованы
- **Session security** - защищённые куки и сессии
- **CORS настройки** - ограничение доступа по доменам
- **Environment variables** - секреты не в коде
- **Database security** - параметризованные запросы

### Настройки безопасности:
```bash
# Обязательные переменные окружения
TELEGRAM_BOT_TOKEN=your_bot_token
FLASK_SECRET_KEY=your_secret_key_32_chars_min
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

### Flask Session Configuration:
```python
app.config.update(
    SECRET_KEY=os.getenv('FLASK_SECRET_KEY'),
    SESSION_COOKIE_HTTPONLY=True,      # Защита от XSS
    SESSION_COOKIE_SECURE=True,        # Только HTTPS
    SESSION_COOKIE_SAMESITE='Lax',     # Защита от CSRF
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
)
```

### CORS конфигурация:
```python
CORS(app, origins=[
    "https://*.trycloudflare.com",
    "https://telegram.org",
    "https://web.telegram.org",
    "https://t.me"
])
```

### Security Monitoring:
- Логирование всех попыток аутентификации
- Мониторинг неудачных попыток входа
- Алерты при подозрительной активности
- Регулярная проверка логов безопасности

### API Keys:
- Безопасное хранение токенов
- Ротация ключей
- Мониторинг использования

### Доступ:
- Контроль доступа к API
- Аутентификация пользователей
- Авторизация операций

Подробнее см. [SECURITY.md](../SECURITY.md)

---

*Это руководство объединяет информацию из CLOUDFLARE_CONFIG.md, DEPLOY.md и DATABASE_MAINTENANCE.md*
