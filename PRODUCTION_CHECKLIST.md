# 🚀 Production Readiness Checklist - PulseAI

**Последнее обновление:** 22 октября 2025  
**Версия:** 1.1  
**Цель:** Готовность к продакшену через 1 месяц

---

## ✅ Week 3: Admin Panel Complete Unification (COMPLETED)

### Admin Panel Architecture
- [x] **Полная унификация дизайна** - все компоненты приведены к NeoGlass дизайн-системе
- [x] **Русификация интерфейса** - весь админ-интерфейс переведен на русский язык
- [x] **Системная архитектура** - System Monitor перенесен в Metrics, News/Events объединены в Content
- [x] **Переиспользуемые компоненты** - созданы Toggle, Chip, Accordion, StatusIndicator
- [x] **Design Tokens** - заменены все hardcoded цвета на семантические токены

### Technical Cleanup
- [x] **Удаление неиспользуемых файлов** - AdminTest.tsx, TestMetrics.tsx, AdminApp.tsx, AdminMetricsEnhanced.tsx
- [x] **Исправление CSS классов** - text-muted-foreground → text-muted во всех файлах
- [x] **Очистка корня проекта** - удалены временные MD файлы и PID файлы
- [x] **Улучшение структуры** - оптимизированы импорты и типизация

### Code Quality
- [x] **TypeScript ошибки** - все ошибки компиляции исправлены
- [x] **Сборка проекта** - npm run build проходит успешно
- [x] **Git коммиты** - все изменения закоммичены с описательными сообщениями
- [x] **Pre-commit hooks** - проверка на утечку секретов проходит успешно

---

## ✅ Week 1: Technical Debt & Stability (COMPLETED)

### Code Quality
- [x] Все незакоммиченные изменения закоммичены (8 коммитов)
- [x] Flake8 ошибки исправлены (было 9, стало 0)
- [x] TODO обновлены с привязкой к плану MVP (7 TODO)
- [x] Pre-push hooks проходят успешно
- [x] Black форматирование применено

### Security Basics
- [x] .env файлы в .gitignore
- [x] Pre-commit hooks установлены (блокируют секреты)
- [x] Pre-push hooks проверяют код
- [x] Секреты импортируются из config, не хардкодятся
- [x] Auto env restore система работает

### Testing
- [x] Unit тесты запускаются (261/345 passed - 76%)
- [ ] **TODO:** Исправить критичные падающие тесты
- [ ] **TODO:** Добавить integration тесты для production

### Documentation
- [x] CHANGELOG.md обновлен
- [x] TASKS.md актуален
- [x] AUTO_ENV_RESTORE.md создан
- [x] Cursor AI rules обновлены

---

## 🎯 Week 2: Subscriptions & Core Features

### Subscriptions Integration (Priority: 🟡)
- [ ] Подключить SubscriptionService к обработчикам подписок
- [ ] Реализовать автоматическую отправку дайджестов через tools/send_daily_digests.py
- [ ] Добавить cron-задачи для регулярных уведомлений:
  ```cron
  # Утренний дайджест (09:00)
  0 9 * * * cd /path/to/project && python tools/send_daily_digests.py --time morning
  # Вечерний дайджест (18:00)
  0 18 * * * cd /path/to/project && python tools/send_daily_digests.py --time evening
  ```
- [ ] Протестировать полный цикл: подписка → генерация → отправка

### Notification Settings API
- [ ] Implement `get_notification_settings` function in db_models
- [ ] Implement `upsert_notification_setting` function in db_models
- [ ] Update routes/api_routes.py endpoints (lines 659, 670)
- [ ] Добавить proper error handling для всех endpoints

### Pagination
- [ ] Добавить pagination для больших списков новостей (routes/news_routes.py:45)
- [ ] Limit: 50 items per page
- [ ] Offset-based или cursor-based pagination

---

## ⚡ Week 3: Performance & Infrastructure

### Caching
- [ ] **Redis или in-memory cache**:
  - [ ] API endpoints (/api/news, /api/events) - TTL 60s
  - [ ] Дайджесты дня - TTL 5 минут
  - [ ] Метрики статистики - TTL 15 минут
- [ ] Создать utils/cache_manager.py
- [ ] Добавить cache warming при старте

### Rate Limiting
- [ ] Установить Flask-Limiter
- [ ] API endpoints: 100 req/min per IP
- [ ] Telegram Bot: 30 req/min per user
- [ ] AI generation: 10 req/hour per user
- [ ] Graceful degradation при превышении лимитов

### Authentication & Security
- [ ] **Authentication** для API endpoints:
  - [ ] Token-based auth
  - [ ] API key validation
  - [ ] User session management
- [ ] **Input Validation**:
  - [ ] Sanitize all user inputs
  - [ ] SQL injection protection (ORM)
  - [ ] XSS protection

### Monitoring & Metrics
- [ ] **Metrics collection**:
  - [ ] Response time (P50, P95, P99)
  - [ ] Error rate
  - [ ] Active users
  - [ ] AI token usage
  - [ ] Database query time
- [ ] **Health endpoints**:
  - [ ] /health - basic health check
  - [ ] /metrics - Prometheus-style metrics
  - [ ] /admin/monitoring - dashboard
- [ ] **Alerting**:
  - [ ] Error rate > 5% → alert
  - [ ] Response time > 2s → warning
  - [ ] Database down → critical alert

### Logging Production
- [ ] **Structured JSON logging**:
  - [ ] File handler: logs/production.log (10MB max, 30 backups)
  - [ ] Stream handler: stdout для Docker
  - [ ] Log levels: INFO для normal, ERROR для failures
- [ ] **Request tracking**:
  - [ ] request_id для трейсинга
  - [ ] User agent logging
  - [ ] IP logging (for rate limiting)

---

## 🔒 Week 4: CI/CD & Security

### CI/CD Setup
- [ ] **GitHub Actions**:
  - [ ] .github/workflows/deploy.yml
  - [ ] Trigger on push to main
  - [ ] Run tests → lint → deploy
- [ ] **SSH Deploy Script**:
  - [ ] scripts/deploy.sh
  - [ ] Pull latest
  - [ ] Restart services
  - [ ] Run migrations
  - [ ] Health check after deploy

### Security Audit
- [ ] **OWASP Top 10 проверка**:
  - [x] SQL Injection protection (ORM used)
  - [x] XSS protection (escaping)
  - [ ] CSRF tokens для форм
  - [ ] Rate limiting на auth endpoints
  - [x] Secrets в environment variables
  - [ ] HTTPS only в production
  - [ ] Security headers (CSP, X-Frame-Options)
- [ ] **Tools**:
  - [ ] pip install safety bandit
  - [ ] safety check
  - [ ] bandit -r . -f json -o security_report.json

### Database Optimization
- [ ] **Индексы**:
  - [ ] CREATE INDEX idx_news_category_date ON news(category, published_at DESC);
  - [ ] CREATE INDEX idx_digests_user_created ON digests(user_id, created_at DESC);
  - [ ] CREATE INDEX idx_events_date ON events(event_date DESC);
- [ ] **Slow query log**:
  - [ ] ALTER SYSTEM SET log_min_duration_statement = 1000; -- 1 second
  - [ ] Analyze slow queries
  - [ ] Optimize with EXPLAIN ANALYZE
- [ ] **Connection pooling**:
  - [x] DatabaseService с pooling (5 connections)
  - [ ] Monitor pool utilization

---

## 🧪 Week 5: Load Testing & Monetization Prep

### Load Testing
- [ ] **Locust или Apache Bench**:
  - [ ] tests/load/locustfile.py
  - [ ] 100 одновременных пользователей
  - [ ] 1000 одновременных пользователей
  - [ ] Spike test (резкий рост)
- [ ] **Цели**:
  - [ ] Response time < 1s при 100 users
  - [ ] Error rate < 1%
  - [ ] No memory leaks

### Monetization Foundation
- [ ] **Database schema**:
  - [ ] subscription_tiers table (free, pro, premium)
  - [ ] user_payments table (amount, status, provider)
  - [ ] Migration: 2025_11_add_subscriptions_tiers.sql
- [ ] **API endpoints**:
  - [ ] /api/subscribe/<tier>
  - [ ] /api/payment/webhook (Stripe or Telegram Stars)
  - [ ] /api/user/subscription/status

### Backup Strategy
- [ ] **Daily backup**:
  - [ ] scripts/backup_db.sh
  - [ ] Cron: 0 3 * * * (3 AM daily)
  - [ ] pg_dump to backups/pulseai_YYYYMMDD.sql.gz
  - [ ] Keep last 30 days
- [ ] **Restore testing**:
  - [ ] Test restore monthly
  - [ ] Document restore procedure

---

## 🚀 Week 6: Deployment & Launch

### VPS Deployment
- [ ] **VPS Requirements**:
  - [ ] Ubuntu 22.04 LTS
  - [ ] 2 CPU, 4GB RAM minimum
  - [ ] Domain name + SSL certificate
- [ ] **Services setup**:
  - [ ] systemd service: pulseai-webapp.service
  - [ ] systemd service: pulseai-bot.service
  - [ ] systemd service: cloudflared.service
  - [ ] nginx reverse proxy
- [ ] **Monitoring**:
  - [ ] systemctl status checks
  - [ ] Log rotation configured
  - [ ] Disk space monitoring

### SSL & Domain
- [ ] **SSL Certificate**:
  - [ ] Let's Encrypt via certbot
  - [ ] Auto-renewal configured
  - [ ] HTTPS enforced
- [ ] **Domain Setup**:
  - [ ] DNS A record to VPS IP
  - [ ] CNAME for www
  - [ ] Cloudflare (optional)

### Environment Setup
- [ ] **Production .env**:
  - [ ] ENVIRONMENT=production
  - [ ] DEBUG=False
  - [ ] All API keys configured
  - [ ] Database credentials
  - [ ] Telegram webhook URL
- [ ] **Backups**:
  - [ ] env-save "production config initial"

---

## 🎯 Pre-Launch Checklist

### Must Have (для запуска)
- [x] Technical Debt Cleanup
- [ ] Subscriptions Integration
- [ ] Basic caching & rate limiting
- [ ] Security basics (HTTPS, secrets, SQL injection protection)
- [ ] Deployment на VPS
- [ ] Backup strategy

### Nice to Have (можно после запуска)
- [ ] CI/CD автоматизация (можно деплоить вручную сначала)
- [ ] Grafana monitoring (достаточно простого /health endpoint)
- [ ] Load testing (можно сделать после запуска)
- [ ] Monetization (можно добавить через 1-2 месяца)

---

## 📊 Production Metrics

### System Health
- **Uptime target:** 99.5% (3.6 часов downtime в месяц)
- **Response time:** < 1s (P95)
- **Error rate:** < 1%
- **Database:** Connection pool utilization < 80%

### User Metrics
- **Active users:** Track daily/weekly/monthly
- **Retention:** Track 7-day, 30-day retention
- **Engagement:** Digests viewed per user

### AI Metrics
- **Token usage:** Track daily cost
- **Savings:** Monitor local predictor vs API (target 60-70%)
- **Quality:** Track confidence scores (target > 0.7)

---

## 🔧 Troubleshooting

### Common Issues
1. **Service не запускается:**
   - Check logs: `tail -f logs/production.log`
   - Check .env: `env-list`
   - Check ports: `netstat -tuln | grep :8001`

2. **Database connection failed:**
   - Check credentials in .env
   - Check Supabase status
   - Check network connectivity

3. **High error rate:**
   - Check logs for patterns
   - Check external API status (OpenAI, Telegram)
   - Check rate limits

---

## 📞 Support

**Repository:** https://github.com/denius89/news_ai_bot  
**Documentation:** docs/README.md  
**Issues:** GitHub Issues

---

**Статус:** 🟡 В процессе (Week 1 завершена)  
**Следующий шаг:** Week 2 - Subscriptions Integration

