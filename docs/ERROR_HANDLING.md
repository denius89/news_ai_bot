# Стандартизированная система обработки ошибок

## Обзор

PulseAI использует стандартизированную систему обработки ошибок, которая обеспечивает консистентное логирование, категоризацию и обработку ошибок по всему проекту.

## Основные компоненты

### 1. Базовый класс PulseAIError

Все ошибки в проекте наследуются от `PulseAIError`:

```python
from utils.error_handler import PulseAIError, ErrorCategory, ErrorSeverity

# Базовая ошибка
error = PulseAIError(
    message="Something went wrong",
    category=ErrorCategory.DATABASE,
    severity=ErrorSeverity.HIGH,
    details={"operation": "insert", "table": "users"},
    cause=original_exception
)
```

### 2. Специализированные классы ошибок

#### DatabaseError
```python
from utils.error_handler import DatabaseError

try:
    # Database operation
    result = supabase.table("users").insert(data).execute()
except Exception as e:
    raise DatabaseError(
        message="Failed to insert user",
        operation="insert",
        table="users",
        cause=e
    )
```

#### NetworkError
```python
from utils.error_handler import NetworkError

try:
    response = requests.get(url, timeout=30)
except Exception as e:
    raise NetworkError(
        message="Request failed",
        url=url,
        status_code=getattr(e, 'response', {}).get('status_code'),
        timeout=30,
        cause=e
    )
```

#### AIServiceError
```python
from utils.error_handler import AIServiceError

try:
    result = openai_client.chat.completions.create(...)
except Exception as e:
    raise AIServiceError(
        message="AI service unavailable",
        model="gpt-4",
        prompt_length=len(prompt),
        cause=e
    )
```

#### TelegramError
```python
from utils.error_handler import TelegramError

try:
    await bot.send_message(chat_id, text)
except Exception as e:
    raise TelegramError(
        message="Failed to send message",
        chat_id=chat_id,
        user_id=user_id,
        retry_after=getattr(e, 'retry_after', None),
        cause=e
    )
```

#### ParsingError
```python
from utils.error_handler import ParsingError

try:
    feed = feedparser.parse(url)
except Exception as e:
    raise ParsingError(
        message="Failed to parse RSS feed",
        source="example.com",
        url=url,
        content_type=response.headers.get('content-type'),
        cause=e
    )
```

#### ValidationError
```python
from utils.error_handler import ValidationError

def validate_email(email):
    if not email or '@' not in email:
        raise ValidationError(
            message="Invalid email format",
            field="email",
            value=email,
            expected_type=str
        )
```

#### ConfigurationError
```python
from utils.error_handler import ConfigurationError

try:
    config = load_config_file("config.yaml")
except Exception as e:
    raise ConfigurationError(
        message="Failed to load configuration",
        config_file="config.yaml",
        config_key="database_url",
        cause=e
    )
```

## Декораторы для обработки ошибок

### retry_on_error
Автоматические повторные попытки с экспоненциальной задержкой:

```python
from utils.error_handler import retry_on_error

@retry_on_error(max_attempts=3, delay=1.0, backoff_factor=2.0)
def flaky_function():
    # Function that might fail
    pass

@retry_on_error(max_attempts=5, delay=0.5, exceptions=(NetworkError,))
async def async_network_function():
    # Async function with specific exception handling
    pass
```

### handle_database_error
Стандартная обработка ошибок базы данных:

```python
from utils.error_handler import handle_database_error

@handle_database_error("user creation")
def create_user(user_data):
    return supabase.table("users").insert(user_data).execute()

@handle_database_error("async user lookup")
async def async_get_user(user_id):
    return await async_supabase.table("users").select("*").eq("id", user_id).execute()
```

### handle_network_error
Стандартная обработка сетевых ошибок:

```python
from utils.error_handler import handle_network_error

@handle_network_error("RSS feed fetch")
def fetch_rss_feed(url):
    response = requests.get(url, timeout=30)
    return response.content
```

### handle_parsing_error
Стандартная обработка ошибок парсинга:

```python
from utils.error_handler import handle_parsing_error

@handle_parsing_error("RSS feed")
def parse_rss_feed(xml_content):
    return feedparser.parse(xml_content)
```

## Функции безопасного выполнения

### safe_execute
Безопасное выполнение синхронных функций:

```python
from utils.error_handler import safe_execute

# С возвратом значения по умолчанию
result = safe_execute(
    risky_function,
    arg1, arg2,
    default_return=None,
    log_errors=True
)

# С повторным вызовом исключения
try:
    result = safe_execute(
        risky_function,
        arg1, arg2,
        reraise=True
    )
except SomeException as e:
    # Handle the exception
    pass
```

### async_safe_execute
Безопасное выполнение асинхронных функций:

```python
from utils.error_handler import async_safe_execute

# С возвратом значения по умолчанию
result = await async_safe_execute(
    async_risky_function,
    arg1, arg2,
    default_return=None,
    log_errors=True
)

# С повторным вызовом исключения
try:
    result = await async_safe_execute(
        async_risky_function,
        arg1, arg2,
        reraise=True
    )
except SomeException as e:
    # Handle the exception
    pass
```

## Удобные функции для создания ошибок

```python
from utils.error_handler import (
    raise_database_error,
    raise_network_error,
    raise_ai_service_error,
    raise_telegram_error,
    raise_parsing_error,
    raise_validation_error,
    raise_configuration_error
)

# Быстрое создание ошибок
raise_database_error("Connection failed", operation="connect")
raise_network_error("Request timeout", url="https://example.com")
raise_ai_service_error("API limit exceeded", model="gpt-4")
raise_telegram_error("Chat not found", chat_id=12345)
raise_parsing_error("Invalid XML", source="example.com")
raise_validation_error("Invalid format", field="email", value="invalid")
raise_configuration_error("Missing key", config_key="database_url")
```

## Категории и уровни серьезности

### ErrorCategory
- `DATABASE` - Ошибки базы данных
- `NETWORK` - Сетевые ошибки
- `AI_SERVICE` - Ошибки AI сервисов
- `TELEGRAM` - Ошибки Telegram API
- `PARSING` - Ошибки парсинга
- `VALIDATION` - Ошибки валидации
- `CONFIGURATION` - Ошибки конфигурации
- `UNKNOWN` - Неизвестные ошибки

### ErrorSeverity
- `LOW` - Низкая серьезность (логируется как INFO)
- `MEDIUM` - Средняя серьезность (логируется как WARNING)
- `HIGH` - Высокая серьезность (логируется как ERROR)
- `CRITICAL` - Критическая серьезность (логируется как CRITICAL)

## Миграция существующего кода

### До (старый подход)
```python
try:
    result = some_operation()
except Exception as e:
    logger.error(f"Error in operation: {e}")
    return None
```

### После (новый подход)
```python
from utils.error_handler import handle_database_error, safe_execute

@handle_database_error("some operation")
def some_operation():
    # Implementation
    pass

# Или
result = safe_execute(some_operation, default_return=None)
```

## Лучшие практики

1. **Используйте специализированные классы ошибок** для разных типов операций
2. **Добавляйте контекстную информацию** через параметры details
3. **Сохраняйте оригинальные исключения** через параметр cause
4. **Используйте декораторы** для стандартизации обработки ошибок
5. **Применяйте retry логику** для временных сбоев
6. **Логируйте ошибки** с соответствующим уровнем серьезности

## Примеры использования в проекте

### Database Service
```python
from utils.error_handler import handle_database_error, DatabaseError

@handle_database_error("news upsert")
def upsert_news(items):
    if not items:
        raise ValidationError("Empty news items list")
    
    try:
        return supabase.table("news").upsert(items).execute()
    except Exception as e:
        raise DatabaseError(
            message="Failed to upsert news",
            operation="upsert",
            table="news",
            details={"item_count": len(items)},
            cause=e
        )
```

### RSS Parser
```python
from utils.error_handler import handle_parsing_error, retry_on_error

@retry_on_error(max_attempts=3, exceptions=(NetworkError,))
@handle_parsing_error("RSS feed")
def parse_rss_source(url, source_name):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return feedparser.parse(response.content)
    except requests.RequestException as e:
        raise NetworkError(
            message="Failed to fetch RSS feed",
            url=url,
            cause=e
        )
```

### Telegram Bot
```python
from utils.error_handler import handle_telegram_error, TelegramError

@handle_telegram_error("message sending")
async def send_digest(chat_id, digest_text):
    try:
        await bot.send_message(chat_id, digest_text)
    except aiogram.exceptions.TelegramRetryAfter as e:
        raise TelegramError(
            message="Rate limited",
            chat_id=chat_id,
            retry_after=e.retry_after,
            cause=e
        )
```

## Мониторинг и алерты

Система автоматически логирует ошибки с соответствующими уровнями:

- **CRITICAL** ошибки должны триггерить алерты
- **HIGH** ошибки требуют внимания
- **MEDIUM** ошибки логируются для мониторинга
- **LOW** ошибки для информационных целей

Логи содержат структурированную информацию:
```
[DATABASE] Failed to insert user | Details: {'operation': 'insert', 'table': 'users'} | Caused by: ConnectionError: Connection refused
```
