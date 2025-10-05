# 📂 Project Structure

_Generated on 2025-10-05 09:41:38 UTC_

```
├── .github/
│   └── workflows/
│       ├── daily-digest.yml
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
├── .runtime/
│   ├── bot.pid
│   └── webapp.pid
├── .vscode/
│   └── settings.json
├── ai_modules/
│   ├── __init__.py
│   ├── credibility.py
│   └── importance.py
├── config/
│   ├── __init__.py
│   ├── constants.py
│   ├── icons_map.json
│   ├── logging.yaml
│   ├── settings.py
│   └── sources.yaml
├── database/
│   ├── migrations/
│   │   ├── 2025_01_04_add_subcategory_field.sql
│   │   ├── 2025_01_05_add_published_at_fmt.sql
│   │   ├── 2025_10_01_published_at_datetime.sql
│   │   ├── 2025_10_02_add_missing_columns.sql
│   │   ├── 2025_10_02_add_updated_at.sql
│   │   ├── 2025_10_02_notifications_indexes.sql
│   │   ├── 2025_10_02_notifications_system.sql
│   │   ├── 2025_10_02_subscriptions_notifications.sql
│   │   └── 2025_10_03_user_notifications.sql
│   ├── __init__.py
│   ├── async_db_models.py
│   ├── create_user_notifications_table.sql
│   ├── db_models.py
│   ├── init_tables.sql
│   ├── MANUAL_MIGRATION_SUBCATEGORY.md
│   ├── MIGRATION_INSTRUCTIONS.md
│   ├── MIGRATION_TO_UNIFIED_SERVICE.md
│   ├── seed_data.sql
│   └── service.py
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
│   ├── DATABASE_MAINTENANCE.md
│   ├── DEPLOY.md
│   ├── ERROR_HANDLING.md
│   ├── SOURCES.md
│   ├── SOURCES_CHECKER.md
│   └── VISION.md
├── examples/
│   └── telegram_sender_example.py
├── logs/
├── models/
│   ├── event.py
│   └── news.py
├── parsers/
│   ├── __init__.py
│   ├── async_rss_parser.py
│   ├── events_parser.py
│   ├── rss_parser.py
│   └── unified_parser_service.py
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
│   ├── async_digest_service.py
│   ├── categories.py
│   ├── digest_ai_service.py
│   ├── digest_service.py
│   ├── notification_delivery_service.py
│   ├── notification_service.py
│   ├── subscription_service.py
│   ├── telegram_notification_service.py
│   └── unified_digest_service.py
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
│   ├── notifications.html
│   ├── style.css
│   └── webapp.css
├── telegram_bot/
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── dashboard.py
│   │   ├── digest.py
│   │   ├── digest_ai.py
│   │   ├── events.py
│   │   ├── notifications.py
│   │   ├── start.py
│   │   └── subscriptions.py
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
│   ├── test_dashboard_webapp.py
│   ├── test_database_service.py
│   ├── test_db_content.py
│   ├── test_db_insert.py
│   ├── test_db_models.py
│   ├── test_deepl.py
│   ├── test_digest_service.py
│   ├── test_digests.py
│   ├── test_error_handler.py
│   ├── test_events.py
│   ├── test_events_parser.py
│   ├── test_events_repository.py
│   ├── test_generator.py
│   ├── test_keyboards_subscriptions.py
│   ├── test_main.py
│   ├── test_main_import.py
│   ├── test_news_repository.py
│   ├── test_openai.py
│   ├── test_parsers.py
│   ├── test_performance_optimization.py
│   ├── test_progress_animation.py
│   ├── test_routes.py
│   ├── test_sources.py
│   ├── test_subscriptions.py
│   ├── test_supabase.py
│   ├── test_telegram_keyboards.py
│   ├── test_telegram_sender.py
│   ├── test_unified_digest_service.py
│   ├── test_unified_parser_service.py
│   ├── test_user_notifications.py
│   └── test_webapp.py
├── tools/
│   ├── database_inspector.py
│   ├── fill_ai_analysis_all.py
│   ├── LEGACY_CLEANUP_PLAN.md
│   ├── migrations.py
│   ├── port_manager.py
│   ├── README_daily_digests.md
│   ├── refresh_news.py
│   ├── repo_map.py
│   └── send_daily_digests.py
├── webapp/
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── README.md
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── vite.config.ts
├── .cursorignore
├── .editorconfig
├── .env.example
├── .flake8
├── .gitignore
├── .pre-commit-config.yaml
├── CODEMAP.md
├── CONTRIBUTING.md
├── LICENSE
├── main.py
├── Makefile
├── MASTER_FILE.md
├── mypy.ini
├── pyproject.toml
├── pytest.ini
├── README.md
├── REFACTORING_FINAL_REPORT.md
├── requirements.txt
├── setup.cfg
├── start_bot.sh
├── TASKS.md
└── webapp.py
```
