# 📂 Project Structure

_Generated on 2025-10-03 07:32:48 UTC_

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
│   │   ├── 2025_10_02_notifications_indexes.sql
│   │   ├── 2025_10_02_notifications_system.sql
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
│   ├── api_routes.py
│   ├── news_routes.py
│   ├── subscriptions.py
│   └── webapp_routes.py
├── services/
│   ├── __init__.py
│   ├── digest_ai_service.py
│   ├── digest_service.py
│   ├── notification_service.py
│   └── subscription_service.py
├── static/
│   ├── assets/
│   │   └── logo/
│   │       ├── favicon.ico
│   │       ├── logo_full.jpg
│   │       ├── logo_icon.PNG
│   │       ├── logo_icon_16.png
│   │       ├── logo_icon_180.png
│   │       ├── logo_icon_192.png
│   │       ├── logo_icon_32.png
│   │       ├── logo_icon_512.png
│   │       ├── logo_icon_96.png
│   │       └── site.webmanifest
│   ├── js/
│   │   └── webapp.js
│   ├── style.css
│   └── webapp.css
├── telegram_bot/
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── digest.py
│   │   ├── digest_ai.py
│   │   ├── events.py
│   │   └── start.py
│   ├── __init__.py
│   ├── bot.py
│   └── keyboards.py
├── templates/
│   ├── base.html
│   ├── digest.html
│   ├── events.html
│   ├── index.html
│   └── webapp.html
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_ai_modules.py
│   ├── test_ai_service.py
│   ├── test_ai_summary.py
│   ├── test_api_notifications.py
│   ├── test_api_subscriptions.py
│   ├── test_bot_routers.py
│   ├── test_clean_text.py
│   ├── test_dashboard_handler.py
│   ├── test_dashboard_webapp.py
│   ├── test_db_content.py
│   ├── test_db_insert.py
│   ├── test_db_models.py
│   ├── test_deepl.py
│   ├── test_digest_service.py
│   ├── test_digests.py
│   ├── test_events_parser.py
│   ├── test_events_repository.py
│   ├── test_generator.py
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
│   ├── check_database_schema.py
│   ├── check_notifications_schema.py
│   ├── check_tables.py
│   ├── clean_notifications_data.py
│   ├── create_demo_notifications.py
│   ├── create_table_via_api.py
│   ├── fetch_and_store_events.py
│   ├── fetch_and_store_news.py
│   ├── fix_old_news.py
│   ├── README_daily_digests.md
│   ├── repo_map.py
│   ├── reset_user.py
│   ├── run_migration.py
│   ├── send_daily_digests.py
│   ├── show_news.py
│   ├── test_daily_digests.py
│   ├── test_notifications_insert.py
│   └── test_webapp_notifications.py
├── .coverage
├── .editorconfig
├── .env.example
├── .gitignore
├── =2025.1
├── bot.log
├── bot_clean.log
├── bot_correct.log
├── bot_final.log
├── bot_fixed.log
├── bot_new.log
├── bot_working.log
├── CODEMAP.md
├── CONTRIBUTING.md
├── env_temp.txt
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
├── start_bot.sh
├── TASKS.md
├── test_webapp_debug.html
├── webapp.log
├── webapp.py
├── webapp_fresh.log
└── webapp_new.log
```
