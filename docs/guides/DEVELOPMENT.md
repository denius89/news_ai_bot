# 🛠️ PulseAI Development Guide

*Объединенное руководство по разработке и развертыванию*  
*Обновлено: 2025-10-08 09:34:46*

## 📋 Содержание

- [Быстрый старт](#быстрый-старт)
- [Архитектура](#архитектура)
- [Развертывание](#развертывание)
- [Порты и сервисы](#порты-и-сервисы)
- [Отладка](#отладка)
- [Команды Makefile](#команды-makefile)

## 🚀 Быстрый старт

```bash
# Запустить все сервисы
make start

# Проверить статус
make status

# Остановить все сервисы
make stop
```

## 🏗️ Архитектура

### Production Ready Architecture

**Архитектура:**
```
Cloudflare Tunnel → Flask:8001 → React Static + API
```

### Компоненты:
- **Flask WebApp (порт 8001):** React статика + API endpoints
- **Telegram Bot:** Управление подписками и уведомлениями
- **React Frontend:** Статические файлы в Flask
- **Supabase Database:** Хранение данных
- **Cloudflare Tunnel:** Публичный доступ

## 🚀 Развертывание

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

## 🔌 Порты и сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| Flask WebApp | 8001 | React статика + API |
| Telegram Bot | - | Polling режим |
| Cloudflare Tunnel | - | Публичный доступ |

## 🐛 Отладка

### Проверка процессов:
```bash
make check-ports
make logs
```

### Проверка качества кода:
```bash
make detailed-fix
make strict-check
```

## 📋 Команды Makefile

### Основные команды:
- `make start` - Запустить все сервисы
- `make stop` - Остановить все сервисы
- `make restart` - Перезапустить сервисы
- `make status` - Проверить статус

### Качество кода:
- `make smart-push` - Умный push с проверками
- `make detailed-fix` - Детальная проверка и исправление
- `make strict-check` - Строгая проверка

### Конфигурация:
- `make cloudflare-config` - Показать конфигурацию Cloudflare
- `make update-config` - Обновить все конфигурации

---

*Это руководство объединяет информацию из DEVELOPMENT_GUIDE.md, DEPLOYMENT_GUIDE.md и PORTS.md*
