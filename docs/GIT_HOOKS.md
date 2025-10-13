# Git Hooks PulseAI

Документация по git hooks для проекта PulseAI.

## 📋 Обзор

PulseAI использует git hooks для автоматической проверки качества кода перед коммитом и push.

### Доступные hooks:

1. **pre-commit** — проверка перед коммитом (быстрая)
2. **pre-push** — проверка перед push (строгая)

## 🔍 Pre-commit Hook

Быстрая проверка только staged файлов перед созданием коммита.

### Что проверяет:

✅ **Синтаксис Python** — все staged `.py` файлы компилируются без ошибок  
✅ **Flake8 (критичные ошибки)** — только E9, F63, F7, F82 (если flake8 установлен)  
✅ **Базовые проблемы** — наличие print(), TODO/FIXME метки  

### Использование:

```bash
# Обычный коммит (с проверками)
git commit -m "feat: новая фича"

# Пропустить проверки
git commit --no-verify -m "feat: новая фича"

# Или через переменную окружения
SKIP_HOOKS=1 git commit -m "feat: новая фича"
```

### Что НЕ проверяет:

- ❌ Форматирование Black (слишком медленно)
- ❌ Все ошибки Flake8 (только критичные)
- ❌ Сортировку импортов (isort)

### Требования:

- ✅ Python 3.6+
- ⚠️ Flake8 (опционально, рекомендуется)

## 🚀 Pre-push Hook

Строгая проверка всего проекта перед отправкой в репозиторий.

### Что проверяет:

#### Если установлены Black и Flake8:
✅ Запускает `scripts/strict_check.sh`:
  - Black форматирование всего проекта
  - Flake8 со строгими настройками
  - isort сортировка импортов (если установлен)
  - Статистика кода

#### Если инструментов нет (fallback):
✅ **Синтаксис Python** — все файлы проекта  
✅ **Flake8 (критичные ошибки)** — E9, F63, F7, F82  
✅ **Debug точки** — проверка на pdb.set_trace() и breakpoint()  

### Использование:

```bash
# Обычный push (с проверками)
git push origin main

# Пропустить проверки
git push origin main --no-verify

# Или через переменную окружения
SKIP_HOOKS=1 git push origin main
```

### Требования:

#### Минимальные:
- ✅ Python 3.6+

#### Рекомендуемые:
- ⚠️ Black — `pip install black`
- ⚠️ Flake8 — `pip install flake8`
- ⚠️ isort — `pip install isort` (опционально)

## 🛠️ Установка инструментов

### Базовая установка:

```bash
pip install flake8
```

### Полная установка (рекомендуется):

```bash
pip install black flake8 isort
```

### Проверка установки:

```bash
python3 -c "import black; print('Black:', black.__version__)"
python3 -c "import flake8; print('Flake8: OK')"
python3 -c "import isort; print('isort:', isort.__version__)"
```

## 💡 Ручная проверка качества

### Быстрая проверка (без изменений):

```bash
# Строгая проверка (требует black + flake8)
./scripts/strict_check.sh
```

### Автоисправление и push:

```bash
# Умный push с автоисправлением (требует black + flake8)
./scripts/smart_push.sh

# Или через Make
make smart-push
```

### Детальная проверка и исправление:

```bash
./scripts/detailed_fix.sh

# Или через Make
make detailed-fix
```

## 🔧 Настройка hooks

### Отключение конкретного hook:

```bash
# Временно
chmod -x .git/hooks/pre-commit
chmod -x .git/hooks/pre-push

# Включить обратно
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

### Переменные окружения:

```bash
# Пропустить все hooks для одной команды
SKIP_HOOKS=1 git commit -m "message"
SKIP_HOOKS=1 git push origin main

# Установить глобально (не рекомендуется)
export SKIP_HOOKS=1
```

### Полное отключение:

```bash
# Удалить hooks
rm .git/hooks/pre-commit
rm .git/hooks/pre-push

# Или переименовать
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
mv .git/hooks/pre-push .git/hooks/pre-push.disabled
```

## 📊 Статус проверок

### Pre-commit (быстро, ~1-5 сек):
```
🔍 Pre-commit проверки PulseAI
==================================
📝 Проверяю 5 Python файл(ов)...
🐍 Проверка синтаксиса Python...
✅ Синтаксис Python корректен
🔍 Проверка Flake8 (только критичные ошибки)...
✅ Flake8 проверка пройдена
🔎 Проверка на базовые проблемы...
✅ Pre-commit проверки пройдены
```

### Pre-push (строго, ~10-30 сек):
```
🚀 Pre-push проверки PulseAI
==================================
✅ Flake8 доступен
✅ Black доступен
🔍 Запуск строгой проверки качества кода...
📝 Проверка Black форматирования...
✅ Black форматирование корректно
🔍 Строгая проверка Flake8...
✅ Flake8 строгая проверка пройдена
✅ Все проверки пройдены успешно!
```

## ⚠️ Частые проблемы

### "Black недоступен"

```bash
# Установите Black
pip install black

# Или пропустите проверку
git push --no-verify
```

### "Flake8 недоступен"

```bash
# Установите Flake8
pip install flake8

# Проверка будет упрощённой (только синтаксис)
```

### "Black нашел проблемы форматирования"

```bash
# Автоматически исправить
python3 -m black .

# Добавить изменения
git add -A

# Или пропустить
git push --no-verify
```

### "Flake8 нашёл критичные ошибки"

```bash
# Посмотреть ошибки
python3 -m flake8 .

# Исправить вручную
# Затем
git add -A
git commit -m "fix: исправление ошибок flake8"
```

## 🎯 Best Practices

### Рекомендуемый workflow:

1. **Разработка** — пишите код
2. **Перед коммитом** — hook проверит staged файлы (~1-5 сек)
3. **Перед push** — hook проверит весь проект (~10-30 сек)
4. **При ошибках** — исправьте или используйте `--no-verify` для срочных случаев

### Когда использовать `--no-verify`:

✅ **Можно:**
- WIP коммиты в feature ветках
- Срочные hotfix
- Экспериментальный код

❌ **Не рекомендуется:**
- Коммиты в main/master
- Production releases
- Pull requests

### Регулярная проверка качества:

```bash
# Еженедельно
./scripts/strict_check.sh

# Перед важным релизом
./scripts/detailed_fix.sh
python3 -m black .
python3 -m flake8 .
```

## 📝 Конфигурация

### Flake8 настройки (.flake8):

```ini
[flake8]
max-line-length = 100
ignore = E203, W503
exclude = venv, node_modules, __pycache__, webapp
```

### Black настройки (pyproject.toml):

```toml
[tool.black]
line-length = 100
target-version = ['py38']
exclude = 'venv|node_modules|__pycache__|webapp'
```

## 🔗 Связанные документы

- [CONTRIBUTING.md](CONTRIBUTING.md) — руководство по участию в разработке
- [CODE_QUALITY.md](guides/CODE_QUALITY.md) — система качества кода
- [DEVELOPMENT.md](guides/DEVELOPMENT.md) — руководство по разработке

## 📞 Поддержка

Проблемы с git hooks? 

1. Проверьте установку инструментов: `python3 -c "import black, flake8"`
2. Попробуйте ручную проверку: `./scripts/strict_check.sh`
3. Посмотрите логи: hook выводит детальную информацию
4. В крайнем случае: `git push --no-verify`

---

*PulseAI - AI-powered news and events platform* 🚀

