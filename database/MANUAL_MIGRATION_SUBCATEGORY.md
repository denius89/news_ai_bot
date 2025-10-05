# Ручная миграция: Добавление поля subcategory

## Проблема
Поле `subcategory` отсутствует в таблицах `news` и `events` в Supabase.

## Решение через Supabase Dashboard

### Шаг 1: Откройте Supabase Dashboard
1. Перейдите в [Supabase Dashboard](https://supabase.com/dashboard)
2. Выберите ваш проект
3. Перейдите в раздел **SQL Editor**

### Шаг 2: Выполните SQL команды
Скопируйте и выполните следующие SQL команды:

```sql
-- Добавляем поле subcategory в таблицу news
ALTER TABLE news ADD COLUMN IF NOT EXISTS subcategory TEXT;

-- Добавляем поле subcategory в таблицу events
ALTER TABLE events ADD COLUMN IF NOT EXISTS subcategory TEXT;

-- Добавляем индексы для производительности
CREATE INDEX IF NOT EXISTS idx_news_subcategory ON news (subcategory);
CREATE INDEX IF NOT EXISTS idx_events_subcategory ON events (subcategory);
CREATE INDEX IF NOT EXISTS idx_news_category_subcategory ON news (category, subcategory);
CREATE INDEX IF NOT EXISTS idx_events_category_subcategory ON events (category, subcategory);

-- Обновляем существующие записи
UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'crypto';
UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'economy';
UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'world';
UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'technology';
UPDATE news SET subcategory = 'general' WHERE subcategory IS NULL AND category = 'politics';

UPDATE events SET subcategory = 'general' WHERE subcategory IS NULL;

-- Добавляем комментарии
COMMENT ON COLUMN news.subcategory IS 'Subcategory for hierarchical categorization (e.g., bitcoin, ethereum for crypto)';
COMMENT ON COLUMN events.subcategory IS 'Subcategory for hierarchical categorization (e.g., stocks, bonds for markets)';
```

### Шаг 3: Проверьте результат
После выполнения команд проверьте:

1. В разделе **Table Editor** → **news** должно появиться поле `subcategory`
2. В разделе **Table Editor** → **events** должно появиться поле `subcategory`

### Шаг 4: Тестирование
После миграции запустите тест:

```bash
cd /Users/denisfedko/news_ai_bot
python -c "
from database.db_models import supabase
try:
    result = supabase.table('news').select('*').limit(1).execute()
    if result.data and 'subcategory' in result.data[0]:
        print('✅ Поле subcategory добавлено успешно!')
    else:
        print('❌ Поле subcategory не найдено')
except Exception as e:
    print(f'❌ Ошибка: {e}')
"
```

## Альтернативный способ через Table Editor

### Для таблицы news:
1. Откройте **Table Editor** → **news**
2. Нажмите **Add Column**
3. Настройки:
   - **Name**: `subcategory`
   - **Type**: `text`
   - **Default value**: `'general'`
   - **Allow nullable**: `true`
4. Нажмите **Save**

### Для таблицы events:
1. Откройте **Table Editor** → **events**
2. Нажмите **Add Column**
3. Настройки:
   - **Name**: `subcategory`
   - **Type**: `text`
   - **Default value**: `'general'`
   - **Allow nullable**: `true`
4. Нажмите **Save**

## После миграции

После успешной миграции:

1. Обновите код для использования поля subcategory
2. Перезапустите WebApp
3. Протестируйте функциональность

## Проверка миграции

Запустите этот скрипт для проверки:

```bash
python tools/check_subcategory_migration.py
```
