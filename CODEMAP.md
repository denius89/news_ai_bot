# 📂 Project Structure

_Generated on 2025-10-05 19:10:52 UTC_

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
│   ├── sources.backup.20251005.yaml
│   ├── sources.backup.before_distribute.20251005_182653.yaml
│   ├── sources.backup.merged.yaml
│   ├── sources.backup.smart_distribute.20251005_182824.yaml
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
│   ├── MIGRATION_INSTRUCTIONS.md
│   ├── seed_data.sql
│   ├── service.py
│   └── service_v2.py
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
│   ├── DIGESTS.md
│   ├── PARSERS.md
│   ├── SOURCES.md
│   └── VISION.md
├── examples/
│   └── telegram_sender_example.py
├── logs/
├── models/
│   ├── event.py
│   └── news.py
├── parsers/
│   ├── __init__.py
│   ├── advanced_parser.py
│   ├── events_parser.py
│   ├── rss_parser.py
│   └── unified_parser.py
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
│   ├── categories.py
│   ├── notification_service.py
│   ├── subscription_service.py
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
│   ├── test_advanced_parser.py
│   ├── test_ai_modules.py
│   ├── test_ai_service.py
│   ├── test_ai_summary.py
│   ├── test_api_notifications.py
│   ├── test_api_subscriptions.py
│   ├── test_bot_routers.py
│   ├── test_cache.py
│   ├── test_clean_text.py
│   ├── test_dashboard_webapp.py
│   ├── test_database_service.py
│   ├── test_db_content.py
│   ├── test_db_insert.py
│   ├── test_db_models.py
│   ├── test_deepl.py
│   ├── test_digest_service.py
│   ├── test_digests.py
│   ├── test_events.py
│   ├── test_events_parser.py
│   ├── test_events_repository.py
│   ├── test_generator.py
│   ├── test_http_client.py
│   ├── test_keyboards_subscriptions.py
│   ├── test_main.py
│   ├── test_main_import.py
│   ├── test_news_repository.py
│   ├── test_openai.py
│   ├── test_parsers.py
│   ├── test_progress_animation.py
│   ├── test_routes.py
│   ├── test_sources.py
│   ├── test_subscriptions.py
│   ├── test_supabase.py
│   ├── test_telegram_keyboards.py
│   ├── test_telegram_sender.py
│   ├── test_unified_services.py
│   ├── test_user_notifications.py
│   └── test_webapp.py
├── tools/
│   ├── clean_old_news.py
│   ├── distribute_sources.py
│   ├── fetch_and_store_news.py
│   ├── fill_ai_analysis_all.py
│   ├── load_fresh_news.py
│   ├── merge_sources.py
│   ├── port_manager.py
│   ├── refresh_news.py
│   ├── repo_map.py
│   ├── run_all.py
│   ├── send_daily_digests.py
│   ├── smart_distribute_sources.py
│   ├── test_advanced_parser.py
│   ├── update_news_with_universal_parser.py
│   ├── update_rss_sources.py
│   └── validate_rss_sources.py
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
├── requirements.txt
├── setup.cfg
├── start_bot.sh
├── TASKS.md
├── test_global_system.py
└── webapp.py
```
