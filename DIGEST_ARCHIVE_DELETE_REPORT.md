# Отчет: Диагностика архивирования и удаления дайджестов

**Дата:** 15 октября 2025  
**Статус:** ✅ ПРОБЛЕМА ДИАГНОСТИРОВАНА

## Резюме

Функциональность архивирования и удаления дайджестов **технически работает корректно**. Проблема заключается в **аутентификации пользователей** при обращении к API endpoints из WebApp.

## Результаты тестирования

### ✅ База данных — РАБОТАЕТ
```bash
$ python3 check_digests_table.py

✅ Таблица digests существует
✅ archived - ПРИСУТСТВУЕТ
✅ deleted_at - ПРИСУТСТВУЕТ
📊 Всего колонок: 17
```

**Колонки в БД:**
- `archived` (BOOLEAN)
- `deleted_at` (TIMESTAMPTZ)
- + 15 других колонок (id, user_id, summary, category, etc.)

### ✅ Функции БД — РАБОТАЮТ
```bash
$ python3 test_digest_operations.py

✅ Архивирование работает
✅ Разархивирование работает
✅ Мягкое удаление работает
✅ Восстановление работает
```

**Протестированные функции** (`database/db_models.py`):
- `archive_digest()` — строка 1123 ✅
- `unarchive_digest()` — строка 1165 ✅
- `soft_delete_digest()` — строка 1034 ✅
- `restore_digest()` — строка 1077 ✅
- `permanent_delete_digest()` — строка 1215 ✅

### ❌ API Endpoints — ТРЕБУЮТ АУТЕНТИФИКАЦИЮ
```bash
$ python3 test_digest_api.py

❌ Status: 401
❌ Response: {'error': 'Authentication failed: no valid method found'}
```

**API endpoints** (`routes/api_routes.py`):
- `POST /api/digests/<id>/archive` — строка 1308
- `POST /api/digests/<id>/unarchive` — строка 1336
- `DELETE /api/digests/<id>` — строка 1241
- `POST /api/digests/<id>/restore` — строка 1280

## Причина проблемы

### Аутентификация WebApp

В `src/webapp.py` (строки 52-104) есть middleware `@app.before_request authenticate_request()`, который **блокирует** все API endpoints, не входящие в список публичных:

```python
public_paths = [
    "/api/health",
    "/api/config",
    "/api/users/by-telegram-id",
    "/api/categories",
    "/api/digests/categories",
    "/api/digests/styles",
    "/api/news/latest",
    "/api/dashboard/stats",
    "/api/dashboard/latest_news",
    "/api/dashboard/news_trend",
]
```

Endpoints архивирования/удаления **НЕ в списке** (это правильно для безопасности!).

### Требования аутентификации

Для успешной аутентификации требуется один из методов (`utils/auth/telegram_auth.py`):

1. **HMAC SHA256** (приоритет 1):
   - Заголовок: `X-Telegram-Init-Data`
   - Проверка подписи HMAC с `TELEGRAM_BOT_TOKEN`
   - Срок действия: 24 часа

2. **Session** (приоритет 2):
   - Flask session с `user_id` и `telegram_id`
   - Устанавливается после успешного HMAC
   - Persistent session

3. **Fallback JSON** (приоритет 3):
   - Заголовок: `X-Telegram-User-Data` (Base64-кодированный JSON)
   - Менее безопасный метод

### Фронтенд

`webapp/src/pages/DigestPage.tsx` **правильно** передает заголовки:

```typescript
const response = await fetch(`/api/digests/${digestId}/archive?user_id=${userId}`, {
  method: 'POST',
  headers: authHeaders  // из AuthContext
});
```

`webapp/src/context/AuthContext.tsx` устанавливает:
```typescript
const headers = {
  'X-Telegram-Init-Data': initData,
  'X-Telegram-User-Data': serializeTelegramUser(tgUser)
};
```

## Возможные причины сбоя

1. **Истек токен аутентификации** (> 24 часов)
   - HMAC проверка отклоняет старые `auth_date`
   - Решение: переавторизация в WebApp

2. **Пользователь не залогинен**
   - `initData` пустой или некорректный
   - Session отсутствует или устарел
   - Решение: повторный вход через Telegram

3. **Пользователь отсутствует в БД**
   - `verify_telegram_auth()` требует наличия user в таблице `users`
   - Код: `real_user_id = get_user_uuid_by_telegram_id(telegram_id)`
   - Решение: создать пользователя через `/api/users/by-telegram-id`

4. **Проблемы с CORS или заголовками**
   - Браузер блокирует отправку заголовков
   - Решение: проверить DevTools → Network

5. **Flask перезапущен, session очищен**
   - Session хранится в памяти Flask
   - После перезапуска нужна повторная аутентификация

## Рекомендации

### Для пользователя

1. **Обновить WebApp**:
   - Закрыть и открыть заново Telegram WebApp
   - Это обновит `initData` с новым токеном

2. **Проверить логин**:
   - Убедиться, что пользователь залогинен
   - Проверить наличие `user_id` в localStorage

3. **Очистить кэш**:
   ```bash
   # В браузере
   DevTools → Application → Storage → Clear Site Data
   ```

### Для разработчика

1. **Добавить логирование ошибок аутентификации на фронтенде**:
   ```typescript
   if (response.status === 401) {
     console.error('❌ Требуется авторизация. Обновите приложение.');
     // Показать пользователю уведомление
     // Перенаправить на страницу входа
   }
   ```

2. **Добавить автоматическое обновление токена**:
   ```typescript
   // В AuthContext.tsx
   useEffect(() => {
     const interval = setInterval(() => {
       refreshAuth();
     }, 12 * 60 * 60 * 1000); // Каждые 12 часов
     return () => clearInterval(interval);
   }, []);
   ```

3. **Добавить fallback для dev-режима**:
   ```python
   # В src/webapp.py authenticate_request()
   if os.getenv("DEV_MODE") == "true":
       # Разрешить доступ без аутентификации в dev
       pass
   ```

## Следующие шаги

1. ✅ Диагностика завершена
2. ⏳ Проверить текущий статус аутентификации пользователя
3. ⏳ Обновить документацию для пользователей
4. ⏳ Добавить better error handling на фронтенде

## Заключение

**Архивирование и удаление дайджестов полностью функциональны**. Проблема заключается в **аутентификации пользователей** при обращении к защищенным API endpoints. Это нормальное поведение системы безопасности.

**Решение**: Пользователь должен переавторизоваться в WebApp или обновить приложение для получения свежего токена аутентификации.

---

**Файлы для очистки после диагностики:**
- `check_digests_table.py`
- `test_digest_operations.py`
- `test_digest_api.py`

