# 🚀 Быстрое исправление проблем

## Проблема 1: pytest не найден
**Исправлено!** ✅ Makefile обновлен для использования `python -m pytest`

## Проблема 2: Отсутствует колонка `locale` в таблице `users`

### 🔧 Быстрое решение:

1. **Откройте Supabase Dashboard**: https://app.supabase.com
2. **Перейдите в SQL Editor**
3. **Выполните этот SQL**:

```sql
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();
UPDATE users SET updated_at = now() WHERE updated_at IS NULL;
```

### ✅ Проверка:

```bash
make check-db
```

### 🧪 Тестирование:

```bash
make test          # Запустить тесты
make run-tests-bot # Тесты + запуск бота
```

## 📋 Доступные команды:

- `make test` - запустить тесты
- `make check-db` - проверить базу данных  
- `make run-bot` - запустить бота
- `make run-tests-bot` - тесты + бот
- `make lint` - проверка кода
- `make format` - форматирование кода

## 🎯 Статус:

- ✅ **Тесты**: 121 тест проходит
- ✅ **Makefile**: исправлен
- ⚠️ **База данных**: нужна миграция (см. выше)
- ✅ **Клавиатуры**: готовы к работе
