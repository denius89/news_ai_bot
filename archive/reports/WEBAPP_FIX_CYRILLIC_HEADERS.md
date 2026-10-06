# 🔧 Исправление проблемы с кириллицей в HTTP headers

**Дата**: 2025-10-15  
**Проблема**: `TypeError: Failed to execute 'fetch' on 'Window': Failed to read the 'headers' property from 'RequestInit': String contains non ISO-8859-1 code point.`

---

## 🔍 Диагноз

### Причина ошибки

HTTP заголовки должны соответствовать стандарту **ISO-8859-1** (Latin-1 charset), но JavaScript `fetch()` передавал данные Telegram пользователя (имя, фамилия на русском) в заголовке `X-Telegram-User-Data` в виде plain JSON с UTF-8 символами.

**Пример проблемного заголовка:**
```
X-Telegram-User-Data: {"id":0,"first_name":"автор","username":"project-user"}
                                                      ^^^^^^ - кириллица в UTF-8!
```

Браузер блокирует `fetch()` запрос, так как кириллица нарушает стандарт HTTP headers.

### Почему проявлялось не у всех пользователей?

- ✅ **Пользователи с латинскими именами** (Alex, John) → заголовки содержат только ASCII → всё работает
- ❌ **Пользователи с кириллическими именами** (автор, Иван) → заголовки содержат UTF-8 → ошибка

---

## ✅ Решение: Base64-кодирование

### Изменения Frontend (`webapp/src/context/AuthContext.tsx`)

**Функция `serializeTelegramUser`**:

```typescript
const serializeTelegramUser = (tgUser: TelegramUser): string => {
  try {
    // НЕ нормализуем Unicode - сохраняем оригинальные данные
    // Но кодируем в Base64 для безопасной передачи через HTTP headers
    const userJson = JSON.stringify(tgUser);
    
    // Кодируем UTF-8 строку в Base64 для совместимости с HTTP headers (ISO-8859-1)
    // btoa() требует Latin-1, поэтому сначала encodeURIComponent → unescape
    const base64 = btoa(unescape(encodeURIComponent(userJson)));
    
    return base64;
  } catch (e) {
    console.error('Error encoding tgUser to Base64:', e);
    // Fallback: минимальные данные в Base64
    const fallbackJson = JSON.stringify({
      id: tgUser.id,
      first_name: tgUser.first_name || '',
      username: tgUser.username || ''
    });
    return btoa(unescape(encodeURIComponent(fallbackJson)));
  }
};
```

**Что изменилось:**
- ✅ Кодируем `tgUser` в JSON
- ✅ Конвертируем UTF-8 → Base64 через `encodeURIComponent → unescape → btoa`
- ✅ Base64 содержит только ASCII символы → совместимо с HTTP headers

---

### Изменения Backend (`utils/auth/telegram_auth.py`)

#### 1. Функция `verify_telegram_auth` (приоритет 3: Fallback JSON)

```python
# 3. ПРИОРИТЕТ 3: Fallback JSON аутентификация (Base64-кодированный)
user_data_header = request_headers.get("X-Telegram-User-Data")
if user_data_header:
    try:
        import base64
        
        # Декодируем Base64 → UTF-8 JSON
        try:
            user_data_json = base64.b64decode(user_data_header).decode('utf-8')
            user_info = json.loads(user_data_json)
        except (base64.binascii.Error, UnicodeDecodeError) as decode_error:
            # Fallback: возможно это старый формат (plain JSON без Base64)
            logger.debug(f"Base64 decode failed, trying plain JSON: {decode_error}")
            user_info = json.loads(user_data_header)
        
        telegram_id = user_info.get("id")
        if telegram_id:
            # ... аутентификация успешна
```

**Что изменилось:**
- ✅ Декодируем Base64 → UTF-8 JSON
- ✅ Fallback для обратной совместимости (если приходит старый формат без Base64)
- ✅ Парсим JSON и извлекаем `telegram_id`

#### 2. Функция `get_telegram_user_id_from_headers`

```python
# Затем пробуем извлечь из user data (Base64-кодированный)
user_data = request_headers.get("X-Telegram-User-Data")
if user_data:
    try:
        import base64
        
        # Пробуем декодировать Base64
        try:
            user_data_json = base64.b64decode(user_data).decode('utf-8')
            user_info = json.loads(user_data_json)
        except (base64.binascii.Error, UnicodeDecodeError):
            # Fallback: plain JSON без Base64
            user_info = json.loads(user_data)
        
        user_id = user_info.get("id")
        if user_id:
            return int(user_id)
```

#### 3. Функция `validate_telegram_auth_headers`

```python
# Если есть user data, проверяем его формат (Base64-кодированный JSON)
if user_data:
    try:
        import base64
        
        # Пробуем декодировать Base64 → JSON
        try:
            user_data_json = base64.b64decode(user_data).decode('utf-8')
            json.loads(user_data_json)
        except (base64.binascii.Error, UnicodeDecodeError):
            # Fallback: plain JSON без Base64
            json.loads(user_data)
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid user data format: {e}")
        return False
```

---

## 🚀 Как применить исправление

### 1. Пересобрать Frontend

```bash
cd /home/user/news_ai_bot/webapp
npm run build
```

### 2. Перезапустить Flask

```bash
pkill -9 -f "src/webapp.py"
cd /home/user/news_ai_bot
python3 src/webapp.py > logs/webapp.log 2>&1 &
```

### 3. Перезапустить Cloudflare Tunnel

```bash
pkill -9 cloudflared
cd /home/user/news_ai_bot
cloudflared tunnel --url http://localhost:8001 > logs/cloudflare.log 2>&1 &

# Получить новый URL:
sleep 5 && grep "https://" logs/cloudflare.log | grep "trycloudflare.com" | head -1
```

**Новый URL:**
```
https://example.invalid
```

---

## ✅ Результат

- ✅ **Проблема решена**: Кириллица в именах пользователей теперь корректно передаётся в Base64
- ✅ **Обратная совместимость**: Старые клиенты с plain JSON всё ещё работают (fallback)
- ✅ **Безопасность**: Base64 содержит только ASCII символы → совместимость с HTTP headers

---

## 📋 Тестирование

### Тест 1: Пользователь с кириллическим именем

**User ID:** `0`  
**Имя:** "автор"

**Ожидаемый результат:**
- ✅ Fetch запросы успешно отправляются
- ✅ События и новости загружаются
- ✅ Нет ошибки `Failed to execute 'fetch'`

### Тест 2: Пользователь с латинским именем

**Имя:** "Alex"

**Ожидаемый результат:**
- ✅ Всё работает как раньше (Base64 кодирование не мешает)

---

## 🔧 Технические детали

### Кодирование на клиенте

```javascript
// UTF-8 JSON → URL encoding → Latin-1 → Base64
const base64 = btoa(unescape(encodeURIComponent(userJson)));
```

**Почему так сложно?**
- `btoa()` работает только с Latin-1 (ISO-8859-1)
- `encodeURIComponent()` кодирует UTF-8 в URL-safe формат (`%D0%94%D0%B5%D0%BD%D0%B8%D1%81`)
- `unescape()` декодирует URL-safe формат в Latin-1
- `btoa()` кодирует Latin-1 в Base64

### Декодирование на сервере

```python
# Base64 → UTF-8 JSON
user_data_json = base64.b64decode(user_data_header).decode('utf-8')
user_info = json.loads(user_data_json)
```

---

## 🎯 Итог

**Проблема:** HTTP headers не поддерживают кириллицу  
**Решение:** Base64-кодирование `X-Telegram-User-Data`  
**Результат:** Всё работает для всех пользователей независимо от языка имени 🚀

