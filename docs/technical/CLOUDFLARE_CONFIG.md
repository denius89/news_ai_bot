# 🌐 Cloudflare Tunnel Configuration

Единое место для управления конфигурацией Cloudflare Tunnel в проекте PulseAI.

## 📁 Структура файлов

```
config/
├── cloudflare.py          # Основной конфиг Cloudflare
└── settings.py            # Импортирует cloudflare.py

scripts/
├── generate_vite_config.py    # Генератор конфига Vite
└── update_cloudflare_config.py # Обновление всех конфигов

webapp/
└── vite.config.ts         # Автогенерируемый конфиг Vite
```

## 🔧 Основные компоненты

### `config/cloudflare.py`
- **CLOUDFLARE_TUNNEL_URL** - основной URL туннеля
- **CLOUDFLARE_LOCAL_URL** - локальный URL для туннеля
- **CLOUDFLARE_TUNNEL_COMMAND** - команда запуска туннеля
- Функции для получения URL различных сервисов
- Валидация конфигурации

### `scripts/generate_vite_config.py`
- Генерирует `webapp/vite.config.ts` с актуальными хостами
- Извлекает домен из Cloudflare URL
- Обновляет `allowedHosts` для Vite

### `scripts/update_cloudflare_config.py`
- Обновляет все конфигурации проекта
- Обновляет документацию
- Показывает текущую конфигурацию

## 🚀 Использование

### Показать текущую конфигурацию
```bash
make cloudflare-config
```

### Обновить все конфигурации
```bash
make update-config
```

### Обновить только Vite конфиг
```bash
python3 scripts/generate_vite_config.py
```

### Обновить документацию
```bash
python3 scripts/update_cloudflare_config.py
```

## 🔄 Автоматическое обновление

При изменении URL Cloudflare Tunnel:

1. **Обновите переменную окружения:**
   ```bash
   export CLOUDFLARE_TUNNEL_URL="https://example.invalid"
   ```

2. **Или обновите `.env` файл:**
   ```
   CLOUDFLARE_TUNNEL_URL=https://example.invalid
   ```

3. **Запустите обновление:**
   ```bash
   make update-config
   ```

## 📋 Что обновляется автоматически

- ✅ `webapp/vite.config.ts` - allowedHosts для Vite
- ✅ `DEPLOYMENT_GUIDE.md` - URL в документации
- ✅ `DEVELOPMENT_GUIDE.md` - URL в документации
- ✅ `start_services.sh` - URL в выводе скрипта
- ✅ Все импорты в Python коде

## 🎯 Функции API

### Основные функции
```python
from config.cloudflare import (
    get_webapp_url,      # URL WebApp
    get_api_url,         # Базовый URL API
    get_health_url,      # URL health check
    get_dashboard_url,   # URL dashboard
    get_vite_allowed_hosts,  # Хосты для Vite
    get_deployment_info,     # Полная информация
    validate_cloudflare_config  # Валидация
)
```

### Пример использования
```python
from config.cloudflare import get_webapp_url, get_deployment_info

# Получить URL WebApp
webapp_url = get_webapp_url()
print(f"WebApp: {webapp_url}")

# Получить всю информацию
info = get_deployment_info()
for key, value in info.items():
    print(f"{key}: {value}")
```

## 🔍 Валидация

Система автоматически проверяет:
- ✅ URL содержит `trycloudflare.com`
- ✅ Локальный URL корректен (`http://localhost:8001`)
- ✅ Все функции возвращают валидные URL

## 📊 Мониторинг

### Проверка конфигурации
```bash
python3 -c "
from config.cloudflare import validate_cloudflare_config, get_deployment_info
print('Валидация:', validate_cloudflare_config())
print('Конфигурация:', get_deployment_info())
"
```

### Логи обновления
Все обновления логируются в консоль с подробной информацией о том, что было изменено.

## 🛠️ Разработка

### Добавление новых URL
1. Добавьте функцию в `config/cloudflare.py`
2. Обновите `get_deployment_info()` если нужно
3. Добавьте тесты валидации

### Интеграция с новыми сервисами
1. Создайте функцию получения URL в `cloudflare.py`
2. Обновите скрипты генерации конфигов
3. Добавьте команды в Makefile

## 🎉 Преимущества

- ✅ **Единое место** для всех Cloudflare настроек
- ✅ **Автоматическое обновление** всех конфигов
- ✅ **Валидация** конфигурации
- ✅ **Обратная совместимость** с существующим кодом
- ✅ **Простота использования** через Makefile
- ✅ **Документированность** всех изменений
