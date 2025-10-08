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

### API Keys:
- Безопасное хранение токенов
- Ротация ключей
- Мониторинг использования

### Доступ:
- Контроль доступа к API
- Аутентификация пользователей
- Авторизация операций

---

*Это руководство объединяет информацию из CLOUDFLARE_CONFIG.md, DEPLOY.md и DATABASE_MAINTENANCE.md*
