# PulseAI Security Policy

## Обзор безопасности

PulseAI реализует многоуровневую систему безопасности для защиты пользовательских данных и обеспечения надёжной аутентификации через Telegram WebApp.

## Аутентификация Telegram WebApp

### Принцип работы

1. **HMAC SHA256 проверка**: Все данные от Telegram WebApp проверяются через HMAC SHA256 подпись
2. **Временные ограничения**: Данные аутентификации действительны не более 24 часов
3. **Fallback совместимость**: Поддержка старого метода аутентификации для плавной миграции

### Алгоритм проверки

```python
# 1. Парсинг initData
parsed_data = dict(parse_qsl(init_data))

# 2. Извлечение hash
hash_value = parsed_data.pop('hash')

# 3. Проверка времени (не старше 24 часов)
auth_date = int(parsed_data.get('auth_date', 0))
if current_time - auth_date > 86400:
    return None

# 4. Создание data_check_string
data_check_arr = [f"{k}={v}" for k, v in sorted(parsed_data.items())]
data_check_string = '\n'.join(data_check_arr)

# 5. Вычисление HMAC SHA256
secret_key = hashlib.sha256(bot_token.encode()).digest()
calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

# 6. Безопасное сравнение
if not hmac.compare_digest(calculated_hash, hash_value):
    return None
```

### Защита от атак

- **Timing attacks**: Использование `hmac.compare_digest()` для постоянного времени сравнения
- **Hash collisions**: HMAC SHA256 обеспечивает криптографическую стойкость
- **Data tampering**: Любое изменение данных приводит к неверному hash

## Нормализация имён пользователей

### Проблемы безопасности

1. **Emoji-only имена**: `🔥🔥🔥` → `User #<user_id>`
2. **Невидимые символы**: `John\u200bDoe` → `JohnDoe`
3. **Стилизованные Unicode**: `𝕀𝕧𝕒𝕟` → `Ivan`
4. **Испорченная кодировка**: `ÐÐ°Ð½` → `Иван`
5. **RTL текст**: Сохраняется как есть
6. **Китайские/японские символы**: Сохраняются как есть

### Алгоритм нормализации

```python
def normalize_user_name(raw_name, username, user_id):
    # 1. Проверка наличия имени
    if not raw_name or not raw_name.strip():
        return _get_fallback_name(username, user_id)
    
    # 2. Исправление испорченной кодировки
    processed_name = _fix_corrupted_encoding(raw_name)
    
    # 3. Удаление невидимых символов
    cleaned_name = _remove_invisible_chars(processed_name)
    
    # 4. Конвертация стилизованных Unicode
    normalized_name = _convert_styled_unicode(cleaned_name)
    
    # 5. Проверка на emoji-only
    if _is_emoji_only(normalized_name):
        return _get_fallback_name(username, user_id)
    
    # 6. Обрезка до 64 символов
    final_name = _truncate_preserving_words(normalized_name, 64)
    
    return final_name.strip()
```

## Сессии и куки

### Настройки безопасности

```python
app.config.update(
    SECRET_KEY=os.getenv('FLASK_SECRET_KEY'),
    SESSION_COOKIE_HTTPONLY=True,      # Защита от XSS
    SESSION_COOKIE_SECURE=True,        # Только HTTPS
    SESSION_COOKIE_SAMESITE='Lax',     # Защита от CSRF
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24)
)
```

### Middleware защита

```python
@app.before_request
def validate_session():
    if request.path.startswith('/api/'):
        if 'user_id' not in session and request.endpoint != 'api.get_user_by_telegram_id':
            return jsonify({"status": "error", "message": "Unauthorized"}), 401
```

## CORS политика

### Разрешённые домены

```python
CORS(app, origins=[
    "https://*.trycloudflare.com",     # Cloudflare туннели
    "https://telegram.org",            # Telegram домены
    "https://web.telegram.org",
    "https://t.me"
])
```

## Логирование безопасности

### Мониторинг аутентификации

```python
def log_auth_attempt(telegram_id, success, method, error=None):
    if success:
        logger.info(f"Telegram auth success: user_id={telegram_id}, method={method}")
    else:
        logger.warning(f"Telegram auth failed: user_id={telegram_id}, method={method}, error={error}")
```

### Типы событий

- **Успешная аутентификация**: `initData`, `userData`, `fallback`
- **Неудачная аутентификация**: Неверный hash, истёкший auth_date, отсутствующие поля
- **Подозрительная активность**: Множественные неудачные попытки

## База данных

### Защита от SQL инъекций

- Использование Supabase ORM с параметризованными запросами
- Валидация всех входных данных
- Ограничение прав доступа к базе данных

### Шифрование данных

- Чувствительные данные не хранятся в открытом виде
- Telegram user ID используется как основной идентификатор
- Персональные данные минимизированы

## Рекомендации по развёртыванию

### Переменные окружения

```bash
# Обязательные для production
TELEGRAM_BOT_TOKEN=your_bot_token
FLASK_SECRET_KEY=your_secret_key_32_chars_min
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Опциональные
DEBUG=false
WEBAPP_HOST=127.0.0.1
```

### HTTPS обязателен

- Все production развёртывания должны использовать HTTPS
- `SESSION_COOKIE_SECURE=True` только для HTTPS
- Cloudflare туннели автоматически обеспечивают HTTPS

### Мониторинг

- Регулярная проверка логов аутентификации
- Мониторинг неудачных попыток входа
- Алерты при подозрительной активности

## Миграция безопасности

### План миграции

1. **Фаза 1**: Добавление новой системы аутентификации (текущая)
2. **Фаза 2**: Логирование использования старого метода
3. **Фаза 3**: Полный переход на новый метод (через 2 недели)
4. **Фаза 4**: Удаление legacy кода

### Обратная совместимость

- Существующие пользователи продолжают работать
- Старые сессии сохраняются
- Плавный переход без потери данных

## Контакты безопасности

При обнаружении уязвимостей безопасности:

1. Не создавайте публичные issue
2. Свяжитесь с командой разработки напрямую
3. Предоставьте детальное описание проблемы
4. Дождитесь подтверждения получения

## Обновления политики

Эта политика безопасности обновляется по мере развития системы. Последнее обновление: 2025-01-06.

---

**Важно**: Безопасность - это непрерывный процесс. Регулярно обновляйте зависимости, мониторьте логи и следите за новыми угрозами.
