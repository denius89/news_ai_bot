# Руководство по получению API токенов для провайдеров событий

## Бесплатные API токены (обязательно для разнообразия событий)

### 1. FINNHUB (Markets - IPO, earnings, экономика)
**Важность:** ⭐⭐⭐⭐⭐ (основной источник markets событий)

1. Зарегистрируйтесь на https://finnhub.io/register
2. Получите бесплатный API key (60 req/min)
3. Добавьте в `.env`:
```bash
FINNHUB_TOKEN=your_finnhub_token_here
```

### 2. GITHUB (Tech - релизы проектов)
**Важность:** ⭐⭐⭐⭐ (все major tech релизы)

1. Перейдите на https://github.com/settings/tokens
2. Generate new token (classic) → read:public_repo
3. Добавьте в `.env`:
```bash
GITHUB_TOKEN=ghp_your_token_here
```

### 3. COINGECKO (Crypto - события криптовалют)
**Важность:** ⭐⭐⭐ (бесплатный, но лимиты)

**Примечание:** CoinGecko Events API был deprecated. Используйте альтернативу:
- Временно отключен в коде
- Заменен на scraping CoinMarketCap

### 4. PANDASCORE (Esports - LoL, CS:GO, Dota)
**Важность:** ⭐⭐⭐⭐ (все киберспорт события)

1. Зарегистрируйтесь на https://pandascore.co/users/sign_up
2. Получите бесплатный токен (1000 req/hour)
3. Добавьте в `.env`:
```bash
PANDASCORE_TOKEN=your_pandascore_token
```

### 5. FOOTBALL-DATA (Football - футбольные матчи)
**Важность:** ⭐⭐⭐ (топ лиги футбола)

1. Зарегистрируйтесь на https://www.football-data.org/client/register
2. Получите бесплатный токен (10 req/min, ограниченные лиги)
3. Добавьте в `.env`:
```bash
FOOTBALL_DATA_TOKEN=your_football_token
```

## Бесплатные провайдеры БЕЗ токенов (работают из коробки)

### ✅ Уже работают:
- **TheSportsDB** - спортивные события (бесплатный API)
- **Liquipedia** - киберспорт через MediaWiki API
- **GosuGamers** - киберспорт RSS
- **OECD** - экономические события
- **UN Security Council** - UN встречи
- **DeFiLlama** - DeFi события
- **TokenUnlocks** - разблокировки токенов

### ⚠️ Частично работают:
- **CoinGecko** - API endpoint изменился, нужно обновить код
- **ESPN** - старый код, нужно обновить под BaseEventProvider

## Платные токены (опционально, для расширения)

### COINMARKETCAL (Crypto календарь)
- $29/месяц
- Много крипто событий
```bash
COINMARKETCAL_TOKEN=your_token
```

## Пример .env файла

Создайте файл `.env` в корне проекта:

```bash
# === ОБЯЗАТЕЛЬНЫЕ (для разнообразия) ===
FINNHUB_TOKEN=your_finnhub_token_here
GITHUB_TOKEN=ghp_your_github_token_here
PANDASCORE_TOKEN=your_pandascore_token_here

# === ОПЦИОНАЛЬНО (улучшат покрытие) ===
FOOTBALL_DATA_TOKEN=your_football_token
COINMARKETCAL_TOKEN=your_coinmarketcal_token

# === Другие настройки ===
OPENAI_API_KEY=sk-your-openai-key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
TELEGRAM_BOT_TOKEN=your_telegram_token
```

## После добавления токенов

1. Перезапустите парсер:
```bash
python tools/events/fetch_events.py --days 30
```

2. Проверьте что провайдеры работают:
```bash
python -c "
from events.events_parser import get_events_parser
parser = get_events_parser()
info = parser.get_provider_info()
for name, data in info.items():
    print(f'{name}: enabled={data.get(\"enabled\", False)}')
"
```

3. Ожидайте:
- До: 1639 событий, 95% markets
- После: 5000-8000 событий, разнообразие категорий

## Проблемы и решения

### "Provider will be disabled" в логах
**Причина:** Токен не установлен в .env
**Решение:** Добавьте токен в .env и перезапустите

### API error 404/403
**Причина:** Неверный токен или API endpoint изменился
**Решение:** Проверьте токен, обновите провайдер если нужно

### Duplicate key errors
**Причина:** Было до upsert исправления
**Решение:** ✅ Исправлено - используется upsert вместо insert

