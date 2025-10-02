# 📂 Project Structure

_Generated on 2025-10-02 07:22:40 UTC_

```
├── .github/
│   └── workflows/
│       ├── integration.yml
│       └── tests.yml
├── .ruff_cache/
│   ├── 0.13.2/
│   │   ├── 10116034348768675673
│   │   ├── 11580765189628323361
│   │   ├── 12608753059934882204
│   │   ├── 12962173965777229691
│   │   ├── 13457321434145763533
│   │   ├── 13471084718433087306
│   │   ├── 14488988700195486325
│   │   ├── 17393587638622327346
│   │   ├── 188309776216779933
│   │   ├── 2610218718754177646
│   │   ├── 4229354752440288288
│   │   ├── 544166894708906565
│   │   ├── 6422456311614551866
│   │   └── 8157489936801255236
│   ├── .gitignore
│   └── CACHEDIR.TAG
├── ai_modules/
│   ├── __init__.py
│   ├── credibility.py
│   └── importance.py
├── config/
│   ├── __init__.py
│   ├── constants.py
│   ├── logging.yaml
│   ├── settings.py
│   └── sources.yaml
├── database/
│   ├── migrations/
│   │   ├── 2025_10_01_published_at_datetime.sql
│   │   ├── 2025_10_02_add_missing_columns.sql
│   │   ├── 2025_10_02_add_updated_at.sql
│   │   └── 2025_10_02_subscriptions_notifications.sql
│   ├── __init__.py
│   ├── db_models.py
│   ├── init_tables.sql
│   ├── MIGRATION_INSTRUCTIONS.md
│   └── seed_data.sql
├── digests/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── ai_summary.py
│   ├── configs.py
│   ├── digest_service.py
│   ├── generator.py
│   └── prompts.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── COMMUNICATION.md
│   ├── DEPLOY.md
│   ├── PROGRESS_ANIMATION.md
│   ├── ROADMAP.md
│   ├── TELEGRAM_KEYBOARDS.md
│   └── VISION.md
├── examples/
│   └── telegram_sender_example.py
├── logs/
├── models/
│   ├── event.py
│   └── news.py
├── parsers/
│   ├── __init__.py
│   ├── events_parser.py
│   └── rss_parser.py
├── repositories/
│   ├── events_repository.py
│   └── news_repository.py
├── routes/
│   ├── __init__.py
│   ├── news_routes.py
│   └── subscriptions.py
├── services/
│   ├── __init__.py
│   ├── digest_ai_service.py
│   ├── digest_service.py
│   ├── notification_service.py
│   └── subscription_service.py
├── static/
│   └── style.css
├── telegram_bot/
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── digest.py
│   │   ├── digest_ai.py
│   │   ├── events.py
│   │   ├── start.py
│   │   └── subscriptions.py
│   ├── __init__.py
│   ├── bot.py
│   └── keyboards.py
├── templates/
│   ├── base.html
│   ├── digest.html
│   ├── events.html
│   └── index.html
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_ai_modules.py
│   ├── test_ai_service.py
│   ├── test_ai_summary.py
│   ├── test_bot_routers.py
│   ├── test_clean_text.py
│   ├── test_db_content.py
│   ├── test_db_insert.py
│   ├── test_db_models.py
│   ├── test_deepl.py
│   ├── test_digest_service.py
│   ├── test_digests.py
│   ├── test_events_parser.py
│   ├── test_events_repository.py
│   ├── test_generator.py
│   ├── test_keyboards_subscriptions.py
│   ├── test_main.py
│   ├── test_main_import.py
│   ├── test_news_repository.py
│   ├── test_openai.py
│   ├── test_parsers.py
│   ├── test_progress_animation.py
│   ├── test_routes.py
│   ├── test_subscriptions.py
│   ├── test_supabase.py
│   ├── test_telegram_keyboards.py
│   ├── test_telegram_sender.py
│   └── test_webapp.py
├── tools/
│   ├── apply_migration.py
│   ├── check_database.py
│   ├── fetch_and_store_events.py
│   ├── fetch_and_store_news.py
│   ├── fix_old_news.py
│   ├── README_daily_digests.md
│   ├── repo_map.py
│   ├── send_daily_digests.py
│   ├── show_news.py
│   └── test_daily_digests.py
├── .coverage
├── .editorconfig
├── .env.example
├── .gitignore
├── =2025.1
├── CODEMAP.md
├── CONTRIBUTING.md
├── LICENSE
├── main.py
├── Makefile
├── MASTER_FILE.md
├── pyproject.toml
├── pytest.ini
├── QUICK_FIX.md
├── README.md
├── requirements.txt
├── setup.cfg
├── TASKS.md
└── webapp.py
```
