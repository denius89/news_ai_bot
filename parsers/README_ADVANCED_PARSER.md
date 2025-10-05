# 🧩 AdvancedParser - Умный универсальный парсер новостей

## 📖 Описание

`AdvancedParser` - это продвинутый асинхронный парсер новостей для PulseAI, который объединяет лучшие решения для извлечения контента. Автоматически определяет тип источника (RSS/HTML/API) и применяет каскадную стратегию извлечения с AI-фильтрацией.

## 🔧 Основные возможности

### 🎯 Автоматическое определение типа источника
- **RSS/XML фиды** - парсинг через feedparser
- **HTML страницы** - извлечение контента каскадным методом
- **API endpoints** - обработка JSON ответов

### 🧠 Каскадное извлечение контента
1. **news-please** (приоритет 1) - машинное обучение для извлечения
2. **trafilatura** (приоритет 2) - надежное извлечение текста
3. **AutoScraper** (fallback) - обученные шаблоны извлечения

### 🤖 AI-фильтрация
- **Оценка важности** - через `ai_modules.importance`
- **Оценка достоверности** - через `ai_modules.credibility`
- **Автоматическая фильтрация** - сохранение только релевантных новостей

### ⚡ Асинхронность и производительность
- **Параллельная обработка** - до 10 источников одновременно
- **Connection pooling** - переиспользование HTTP соединений
- **Retry логика** - автоматические повторы при ошибках

## 🚀 Использование

### Базовый запуск
```python
from parsers.advanced_parser import AdvancedParser
import asyncio

async def main():
    async with AdvancedParser() as parser:
        stats = await parser.run()
        print(f"Сохранено {stats['total_saved']} новостей")

asyncio.run(main())
```

### Настройка параметров
```python
async with AdvancedParser(
    max_concurrent=5,      # Максимум одновременных запросов
    min_importance=0.5     # Минимальный порог важности
) as parser:
    stats = await parser.run()
```

### Запуск через скрипт
```bash
# Базовый запуск
python tools/fetch_and_store_news.py

# С настройками
python tools/fetch_and_store_news.py --min-importance 0.5 --max-concurrent 5 --verbose
```

## 📁 Структура конфигурации

Парсер читает источники из `config/sources.yaml`:

```yaml
crypto:
  btc:
    sources:
      - name: "Bitcoin Magazine"
        url: "https://bitcoinmagazine.com/.rss/full/"
      - "CoinTelegraph: https://cointelegraph.com/rss/tag/bitcoin"
      
tech:
  ai:
    sources:
      - name: "OpenAI Blog"
        url: "https://openai.com/blog/rss.xml"
```

## 🔍 Алгоритм работы

### 1. Инициализация
- Загрузка конфигурации источников
- Создание HTTP сессии с connection pooling
- Настройка семафора для ограничения параллельности

### 2. Обработка источника
- Загрузка контента по URL
- Определение типа источника (RSS/HTML)
- Извлечение данных соответствующим методом

### 3. Извлечение контента (HTML)
- **news-please**: машинное обучение для извлечения
- **trafilatura**: надежное извлечение текста
- **AutoScraper**: обученные шаблоны

### 4. AI-фильтрация
- Оценка важности через `evaluate_importance()`
- Оценка достоверности через `evaluate_credibility()`
- Фильтрация по минимальному порогу важности

### 5. Сохранение
- Сохранение в БД через `insert_news_item()`
- Логирование результатов

## 📊 Логирование

Парсер использует структурированное логирование:

```
[INFO] [crypto/btc] https://bitcoinmagazine.com/.rss/full/ -> START
[INFO] [crypto/btc] https://bitcoinmagazine.com/.rss/full/ -> SUCCESS (news-please, importance: 0.85)
[DEBUG] [crypto/btc] Bitcoin Reaches New High -> SAVED (importance: 0.85)
```

## 🧪 Тестирование

### Запуск тестов
```bash
# Все тесты
pytest tests/test_advanced_parser.py -v

# Конкретный тест
pytest tests/test_advanced_parser.py::TestAdvancedParser::test_extract_with_newsplease_success -v

# С покрытием
pytest tests/test_advanced_parser.py --cov=parsers.advanced_parser --cov-report=html
```

### Тестовые сценарии
- ✅ Успешное извлечение контента с Binance Blog
- ✅ Обработка сетевых ошибок
- ✅ Вызов AI-модулей оценки
- ✅ Интеграция с database.db_insert
- ✅ Каскадное извлечение контента
- ✅ Фильтрация по важности

## 📈 Производительность

### Оптимизации
- **Connection pooling** - переиспользование TCP соединений
- **Асинхронность** - параллельная обработка источников
- **Семафор** - ограничение нагрузки на серверы
- **Timeout настройки** - предотвращение зависаний

### Мониторинг
- Время выполнения каждого источника
- Статистика успешности
- Детальные логи ошибок

## 🔧 Требования

### Зависимости
```bash
pip install aiohttp feedparser news-please trafilatura autoscraper pyyaml
```

### Системные требования
- Python 3.8+
- Доступ к интернету
- Конфигурация источников в `config/sources.yaml`

## 🐛 Отладка

### Включение подробного логирования
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

### Тестирование конкретного источника
```python
async def test_specific_source():
    parser = AdvancedParser()
    await parser._init_session()
    
    result = await parser._process_source(
        "crypto", "btc", "Test", "https://example.com"
    )
    
    print(result)
    await parser._close_session()
```

## 🚀 Примеры интеграции

### Интеграция в cron задачу
```bash
# Каждые 30 минут
*/30 * * * * cd /path/to/project && python tools/fetch_and_store_news.py
```

### Интеграция в Flask приложение
```python
from parsers.advanced_parser import AdvancedParser

@app.route('/admin/update-news')
async def update_news():
    async with AdvancedParser() as parser:
        stats = await parser.run()
        return jsonify(stats)
```

## 📝 Changelog

### v1.0.0
- ✅ Базовая функциональность парсера
- ✅ Каскадное извлечение контента
- ✅ AI-фильтрация важности и достоверности
- ✅ Асинхронная обработка
- ✅ Полное покрытие тестами
- ✅ Документация и примеры

---

*Создано для PulseAI - умной платформы персонализированных дайджестов новостей*
