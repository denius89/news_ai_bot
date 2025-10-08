# Источники новостей и категории

## Обзор

В проекте PulseAI используется единый источник истины для всех категорий, подкатегорий и RSS источников - файл `config/sources.yaml`. Этот подход обеспечивает:

- **Консистентность** - все компоненты (бот, WebApp, парсеры) используют одни и те же данные
- **Централизованное управление** - добавление новых источников требует изменения только одного файла
- **Автоматическую синхронизацию** - изменения в YAML автоматически отражаются во всех частях системы

## Структура файла sources.yaml

### Иерархия данных

```yaml
crypto:                    # Глобальная категория
  bitcoin:                 # Подкатегория
    icon: btc             # Иконка (ключ для emoji)
    sources:              # Список источников
      - name: Bitcoin Magazine
        url: https://bitcoinmagazine.com/feed
      - name: CoinTelegraph BTC
        url: https://cointelegraph.com/rss/tag/bitcoin
  ethereum:
    icon: eth
    sources:
      - name: Ethereum Blog
        url: https://blog.ethereum.org/feed.xml
```

### Глобальные категории

1. **crypto** - Криптовалюты и блокчейн
2. **sports** - Спорт и спортивные события  
3. **markets** - Финансовые рынки и экономика
4. **tech** - Технологии и IT
5. **world** - Мировые новости и геополитика

### Подкатегории с иконками

#### Crypto
- `bitcoin` (btc) - ₿ Bitcoin новости
- `ethereum` (eth) - Ξ Ethereum и смарт-контракты
- `altcoins` (altcoin) - 🪙 Альткоины
- `defi` (defi) - 🏦 Децентрализованные финансы
- `nft` (nft) - 🖼️ NFT и цифровое искусство
- `gamefi` (gamefi) - 🎮 GameFi и метавселенные
- `exchanges` (exchange) - 🏢 Биржи и торговля
- `regulation` (regulation) - ⚖️ Регулирование
- `security` (security) - 🔒 Безопасность
- `market_trends` (market_trends) - 📊 Рыночные тренды

#### Sports
- `football` (football) - ⚽ Футбол
- `basketball` (basketball) - 🏀 Баскетбол
- `tennis` (tennis) - 🎾 Теннис
- `ufc` (ufc) - 🥊 MMA/UFC
- `cricket` (cricket) - 🏏 Крикет
- `baseball` (baseball) - ⚾ Бейсбол
- `badminton` (badminton) - 🏸 Бадминтон
- `table_tennis` (table_tennis) - 🏓 Настольный теннис
- `esports` (esports) - 🎮 Киберспорт
- `sports_other` (sports_other) - 🏆 Другие виды спорта

#### Markets
- `stocks` (stocks) - 📈 Акции
- `bonds` (bonds) - 📊 Облигации
- `forex` (forex) - 💱 Валютный рынок
- `commodities` (commodities) - 🌾 Сырьевые товары
- `ipos` (ipos) - 📋 IPO и размещения
- `earnings` (earnings) - 💰 Отчеты компаний
- `etf` (etf) - 📊 ETF и фонды
- `economic_data` (economic_data) - 📊 Экономические данные
- `central_banks` (central_banks) - 🏛️ Центральные банки

#### Tech
- `ai` (ai) - 🤖 Искусственный интеллект
- `bigtech` (bigtech) - 💻 Большие технологические компании
- `hardware` (hardware) - 🔧 Аппаратное обеспечение
- `software` (software) - 💿 Программное обеспечение
- `cybersecurity` (cybersecurity) - 🛡️ Кибербезопасность
- `blockchain` (blockchain) - ⛓️ Блокчейн технологии
- `startups` (startups) - 🚀 Стартапы
- `conferences` (conferences) - 🎤 Технические конференции

#### World
- `conflicts` (conflicts) - ⚠️ Конфликты и войны
- `elections` (elections) - 🗳️ Выборы
- `energy` (energy) - ⚡ Энергетика
- `geopolitics` (geopolitics) - 🌍 Геополитика
- `diplomacy` (diplomacy) - 🤝 Дипломатия
- `sanctions` (sanctions) - 🚫 Санкции
- `organizations` (organizations) - 🏛️ Международные организации
- `migration` (migration) - 👥 Миграция
- `climate` (climate) - 🌱 Климат и экология
- `global_risks` (global_risks) - ⚠️ Глобальные риски

## Сервис categories.py

### Основные функции

```python
from services.categories import (
    get_categories,           # Список всех категорий
    get_subcategories,        # Подкатегории для категории
    get_icon,                # Иконка подкатегории
    get_sources,             # Источники подкатегории
    get_all_sources,         # Все источники (category, subcategory, name, url)
    get_category_structure,  # Полная структура
    validate_sources,        # Валидация YAML
    get_emoji_icon,          # Emoji иконка для бота
    get_statistics           # Статистика источников
)
```

### Кэширование

Сервис автоматически кэширует данные из YAML файла и перезагружает их только при изменении файла:

```python
# Первый вызов - загрузка из файла
categories = get_categories()

# Последующие вызовы - из кэша
categories = get_categories()

# При изменении файла - автоматическая перезагрузка
categories = get_categories()
```

## Правила добавления новых источников

### 1. Добавление новой подкатегории

```yaml
crypto:
  new_subcategory:
    icon: new_icon_key        # Уникальный ключ иконки
    sources:
      - name: Source Name
        url: https://example.com/rss
```

### 2. Добавление источника в существующую подкатегорию

```yaml
crypto:
  bitcoin:
    icon: btc
    sources:
      - name: Existing Source
        url: https://existing.com/rss
      - name: New Source      # Добавляем новый источник
        url: https://new.com/rss
```

### 3. Добавление новой глобальной категории

```yaml
new_category:
  subcategory1:
    icon: icon1
    sources:
      - name: Source 1
        url: https://source1.com/rss
  subcategory2:
    icon: icon2
    sources:
      - name: Source 2
        url: https://source2.com/rss
```

### 4. Обновление иконок

Добавьте новый ключ иконки в функцию `get_emoji_icon()` в `services/categories.py`:

```python
icon_map = {
    # ... существующие иконки ...
    'new_icon_key': '🆕',  # Новый emoji
}
```

## Валидация структуры

### Автоматическая валидация

```python
from services.categories import validate_sources

is_valid, errors = validate_sources()
if not is_valid:
    for error in errors:
        print(f"Ошибка: {error}")
```

### API валидация

```bash
curl http://localhost:8001/api/categories/validate
```

### Проверка через тесты

```bash
pytest tests/test_sources.py::TestSourcesYAML::test_subcategories_have_icons -v
```

## Интеграция с компонентами

### Telegram Bot

```python
from telegram_bot.keyboards import categories_inline_keyboard

# Динамическая клавиатура категорий
keyboard = categories_inline_keyboard("subscribe")

# Клавиатура подкатегорий
subcategory_keyboard = subcategories_inline_keyboard("crypto", "subscribe")
```

### WebApp API

```bash
# Получение всех категорий
curl http://localhost:8001/api/categories

# Валидация структуры
curl http://localhost:8001/api/categories/validate
```

### Парсеры

```python
from parsers.rss_parser import parse_source

# Парсинг конкретного источника
news_items = parse_source(
    url="https://example.com/rss",
    category="crypto",
    subcategory="bitcoin", 
    source_name="Example Source"
)
```

### База данных

Все новости и события сохраняются с полями `category` и `subcategory`:

```sql
INSERT INTO news (title, content, category, subcategory, ...)
VALUES ('Title', 'Content', 'crypto', 'bitcoin', ...);
```

## Мониторинг и обслуживание

### Проверка источников

```bash
# Проверка всех источников
make check-sources

# Просмотр отчетов
make sources-report
```

### Статистика

```python
from services.categories import get_statistics

stats = get_statistics()
print(f"Категории: {stats['categories']}")
print(f"Подкатегории: {stats['subcategories']}")
print(f"Источники: {stats['sources']}")
```

### Перезагрузка кэша

```python
from services.categories import reload_sources

reload_sources()  # Принудительная перезагрузка
```

## Лучшие практики

1. **Всегда валидируйте** изменения в YAML через `validate_sources()`
2. **Используйте уникальные ключи** иконок для избежания конфликтов
3. **Тестируйте изменения** через `pytest tests/test_sources.py`
4. **Документируйте новые категории** в этом файле
5. **Проверяйте источники** регулярно через `make check-sources`
6. **Не дублируйте источники** между подкатегориями без необходимости

## Troubleshooting

### Ошибка "Category not found"

Проверьте, что категория существует в `sources.yaml`:
```python
from services.categories import get_categories
print(get_categories())  # Должна содержать нужную категорию
```

### Ошибка "Icon not found"

Убедитесь, что иконка определена в `get_emoji_icon()`:
```python
from services.categories import get_emoji_icon
icon = get_emoji_icon("crypto", "bitcoin")  # Должна вернуть emoji
```

### Проблемы с кэшированием

Принудительно перезагрузите кэш:
```python
from services.categories import reload_sources
reload_sources()
```
