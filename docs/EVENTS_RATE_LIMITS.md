# Event Providers Rate Limits

## Overview

Все event providers в PulseAI используют rate limiting для соблюдения ограничений API и предотвращения блокировок.

---

## ⚙️ Configured Rate Limits

### 🏀 Sports Providers

| Provider | Limit | Интервал | Status | Notes |
|----------|-------|----------|--------|-------|
| **football_data** | 10 req/min | 6 sec | ✅ | FREE tier, 10 calls/minute |
| **thesportsdb** | 100 req/hour | 36 sec | ✅ | Conservative estimate |
| **pandascore** | 1000 req/hour | ~3.6 sec | ✅ | Esports API, FREE tier |
| **liquipedia** | 2 req/min | 30 sec | ✅ | MediaWiki `action=parse` limit |
| **gosugamers** | 6 req/hour | 10 min | ✅ | RSS feed, conservative |

### 🪙 Crypto Providers

| Provider | Limit | Интервал | Status | Notes |
|----------|-------|----------|--------|-------|
| **coinmarketcal** | 100 req/day | ~15 min | ✅ | Daily quota |
| **coingecko** | 10 req/min | 6 sec | ✅ | FREE tier (10-50/min, using 10) |
| **tokenunlocks** | 1 req/sec | 1 sec | ✅ | Conservative (no official docs) |
| **defillama** | 1 req/sec | 1 sec | ⚠️ | Not implemented yet |

### 📈 Markets Providers

| Provider | Limit | Интервал | Status | Notes |
|----------|-------|----------|--------|-------|
| **finnhub** | 60 req/min | 1 sec | ✅ | FREE tier, 60 calls/minute |
| **oecd_events** | 60 req/hour | 60 sec | ✅ | HTML scraping, conservative |
| **eodhd** | 1 req/sec | 1 sec | ⚠️ | Not implemented yet |
| **fmp** | 1 req/sec | 1 sec | ⚠️ | Not implemented yet |
| **nasdaq_rss** | 6 req/hour | 10 min | ⚠️ | Not implemented yet |

### 💻 Tech Providers

| Provider | Limit | Интервал | Status | Notes |
|----------|-------|----------|--------|-------|
| **github_releases** | 5000 req/hour | ~0.72 sec | ✅ | Authenticated GitHub API |
| **lf_events** | 60 req/hour | 60 sec | ⚠️ | Not implemented yet |
| **cncf_events** | 60 req/hour | 60 sec | ⚠️ | Not implemented yet |
| **wikidata_sparql** | 1 req/sec | 1 sec | ⚠️ | Not implemented yet |

### 🌍 World Providers

| Provider | Limit | Интервал | Status | Notes |
|----------|-------|----------|--------|-------|
| **un_sc_programme** | 60 req/hour | 60 sec | ✅ | HTML scraping, conservative |
| **eu_council** | 60 req/hour | 60 sec | ⚠️ | Not implemented yet |
| **ifes_electionguide** | 60 req/hour | 60 sec | ⚠️ | Not implemented yet |
| **unfccc_events** | 60 req/hour | 60 sec | ⚠️ | Not implemented yet |

---

## 🎯 Implementation Details

### Rate Limiter Class

**Location:** `events/providers/rate_limiter.py`

**Algorithm:** Token Bucket

**Features:**
- Async-safe with `asyncio.Lock`
- Configurable per-provider
- Automatic delay calculation
- Thread-safe

**Usage:**
```python
# In provider
await self.rate_limiter.acquire()  # Blocks until rate limit allows
async with self.session.get(url) as response:
    ...
```

### Integration

**BaseEventProvider** автоматически создает rate limiter для каждого провайдера при инициализации:

```python
def __init__(self, name: str, category: str):
    ...
    self.rate_limiter = get_rate_limiter(name)
```

### Configuration

Rate limits настроены в `RATE_LIMITERS` dictionary в `rate_limiter.py`:

```python
RATE_LIMITERS = {
    "football_data": RateLimiter(calls_per_minute=10),
    "github_releases": RateLimiter(calls_per_hour=5000),
    ...
}
```

---

## 📊 Status Summary

**Implemented & Rate Limited:** 11/29 providers (38%)
- ✅ Sports: 5/5 (100%)
- ✅ Crypto: 3/5 (60%)
- ✅ Markets: 2/8 (25%)
- ✅ Tech: 1/4 (25%)
- ✅ World: 1/4 (25%)

**Working Providers:** 11
- All have rate limiting
- All respect API quotas
- All prevent ban/throttling

**TODO Providers:** 18
- Need implementation
- Rate limits already configured
- Ready for integration

---

## 🚀 Testing

```bash
# Test rate limiting
python3 tools/events/fetch_events.py --dry-run --days 7

# Test specific provider
python3 tools/events/fetch_events.py --providers sports_football_data --dry-run

# Check rate limiter config
python3 -c "from events.providers.rate_limiter import RATE_LIMITERS; print(RATE_LIMITERS['football_data'].get_info())"
```

---

## ⚠️ Important Notes

1. **API Keys Required:**
   - football_data → `FOOTBALL_DATA_TOKEN`
   - pandascore → `PANDASCORE_TOKEN`
   - coinmarketcal → `COINMARKETCAL_TOKEN`
   - finnhub → `FINNHUB_TOKEN`
   - github_releases → `GITHUB_TOKEN`

2. **Rate Limit Strategy:**
   - Official API limits used when available
   - Conservative estimates (1 req/sec or 60 req/hour) for undocumented APIs
   - RSS feeds limited to 6 req/hour (every 10 minutes)
   - HTML scraping limited to 60 req/hour (every minute)

3. **Best Practices:**
   - Always use `await self.rate_limiter.acquire()` before requests
   - Handle 429 (Too Many Requests) responses
   - Log rate limit info on provider initialization
   - Monitor logs for rate limit violations

---

## 📝 Next Steps

**Priority 1 (High):**
- [ ] Implement DeFiLlama provider (crypto TVL events)
- [ ] Implement NASDAQ RSS provider (IPO calendar)
- [ ] Implement EODHD provider (earnings)

**Priority 2 (Medium):**
- [ ] EU Council provider (politics)
- [ ] IFES ElectionGuide (elections)
- [ ] FMP provider (financial events)

**Priority 3 (Low):**
- [ ] Linux Foundation events
- [ ] CNCF events
- [ ] Wikidata SPARQL
- [ ] UNFCCC events

---

**Last Updated:** October 13, 2025
**Author:** PulseAI Team

