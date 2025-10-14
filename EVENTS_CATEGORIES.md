# Полная структура категорий и подкатегорий событий PulseAI

## 📊 Текущее состояние (реальные данные)

### 🗂️ MARKETS (Рынки) - 1500 событий

| Подкатегория | Описание | События | Провайдер |
|-------------|----------|---------|-----------|
| `earnings` | Отчеты о прибыли компаний | ~1497 | Finnhub ✅ |
| `ipos` | IPO (первичное размещение) | ~3 | Finnhub ✅ |
| `economic_data` | Экономические показатели | 0 | - |
| `rates` | Решения ЦБ по ставкам | 0 | - |
| `dividends` | Дивиденды | 0 | - |
| `splits` | Сплиты акций | 0 | - |

### 🗂️ SPORTS (Спорт) - 180+ событий

#### ⚽ Футбол (116 событий)
| Подкатегория | Описание | События | Провайдер |
|-------------|----------|---------|-----------|
| `champions_league` | Лига Чемпионов UEFA | ~36 | Football-Data ✅ |
| `europa_league` | Лига Европы UEFA | ~15 | Football-Data ✅ |
| `conference_league` | Лига Конференций UEFA | ~5 | Football-Data ✅ |
| `premier_league` | Английская Премьер-лига | ~40 | Football-Data ✅ |
| `bundesliga` | Немецкая Бундеслига | ~10 | Football-Data ✅ |
| `la_liga` | Испанская Ла Лига | ~8 | Football-Data ✅ |
| `serie_a` | Итальянская Серия А | ~8 | Football-Data ✅ |
| `ligue_1` | Французская Лига 1 | ~8 | Football-Data ✅ |
| `world_cup` | Чемпионат мира FIFA | 0-2 | Football-Data ✅ |
| `football` | Прочие футбольные матчи | ~172 | TheSportsDB ✅ |

#### 🎮 Киберспорт (53 события)
| Подкатегория | Описание | События | Провайдер |
|-------------|----------|---------|-----------|
| `dota2` | Dota 2 турниры | 0 | PandaScore ⚠️ |
| `csgo` | CS:GO турниры | 0 | PandaScore ⚠️ |
| `lol` | League of Legends | ~14 | PandaScore ✅ |
| `valorant` | Valorant | ~29 | PandaScore ✅ |
| `overwatch` | Overwatch | ~4 | PandaScore ✅ |
| `r6siege` | Rainbow Six Siege | ~6 | PandaScore ✅ |
| `rocket_league` | Rocket League | 0 | PandaScore ⚠️ |
| `pubg` | PUBG | 0 | PandaScore ⚠️ |
| `fortnite` | Fortnite | 0 | PandaScore ⚠️ |
| `apex_legends` | Apex Legends | 0 | PandaScore ⚠️ |
| `call_of_duty` | Call of Duty: Warzone | 0 | PandaScore ⚠️ |

#### 🏀 Другие виды спорта (70 событий)
| Подкатегория | Описание | События | Провайдер |
|-------------|----------|---------|-----------|
| `basketball` | Баскетбол (NBA, EuroLeague) | ~10 | TheSportsDB ✅ |
| `hockey` | Хоккей (NHL, KHL) | ~8 | TheSportsDB ✅ |
| `tennis` | Теннис (ATP, WTA) | ~12 | TheSportsDB ✅ |
| `baseball` | Бейсбол (MLB) | ~6 | TheSportsDB ✅ |
| `american_football` | Американский футбол (NFL) | ~5 | TheSportsDB ✅ |
| `rugby` | Регби | ~4 | TheSportsDB ✅ |
| `cricket` | Крикет | ~8 | TheSportsDB ✅ |
| `volleyball` | Волейбол | ~3 | TheSportsDB ✅ |
| `handball` | Гандбол | ~2 | TheSportsDB ✅ |
| `other` | Прочие виды спорта | ~12 | TheSportsDB ✅ |

### 🗂️ CRYPTO (Криптовалюты) - 0 событий (пока)

| Подкатегория | Описание | События | Провайдер |
|-------------|----------|---------|-----------|
| `bitcoin` | Bitcoin события | 0 | CoinGecko ⚠️ |
| `ethereum` | Ethereum события | 0 | CoinGecko ⚠️ |
| `defi` | DeFi протоколы | 0 | DeFiLlama ⚠️ |
| `listing` | Новые листинги | 0 | CoinGecko ⚠️ |
| `unlock` | Разблокировки токенов | 0 | TokenUnlocks ⚠️ |
| `hardfork` | Хардфорки | 0 | CoinMarketCal ⚠️ |
| `mainnet` | Запуски mainnet | 0 | CoinMarketCal ⚠️ |
| `airdrop` | Airdrop события | 0 | CoinMarketCal ⚠️ |

### 🗂️ TECH (Технологии) - 0 событий (пока)

| Подкатегория | Описание | События | Провайдер |
|-------------|----------|---------|-----------|
| `conference` | Конференции | 0 | GitHub ⚠️ |
| `release` | Релизы продуктов | 0 | GitHub ⚠️ |
| `launch` | Запуски продуктов | 0 | ProductHunt 🔜 |
| `update` | Обновления ПО | 0 | GitHub ⚠️ |

### 🗂️ WORLD (Мировые события) - 0 событий (пока)

| Подкатегория | Описание | События | Провайдер |
|-------------|----------|---------|-----------|
| `politics` | Политические события | 0 | UN ⚠️ |
| `summit` | Саммиты (G7, G20) | 0 | - 🔜 |
| `elections` | Выборы | 0 | - 🔜 |
| `climate` | Климатические конференции | 0 | - 🔜 |
| `economy` | Экономические форумы | 0 | - 🔜 |

---

## 📈 Статистика

**Всего категорий:** 5
- Markets, Sports, Crypto, Tech, World

**Всего подкатегорий:** 50+
- Markets: 6 подкатегорий
- Sports: 25+ подкатегорий (9 футбольных турниров + 11 игр киберспорта + 10 видов спорта)
- Crypto: 8 подкатегорий
- Tech: 4 подкатегории
- World: 5 подкатегорий

**Работают сейчас:** 12 подкатегорий
- Markets: 2 (earnings, ipos)
- Sports: 10 (футбол + киберспорт + другие)

**Готовы к активации:** 38+ подкатегорий
- Требуют только включения провайдеров или добавления токенов

---

## 🎯 Приоритет развития

### Высокий (добавить в первую очередь):
1. **Crypto события** - добавить рабочие endpoints
2. **Tech releases** - добавить GITHUB_TOKEN
3. **Баскетбол NBA** - расширить через ESPN
4. **Теннис ATP/WTA** - больше турниров

### Средний:
1. World politics - UN, G7/G20
2. Elections calendar
3. Climate conferences

### Низкий:
1. Дополнительные markets провайдеры (FMP, EODHD)
2. Экзотические виды спорта
3. Региональные события

---

## 📝 Легенда

- ✅ Работает и дает события
- ⚠️ Провайдер реализован но API не работает / нужен токен
- 🔜 Провайдер планируется (не реализован)
- 0 Подкатегория поддерживается но событий пока нет

---

**Обновлено:** 14 октября 2025

