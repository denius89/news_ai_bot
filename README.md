# PulseAI

![Tests – main](https://github.com/denius89/news_ai_bot/actions/workflows/tests.yml/badge.svg?branch=main)
![Code Quality](https://img.shields.io/badge/code%20quality-A%20-green)
![Architecture](https://img.shields.io/badge/architecture-unified-blue)
![Performance](https://img.shields.io/badge/performance-optimized-orange)

**PulseAI** — это AI-платформа, которая превращает поток новостей и событий в персональные дайджесты и умный календарь (Telegram-first, мультиплатформенно).

## 📚 Документация

**Вся документация находится в папке [`docs/`](docs/):**

- 📖 **[Документация](docs/README.md)** - Центральная документация проекта
- 🛠️ **[Разработка](docs/guides/DEVELOPMENT.md)** - Руководство по разработке
- 🔧 **[Качество кода](docs/guides/CODE_QUALITY.md)** - Система качества кода
- 🎨 **[Фронтенд](docs/guides/FRONTEND.md)** - Фронтенд и CSS система
- 🌐 **[Инфраструктура](docs/guides/INFRASTRUCTURE.md)** - Инфраструктура и конфигурация

## 🚀 Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/denius89/news_ai_bot.git
cd news_ai_bot

# Установить зависимости
pip install -r requirements.txt
npm install --prefix webapp

# Запустить все сервисы
make start

# Проверить статус
make status
```

## 📋 Основные команды

```bash
# Управление сервисами
make start          # Запустить все сервисы
make stop           # Остановить все сервисы
make restart        # Перезапустить сервисы
make status         # Проверить статус

# Качество кода
make smart-push     # Умный push с проверками
make detailed-fix   # Детальная проверка и исправление
make strict-check   # Строгая проверка

# Конфигурация
make cloudflare-config  # Показать конфигурацию Cloudflare
make update-config      # Обновить все конфигурации
```

## 🏗️ Архитектура

```
Cloudflare Tunnel → Flask:8001 → React Static + API
```

### Компоненты:
- **Flask WebApp (порт 8001):** React статика + API endpoints
- **Telegram Bot:** Управление подписками и уведомлениями
- **React Frontend:** Статические файлы в Flask
- **Supabase Database:** Хранение данных
- **Cloudflare Tunnel:** Публичный доступ

## 📊 Статистика проекта

- **Python файлов:** 200+
- **React компонентов:** 15+
- **API endpoints:** 25+
- **Тестов:** 50+
- **Документации:** 20+ файлов

## 🤝 Участие в проекте

См. [CONTRIBUTING.md](docs/CONTRIBUTING.md) для детальной информации о том, как участвовать в разработке.

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. [LICENSE](LICENSE) файл для деталей.

## 📞 Поддержка

- 📖 **Документация:** [docs/README.md](docs/README.md)
- 🐛 **Баги:** [Issues](https://github.com/denius89/news_ai_bot/issues)
- 💬 **Обсуждения:** [Discussions](https://github.com/denius89/news_ai_bot/discussions)

---

*PulseAI - AI-powered news and events platform* 🚀
