# 🚦 Rate Limiting Status

**Дата:** 27 октября 2025
**Статус:** Частично реализован
**Проблема:** Циклический импорт

---

## ✅ Что Сделано

1. **Flask-Limiter установлен** ✅
   ```bash
   pip install flask-limiter
   ```

2. **Инициализация в `src/webapp.py`** ✅
   ```python
   limiter = Limiter(
       app=app,
       key_func=get_remote_address,
       default_limits=["200 per day", "50 per hour"],
       storage_uri=os.getenv("REDIS_URL", "memory://"),
       strategy="fixed-window",
       headers_enabled=True,
   )
   ```

3. **Admin API endpoints созданы** ✅
   - `GET /admin/api/rate-limit/config`
   - `GET /admin/api/rate-limit/stats`

---

## ⚠️ Известная Проблема

**Циклический импорт** при попытке использовать `limiter` в `routes/api_routes.py`:

```python
from src.webapp import limiter  # ❌ Causes 502 error
```

**Решение:** Декораторы будут применяться динамически или через middleware.

---

## 🔧 Варианты Решения

### **Вариант 1: Позднее применение декораторов**

Создать helper функцию:

```python
# utils/rate_limit.py
def apply_rate_limit(limit_str):
    """Применить rate limit к функции."""
    from flask import current_app

    def decorator(f):
        limiter = current_app.extensions.get('limiter')
        if limiter:
            return limiter.limit(limit_str)(f)
        return f
    return decorator
```

Использование:
```python
@api_bp.route("/digests/generate", methods=["POST"])
@apply_rate_limit("10 per hour")
def generate_digest():
    ...
```

### **Вариант 2: Middleware Approach**

Использовать `@before_request`:

```python
@app.before_request
def rate_limit_before_request():
    if request.endpoint == 'api_routes.generate_digest':
        limiter = current_app.extensions.get('limiter')
        if limiter:
            limiter.check(target=get_current_function_name())
```

### **Вариант 3: Глобальные лимиты**

Функционирует без изменений:
- Default limits: `200 per day, 50 per hour`
- Applied globally to all endpoints

---

## 📊 Текущий Статус

| Компонент | Статус | Комментарий |
|-----------|--------|-------------|
| Flask-Limiter | ✅ Установлен | 4.0.0 |
| Инициализация | ✅ Работает | В `src/webapp.py` |
| Глобальные лимиты | ✅ Работают | 200/day, 50/hour |
| Per-endpoint лимиты | ⚠️ Частично | Нужно обойти циклический импорт |
| Admin API | ✅ Работает | Полностью функционален |
| Redis интеграция | ✅ Готова | Через `REDIS_URL` |

---

## 🎯 Рекомендации

### **Для продакшена:**

1. **Использовать глобальные лимиты** (уже работают) ✅
2. **Добавить Redis** для multi-instance:
   ```bash
   REDIS_URL=redis://localhost:6379/0
   ```
3. **Применить per-endpoint лимиты** после решения циклического импорта

### **Временное Решение:**

Глобальные лимиты (200/day, 50/hour) уже защищают систему.
Per-endpoint лимиты можно добавить позже через middleware.

---

## 📝 TODO

- [ ] Создать helper функцию `apply_rate_limit()`
- [ ] Применить к критичным endpoints:
  - `/api/digests/generate` → `10 per hour`
  - `/api/news/latest` → `100 per hour`
  - `/api/digests/history` → `50 per hour`
- [ ] Добавить Redis в production
- [ ] Тестирование под нагрузкой

---

**Приоритет:** Средний
**Блокирует запуск:** Нет
**Глобальные лимиты работают** ✅
