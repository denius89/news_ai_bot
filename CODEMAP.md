# 📂 Project Structure

_Generated on 2025-09-24 09:19:35 UTC_

```
├── .github/
│   └── workflows/
│       ├── integration.yml
│       └── tests.yml
├── ai_modules/
│   ├── __init__.py
│   ├── credibility.py
│   └── importance.py
├── config/
│   ├── logging.yaml
│   └── sources.yaml
├── database/
│   ├── __init__.py
│   ├── db_models.py
│   ├── init_tables.sql
│   └── seed_data.sql
├── digests/
│   ├── __init__.py
│   ├── ai_summary.py
│   └── generator.py
├── docs/
│   ├── ARCHITECTURE.md
│   ├── COMMUNICATION.md
│   ├── DEPLOY.md
│   ├── ROADMAP.md
│   └── VISION.md
├── logs/
├── parsers/
│   ├── __init__.py
│   ├── events_parser.py
│   └── rss_parser.py
├── routes/
│   ├── __init__.py
│   └── news_routes.py
├── static/
│   └── style.css
├── templates/
│   ├── base.html
│   ├── digest.html
│   ├── events.html
│   └── index.html
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_ai_modules.py
│   ├── test_ai_summary.py
│   ├── test_db_content.py
│   ├── test_db_insert.py
│   ├── test_deepl.py
│   ├── test_digests.py
│   ├── test_main.py
│   ├── test_openai.py
│   ├── test_parsers.py
│   └── test_supabase.py
├── tools/
│   ├── fetch_and_store_events.py
│   ├── fetch_and_store_news.py
│   ├── fix_old_news.py
│   ├── repo_map.py
│   └── show_news.py
├── .env.example
├── .gitignore
├── CODEMAP.md
├── config.py
├── main.py
├── MASTER_FILE.md
├── pytest.ini
├── README.md
├── requirements.txt
├── TASKS.md
└── webapp.py
```
