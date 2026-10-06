# GitHub Actions Workflows

Документация по автоматическим workflows проекта PulseAI.

## 📋 Обзор workflows

### 1. tests.yml — Основной CI

**Триггеры:**
- Push в `main`
- Pull requests в `main`

**Что делает:**
- ✅ Запускает unit тесты (`pytest tests/unit`)
- ✅ Запускает все тесты с покрытием кода
- ✅ Проверяет критичные ошибки Flake8 (E9, F63, F7, F82)
- ✅ Загружает отчёт о покрытии в Codecov

**Время выполнения:** ~5-15 минут  
**Timeout:** 15 минут

**Статус:** 
![Tests](https://github.com/repository-owner/news_ai_bot/actions/workflows/tests.yml/badge.svg?branch=main)

---

### 2. integration.yml — Интеграционные тесты

**Триггеры:**
- Push в `main`
- Manual dispatch (запуск вручную)

**Что делает:**
- ✅ Запускает интеграционные тесты (`pytest tests/integration`)
- ✅ Использует секреты для подключения к Supabase, OpenAI, DeepL
- ✅ Загружает логи при ошибках

**Время выполнения:** ~10-30 минут  
**Timeout:** 30 минут

**Требует секреты:**
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `OPENAI_API_KEY`
- `DEEPL_API_KEY`

---

### 3. code-quality.yml — Проверки качества кода

**Триггеры:**
- Pull requests в `main`
- Manual dispatch

**Что делает:**
- ✅ Black форматирование (`--check`)
- ✅ Flake8 полная проверка
- ✅ isort сортировка импортов
- ✅ mypy type checking (опционально)

**Время выполнения:** ~3-10 минут  
**Timeout:** 10 минут

**Note:** Все проверки `continue-on-error: true` — не блокируют PR

---

### 4. daily-digest.yml — Ежедневные дайджесты

**Триггеры:**
- Schedule: `0 7 * * *` (каждый день в 07:00 UTC = 09:00 Warsaw)
- Manual dispatch

**Что делает:**
- ✅ Запускает генерацию и отправку ежедневных дайджестов
- ✅ Использует `tools/send_daily_digests.py`
- ✅ Загружает логи при ошибках

**Время выполнения:** ~5-30 минут  
**Timeout:** 30 минут

**Требует секреты:**
- `TELEGRAM_BOT_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `OPENAI_API_KEY`

---

## 🚀 Оптимизации

### Кеширование dependencies

Все workflows используют кеширование pip зависимостей:

```yaml
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

**Эффект:** Ускорение установки зависимостей с ~2-3 минут до ~10-30 секунд

### Timeouts

Все workflows имеют `timeout-minutes` для предотвращения зависания:
- tests.yml: 15 минут
- integration.yml: 30 минут
- code-quality.yml: 10 минут
- daily-digest.yml: 30 минут

### Artifacts

При ошибках автоматически сохраняются логи:

```yaml
- uses: actions/upload-artifact@v3
  if: failure()
  with:
    name: test-logs
    path: logs/*.log
    retention-days: 7
```

---

## 💡 Локальная проверка

Перед push рекомендуется запустить проверки локально:

### Unit тесты:
```bash
pytest tests/unit -v
```

### Все тесты с покрытием:
```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Качество кода:
```bash
# Строгая проверка
./scripts/strict_check.sh

# Или вручную
python -m black --check .
python -m flake8 .
python -m isort --check-only .
```

### Интеграционные тесты:
```bash
pytest tests/integration -v
```

---

## 🔧 Настройка секретов

Для работы workflows требуются следующие GitHub Secrets:

### Repository Secrets (Settings → Secrets and variables → Actions):

1. **TELEGRAM_BOT_TOKEN** — токен Telegram бота
2. **SUPABASE_URL** — URL Supabase проекта
3. **SUPABASE_KEY** — Service key Supabase
4. **SUPABASE_SERVICE_KEY** — Alias для SUPABASE_KEY
5. **OPENAI_API_KEY** — API ключ OpenAI
6. **DEEPL_API_KEY** — API ключ DeepL (опционально)

---

## 📊 Мониторинг

### Просмотр статуса workflows:

1. Перейдите в вкладку **Actions** на GitHub
2. Выберите нужный workflow слева
3. Просмотрите историю запусков

### Badges в README:

```markdown
![Tests](https://github.com/repository-owner/news_ai_bot/actions/workflows/tests.yml/badge.svg?branch=main)
```

### Ручной запуск:

Workflows с `workflow_dispatch` можно запустить вручную:
1. Actions → выбрать workflow
2. Нажать "Run workflow"
3. Выбрать ветку
4. Нажать "Run workflow"

---

## 🐛 Troubleshooting

### Workflow fails with "Module not found"

**Причина:** Не установлены зависимости или некорректный PYTHONPATH

**Решение:**
1. Проверьте `requirements.txt` — все зависимости указаны?
2. Убедитесь что кеш актуален (можно очистить вручную)

### Timeout errors

**Причина:** Workflow выполняется дольше указанного timeout

**Решение:**
1. Увеличьте `timeout-minutes` в workflow
2. Оптимизируйте тесты (уберите медленные)
3. Проверьте нет ли зависших процессов

### Integration tests fail

**Причина:** Секреты не настроены или неверные

**Решение:**
1. Проверьте Settings → Secrets → Actions
2. Убедитесь что все секреты установлены
3. Проверьте права доступа к Supabase/OpenAI

### Cache issues

**Причина:** Устаревший кеш с несовместимыми зависимостями

**Решение:**
```bash
# Изменить ключ кеша в workflow (добавить версию)
key: ${{ runner.os }}-pip-v2-${{ hashFiles('requirements.txt') }}
```

---

## 📝 Best Practices

### При создании PR:

1. ✅ Запустите тесты локально: `pytest tests/unit`
2. ✅ Проверьте качество кода: `./scripts/strict_check.sh`
3. ✅ Убедитесь что все workflows проходят
4. ✅ Просмотрите логи при ошибках

### При merge в main:

1. ✅ Все workflows должны пройти успешно
2. ✅ Code quality checks не должны показывать критичных ошибок
3. ✅ Coverage не должен упасть значительно

### Регулярное обслуживание:

1. 📅 Еженедельно проверяйте failed workflows
2. 📅 Ежемесячно обновляйте GitHub Actions versions (`@v4` → `@v5`)
3. 📅 Очищайте старые artifacts (автоматически через 7 дней)

---

## 🔗 Связанные документы

- [Git Hooks](../../docs/GIT_HOOKS.md) — локальные проверки перед commit/push
- [Testing Guide](../../docs/guides/DEVELOPMENT.md) — руководство по тестированию
- [Code Quality](../../docs/guides/CODE_QUALITY.md) — стандарты качества кода

---

*PulseAI - AI-powered news and events platform* 🚀

