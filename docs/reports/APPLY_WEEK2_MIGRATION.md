# 🚀 Применение Week 2 Migration - Пошаговая инструкция

**Файл миграции:** `database/migrations/2025_01_18_performance_rpc_functions.sql`  
**Время:** ~5 минут  
**Риск:** Минимальный (только создание READ-ONLY функций)

---

## 📋 Checklist перед применением

- [x] Файл миграции создан
- [x] Код обновлен (routes/news_routes.py, routes/dashboard_api.py)
- [ ] Backup БД создан (опционально, для безопасности)
- [ ] Доступ к Supabase Dashboard

---

## 🎯 Способ 1: Через Supabase Dashboard (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Открыть Supabase Dashboard
1. Перейти: https://supabase.com/dashboard
2. Выбрать проект PulseAI
3. В левом меню: **SQL Editor**

### Шаг 2: Скопировать миграцию
```bash
# Открыть файл миграции
cat database/migrations/2025_01_18_performance_rpc_functions.sql
```

Или просто открыть файл в Cursor (уже открыт!) и скопировать весь текст (Cmd+A, Cmd+C)

### Шаг 3: Выполнить в SQL Editor
1. В Supabase SQL Editor: **New Query**
2. Вставить скопированный SQL (Cmd+V)
3. Нажать **Run** (или Cmd+Enter)

### Шаг 4: Проверить результат
В выводе должно быть:
```
✅ RPC функции успешно созданы:
  - get_news_by_categories_batch()
  - get_all_category_stats()
  - count_sources_in_period()
  - count_unique_categories()
  - get_provider_stats()
  - get_news_stats_period()

📊 Ожидаемый эффект:
  - ↓ 80-90% количество DB queries
  - ↓ 90-95% объем загружаемых данных
  - ↑ 5-10x скорость endpoints
```

---

## 🎯 Способ 2: Через psql (альтернатива)

### Если у вас есть прямой доступ к БД:

```bash
# Получить credentials из .env
source .env
echo $SUPABASE_URL
echo $SUPABASE_KEY

# Применить миграцию
psql -h YOUR_SUPABASE_HOST \
     -U postgres \
     -d postgres \
     -f database/migrations/2025_01_18_performance_rpc_functions.sql
```

**Примечание:** Supabase обычно использует Dashboard, psql доступ может быть ограничен.

---

## ✅ Проверка что функции созданы

### В Supabase SQL Editor выполнить:

```sql
-- 1. Проверить что все функции существуют
SELECT 
  proname as function_name,
  pg_get_function_result(oid) as return_type
FROM pg_proc 
WHERE proname LIKE 'get_%' OR proname LIKE 'count_%'
ORDER BY proname;

-- Должно вывести:
-- get_news_by_categories_batch | TABLE(...)
-- get_all_category_stats | TABLE(...)
-- count_sources_in_period | bigint
-- count_unique_categories | bigint
-- get_provider_stats | TABLE(...)
-- get_news_stats_period | TABLE(...)
```

### Проверить работу функций:

```sql
-- 2. Тест get_all_category_stats
SELECT * FROM get_all_category_stats();
-- Должно вернуть таблицу с категориями и статистикой

-- 3. Тест count_unique_categories
SELECT count_unique_categories();
-- Должно вернуть число (например: 8)

-- 4. Тест count_sources_in_period
SELECT count_sources_in_period(
  NOW() - INTERVAL '7 days',
  NOW()
);
-- Должно вернуть число источников за последнюю неделю

-- 5. Тест get_news_by_categories_batch
SELECT category, COUNT(*) as news_count
FROM get_news_by_categories_batch(
  ARRAY['tech', 'crypto', 'world'], 
  10
)
GROUP BY category;
-- Должно вернуть до 10 новостей на категорию
```

---

## 🔄 Перезапуск приложения

После применения миграции:

```bash
# 1. Остановить сервисы
./stop_services.sh

# 2. Запустить сервисы
./start_services.sh

# 3. Проверить логи
tail -f logs/app.log

# Искать в логах:
# ✅ Batch загрузка: X новостей из Y категорий
# ✅ Статистика получена через RPC: X категорий
# ✅ RPC подсчет источников: current=X, prev=Y
```

---

## 🧪 Тестирование endpoints

```bash
# 1. Тест weighted distribution
curl -s "http://localhost:5000/api/latest-weighted?limit=20" | jq '.status'
# Ожидается: "success"
# В логах: "✅ Batch загрузка: ..."

# 2. Тест distribution stats
curl -s "http://localhost:5000/api/distribution-stats" | jq '.status'
# Ожидается: "success"
# В логах: "✅ Статистика получена через RPC: ..."

# 3. Тест с force fallback (для проверки fallback механизма)
# Временно переименовать RPC функцию в Supabase:
# ALTER FUNCTION get_all_category_stats RENAME TO get_all_category_stats_backup;
# Проверить что endpoint все еще работает (через fallback)
# Вернуть имя обратно
```

---

## 📊 Измерение улучшений

### До миграции:
```bash
# Засечь время
time curl -s "http://localhost:5000/api/distribution-stats" > /dev/null
# Результат: ~2-3 секунды
```

### После миграции:
```bash
# Засечь время еще раз
time curl -s "http://localhost:5000/api/distribution-stats" > /dev/null
# Результат: ~0.05-0.2 секунды (↑ 10-20x быстрее!)
```

---

## 🐛 Troubleshooting

### Проблема: "function does not exist"

**В логах:**
```
Ошибка RPC get_all_category_stats: function get_all_category_stats() does not exist
```

**Решение:**
1. Проверить что SQL миграция выполнена успешно
2. В Supabase SQL Editor: `SELECT proname FROM pg_proc WHERE proname = 'get_all_category_stats';`
3. Если пусто - миграция не применена, выполнить заново

---

### Проблема: Код работает через fallback

**В логах:**
```
Ошибка batch загрузки новостей: ..., fallback на старый способ
```

**Это нормально если:**
- RPC функции еще не применены
- Есть опечатка в имени функции
- Проблемы с правами доступа

**Код продолжит работать, но медленнее.**

**Решение:**
1. Проверить что RPC функции созданы (см. выше)
2. Перезапустить приложение
3. Проверить логи на детали ошибки

---

### Проблема: Разные результаты

**Симптом:**
RPC возвращает другое количество записей чем fallback

**Объяснение:**
Это нормально! RPC использует точный COUNT вместо limit=1000.

**Пример:**
- Fallback: загружает 1000 записей, считает уникальные → результат ≤1000
- RPC: COUNT(DISTINCT) по всей таблице → результат = реальное количество

RPC данные **более точные**.

---

## ⏪ Откат (если нужно)

### Удалить RPC функции:
```sql
DROP FUNCTION IF EXISTS get_news_by_categories_batch(TEXT[], INT);
DROP FUNCTION IF EXISTS get_all_category_stats();
DROP FUNCTION IF EXISTS count_sources_in_period(TIMESTAMPTZ, TIMESTAMPTZ);
DROP FUNCTION IF EXISTS count_unique_categories();
DROP FUNCTION IF EXISTS get_provider_stats();
DROP FUNCTION IF EXISTS get_news_stats_period(TIMESTAMPTZ, TIMESTAMPTZ);
```

Код автоматически переключится на fallback.

---

## ✅ Checklist после применения

- [ ] SQL миграция выполнена в Supabase
- [ ] Все 6 функций созданы (проверено SELECT)
- [ ] Функции протестированы (SELECT * FROM ...)
- [ ] Приложение перезапущено
- [ ] Логи проверены (есть "✅ Batch", "✅ RPC")
- [ ] Endpoints протестированы (curl)
- [ ] Время ответа улучшено (измерено с time)

---

## 🎉 Успех!

Если все пункты выполнены:
- ✅ RPC функции работают
- ✅ Логи показывают "✅ Batch загрузка" и "✅ RPC подсчет"
- ✅ Endpoints отвечают быстрее
- ✅ Fallback не срабатывает

**Поздравляю! Week 2 оптимизация применена успешно! 🚀**

---

**Следующий шаг:** Мониторинг производительности в production
- Смотреть логи: `logs/app.log`
- Замерять latency endpoints
- Проверять нагрузку на БД в Supabase Dashboard

---

**Дата:** 2025-01-18  
**Статус:** Готово к применению  
**Время применения:** ~5 минут


