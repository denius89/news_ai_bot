# 🔧 PulseAI Development Scripts

Набор скриптов для удобной разработки и деплоя PulseAI.

## 📋 Доступные скрипты

### 🚀 `dev-push.sh` - Умный push с проверками
```bash
./scripts/dev-push.sh [commit_message]
```

**Что делает:**
1. Запускает все проверки (Black + Flake8)
2. Форматирует код автоматически
3. Коммитит изменения
4. Пушит в GitHub

**Примеры использования:**
```bash
# Автоматическое сообщение коммита
./scripts/dev-push.sh

# Своё сообщение коммита
./scripts/dev-push.sh "fix: исправил баг в парсере"
```

### 🔍 `pre-push.sh` - Проверки перед push
```bash
./scripts/pre-push.sh
```

**Что делает:**
1. Black форматирование
2. Flake8 проверка (только критические ошибки)
3. Запуск критических тестов

## 🛠️ Makefile команды

### Основные команды разработки:
```bash
make pre-push          # Black + Flake8 + проверки
make format            # Только Black форматирование
make lint              # Только Flake8 (критические ошибки)
make check             # Полная проверка + тесты
```

### Запуск приложений:
```bash
make run-bot           # Запуск Telegram бота
make run-web           # Запуск WebApp
make run-all           # Запуск всех сервисов
make dev               # Безопасный запуск для разработки
```

### Управление базой данных:
```bash
make db-check          # Проверка структуры БД
make db-cleanup        # Очистка БД
make db-optimize       # Оптимизация БД
```

## 🔧 Настройка pre-commit hooks

Pre-commit hooks уже настроены и будут автоматически запускаться при каждом `git push`.

**Что проверяется:**
- ✅ Black форматирование (автоматическое исправление)
- ✅ Flake8 линтер (только критические ошибки)
- ✅ Исключены инструменты разработки (`tools/`, `venv/`, etc.)

## 🚨 Troubleshooting

### Если pre-push hook падает:
```bash
# Запустить проверки вручную
make pre-push

# Или пропустить проверки (не рекомендуется)
git push --no-verify
```

### Если нужно исправить форматирование:
```bash
make format            # Автоматическое исправление
make lint              # Проверка критических ошибок
```

### Если проблемы с портами:
```bash
make check-ports       # Проверить занятые порты
make free-ports        # Освободить порты
```

## 📝 Рекомендации

1. **Всегда используйте `make pre-push` перед коммитом**
2. **Для быстрого деплоя используйте `./scripts/dev-push.sh`**
3. **При проблемах с линтером - сначала `make format`, потом `make lint`**
4. **Критические ошибки (F821, F811) нужно исправлять обязательно**

## 🎯 Workflow

```bash
# 1. Разработка
make run-bot &          # В фоне
make run-web            # В отдельном терминале

# 2. Тестирование
make pre-push           # Проверки
make test               # Полные тесты

# 3. Деплой
./scripts/dev-push.sh   # Умный push
```

---

**💡 Совет:** Настройте алиасы в вашем shell для ещё большего удобства:
```bash
alias push='./scripts/dev-push.sh'
alias check='make pre-push'
alias fmt='make format'
```
