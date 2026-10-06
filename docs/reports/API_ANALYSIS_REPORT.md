# 🔍 ПОДРОБНЫЙ ОТЧЕТ ПО АНАЛИЗУ API ПРОЕКТА PULSEAI

**Дата проверки:** 13 октября 2025  
**Автор:** PulseAI Senior Engineer

---

## 📊 ТЕКУЩЕЕ СОСТОЯНИЕ БАЗЫ ДАННЫХ

### Новости
- ✅ **Всего новостей:** 2,020
- ✅ **Новостей сегодня:** 282
- ✅ **За последние 7 дней:** 544
- ✅ **Уникальных категорий:** 6 (business, crypto, entertainment, markets, politics, sports)
- ✅ **Активных источников:** 52

### События
- ✅ **Всего событий (events_new):** 3,821
- ⚠️ **События с пустым organizer:** 1,000 из 3,821 (26.2%)
- ⚠️ **События с пустым location:** 525 из 3,821 (13.7%)
- ✅ **Все события имеют description** (0% пустых)
- ✅ **Все события имеют category** (0% пустых)
- ℹ️ **Старая таблица events:** 342 события (устаревшая)

---

## ❌ ОБНАРУЖЕННЫЕ ПРОБЛЕМЫ

### 1. 🚨 КРИТИЧЕСКАЯ: Новости загружаются только 3 штуки

**Проблема:**
На фронтенде отображаются только 3 fallback новости вместо реальных данных из базы.

**Причина:**
В `/webapp/src/pages/NewsPage.tsx` (строки 116-158) используются fallback данные при ошибке API запроса:

```typescript
catch (error) {
  console.error('❌ Error fetching news:', error);
  
  // Fallback to mock data if API fails
  const fallbackNews: NewsItem[] = [
    // Только 3 захардкоженные новости
    { id: '1', title: 'Bitcoin достигает...' },
    { id: '2', title: 'ИИ-революция...' },
    { id: '3', title: 'Чемпионат мира...' },
  ];
  
  setNews(fallbackNews);
  setHasMoreNews(false);
}
```

**Возможные причины сбоя API:**
1. URL `/api/latest` не совпадает с базовым URL (должен быть `/api/news/latest`)
2. CORS ошибки
3. Проблемы с аутентификацией
4. API возвращает ошибку 500

**Подтверждение:**
- В логах консоли должны быть ошибки `❌ Error fetching news:`
- API endpoint работает корректно (возвращает 10 новостей при прямом запросе)

---

### 2. ⚠️ СРЕДНЕЙ ВАЖНОСТИ: Странные показатели статистики на главной

**Проблема:**
Статистика показывает необычные значения:
- Новостей сегодня: 281 **(изменение: +128%)**
- Активных источников: 52 **(изменение: -46)**
- AI дайджестов: 44 **(изменение: +44)**

**Причина:**
Некорректная логика расчета изменений в `/routes/dashboard_api.py`:

1. **Новости сегодня (строки 28-94):**
   - Если сегодня нет новостей, берется неделя
   - Процент считается относительно предыдущей недели
   - Это дает неадекватные значения вроде +128%

2. **Активные источники (строки 97-138):**
   - Изменение считается как абсолютная разница (не процент)
   - Показывает `-46` вместо процента

3. **AI дайджесты (строки 164-198):**
   - Сравнивает недельные данные с предыдущей неделей
   - Изменение +44 означает 44 новых дайджеста, а не процент

**Решение:**
Унифицировать расчет изменений во всех функциях (использовать проценты).

---

### 3. ⚠️ СРЕДНЕЙ ВАЖНОСТИ: События с пустыми полями organizer и location

**Проблема:**
- 26.2% событий (1,000 из 3,821) имеют `organizer: None`
- 13.7% событий (525 из 3,821) имеют `location: None`

**Примеры:**
```python
{
  "title": "Bitcoin Halving Event",
  "category": "crypto",
  "subcategory": "bitcoin",
  "description": "Bitcoin network halving event...",
  "location": "Global",
  "organizer": None,  # ❌ Проблема
}
```

**Причина:**
1. Провайдеры событий не всегда предоставляют эти поля
2. Некоторые события (например, крипто-события) не имеют организатора
3. Frontend отображает `None` как текст вместо fallback значения

**Влияние:**
На фронтенде в EventsPage.tsx пользователь видит "None" вместо красивого отсутствия поля или дефолтного значения.

**Решение:**
1. В провайдерах использовать fallback значения (например, "N/A", "Global", "Community")
2. На фронтенде обрабатывать `null`/`None` и не показывать поле или показывать красиво

---

### 4. ℹ️ НИЗКОЙ ВАЖНОСТИ: Дублирование событий в двух таблицах

**Проблема:**
- Новая таблица `events_new`: 3,821 событие
- Старая таблица `events`: 342 события

**Причина:**
В процессе разработки была создана новая таблица events_new, но старая events не удалена.

**Решение:**
1. Убедиться, что все провайдеры пишут в `events_new`
2. Удалить старую таблицу `events` после миграции
3. Переименовать `events_new` → `events`

---

## ✅ ПРЕДЛОЖЕНИЯ ПО РЕШЕНИЮ

### 🔧 Приоритет 1: Исправить загрузку новостей (КРИТИЧНО)

**Решение A: Исправить URL API**

В `webapp/src/pages/NewsPage.tsx` строка 76:
```typescript
// Было:
const response = await fetch(`/api/latest?page=${page}&limit=20`);

// Должно быть:
const response = await fetch(`/api/news/latest?page=${page}&limit=20`);
```

**Решение B: Добавить debug логирование**

Добавить логи для диагностики:
```typescript
console.log('📡 Full URL:', `${window.location.origin}/api/latest?page=${page}&limit=20`);
console.log('📡 Response:', await response.text());
```

**Решение C: Убрать fallback или сделать его более информативным**

```typescript
catch (error) {
  console.error('❌ Error fetching news:', error);
  
  // Показываем пользователю реальную ошибку
  setNews([]);
  setError('Не удалось загрузить новости. Проверьте подключение к интернету.');
}
```

---

### 🔧 Приоритет 2: Исправить статистику на главной

**Файл:** `routes/dashboard_api.py`

**Решение:**

```python
def get_news_stats_today() -> Dict:
    """Получает статистику новостей за сегодня."""
    # ... existing code ...
    
    # Унифицированный расчет процента изменения
    if yesterday_count > 0:
        change_percent = round(((today_count - yesterday_count) / yesterday_count) * 100)
    else:
        change_percent = 100 if today_count > 0 else 0
    
    return {"count": today_count, "change": change_percent}

def get_active_sources_stats() -> Dict:
    """Получает статистику активных источников."""
    # ... existing code ...
    
    # Изменение в процентах, а не абсолютное
    if prev_sources > 0:
        change_percent = round(((active_sources - prev_sources) / prev_sources) * 100)
    else:
        change_percent = 100 if active_sources > 0 else 0
    
    return {"count": active_sources, "change": change_percent}
```

---

### 🔧 Приоритет 3: Исправить пустые поля в событиях

**Вариант A: Исправить в провайдерах (рекомендуется)**

В `events/providers/*.py`:
```python
event_data = {
    "title": event.get("title"),
    "category": event.get("category"),
    "subcategory": event.get("subcategory"),
    "description": event.get("description", "No description available"),
    "location": event.get("location") or "Global",  # Fallback
    "organizer": event.get("organizer") or "Community",  # Fallback
    # ...
}
```

**Вариант B: Исправить на фронтенде**

В `webapp/src/pages/EventsPage.tsx`:
```typescript
{event.location && event.location !== 'None' && (
  <p className="text-xs text-[var(--color-text)]-secondary mt-1">
    📍 {event.location}
  </p>
)}

{event.organizer && event.organizer !== 'None' && (
  <p className="text-xs text-[var(--color-text)]-secondary mt-1">
    👤 {event.organizer}
  </p>
)}
```

**Вариант C: Миграция данных в БД (одноразово)**

```sql
UPDATE events_new 
SET organizer = 'Community' 
WHERE organizer IS NULL OR organizer = 'None';

UPDATE events_new 
SET location = 'Global' 
WHERE location IS NULL OR location = 'None';
```

---

### 🔧 Приоритет 4: Удалить старые события

**Вариант A: Удалить таблицу events (после миграции)**

```sql
-- Проверить, что events_new используется
SELECT COUNT(*) FROM events_new;  -- Должно быть > 0

-- Удалить старую таблицу
DROP TABLE IF EXISTS events;

-- Опционально: переименовать events_new -> events
ALTER TABLE events_new RENAME TO events;
```

**Вариант B: Удалить только события с пустыми полями**

```sql
-- Удалить события из events_new с критически пустыми полями
DELETE FROM events_new 
WHERE (description IS NULL OR description = '') 
  AND (title IS NULL OR title = '');
```

---

## 📋 ПЛАН ДЕЙСТВИЙ (РЕКОМЕНДУЕМЫЙ ПОРЯДОК)

### Шаг 1: Срочно исправить загрузку новостей (30 минут)
1. ✅ Проверить правильный URL API endpoint
2. ✅ Добавить debug логирование
3. ✅ Исправить обработку ошибок
4. ✅ Протестировать загрузку новостей

### Шаг 2: Исправить статистику (20 минут)
1. ✅ Унифицировать расчет изменений в `dashboard_api.py`
2. ✅ Проверить корректность всех метрик
3. ✅ Протестировать дашборд

### Шаг 3: Исправить отображение событий (30 минут)
1. ✅ Добавить fallback значения в провайдеры
2. ✅ Обновить EventsPage.tsx для корректного отображения
3. ✅ (Опционально) Мигрировать данные в БД

### Шаг 4: Очистить старые данные (10 минут)
1. ✅ Убедиться, что `events_new` используется
2. ✅ Удалить или переименовать таблицу `events`

**Общее время:** ~1.5 часа

---

## 🎯 ОЖИДАЕМЫЕ РЕЗУЛЬТАТЫ

После выполнения всех исправлений:

1. ✅ **Новости:** Корректная загрузка всех 282+ новостей с пагинацией
2. ✅ **Статистика:** Понятные и корректные проценты изменений
3. ✅ **События:** Все поля заполнены или красиво отсутствуют
4. ✅ **База данных:** Только актуальные события в одной таблице

---

## 📝 ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ

### Мониторинг
1. Добавить логирование ошибок API
2. Настроить алерты при падении новостей < 100/день
3. Мониторить rate limits провайдеров событий

### Тестирование
1. Написать unit-тесты для `dashboard_api.py`
2. Добавить E2E тесты для загрузки новостей
3. Проверить работу на мобильных устройствах

### Документация
1. Обновить API документацию
2. Задокументировать логику fallback значений
3. Создать руководство по добавлению новых провайдеров

---

**Подготовлено:** PulseAI Engineering Team  
**Контакт:** contact@example.invalid

