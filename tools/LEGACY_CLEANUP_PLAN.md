# План очистки Legacy кода в tools/

## Анализ файлов в tools/

### ✅ Файлы для сохранения (активные/важные)
1. **check_sources.py** - проверка RSS источников (активный инструмент)
2. **port_manager.py** - управление портами для тестов (используется в CI)
3. **repo_map.py** - генерация CODEMAP.md (используется в git hooks)
4. **send_daily_digests.py** - отправка ежедневных дайджестов (production)
5. **test_daily_digests.py** - тестирование дайджестов
6. **fill_ai_analysis_all.py** - заполнение AI анализа (активный)
7. **refresh_news.py** - обновление новостей (активный)

### 🔄 Файлы для консолидации
1. **add_*.py** - можно объединить в один migration tool
   - add_notifications_correct.py
   - add_notifications_final.py
   - add_subcategory_field.py
   - add_test_notifications.py

2. **apply_*.py** - можно объединить в один migration tool
   - apply_migration.py
   - apply_subcategory_migration.py
   - apply_user_notifications_migration.py

3. **check_*.py** - можно объединить в database inspection tool
   - check_all_columns.py
   - check_all_notifications.py
   - check_database.py
   - check_notifications_schema.py
   - check_subcategory_migration.py
   - check_users_table.py

4. **test_*.py** - можно объединить в testing suite
   - test_api_direct.py
   - test_digest_ai.py
   - test_get_notifications.py
   - test_notifications_api.py
   - test_notifications_webapp.py
   - test_telegram_notifications.py

### ❌ Файлы для удаления (legacy/дублирующие)
1. **debug_*.py** - отладочные скрипты
   - debug_api_issue.py
   - debug_user_lookup.py

2. **fix_*.py** - одноразовые исправления
   - fix_old_news.py
   - fix_user_notifications_schema.py

3. **create_*.py** - одноразовые создания таблиц
   - create_notifications_table.py

4. **cleanup_*.py** - одноразовые очистки
   - cleanup_database.py

5. **optimize_*.py** - одноразовые оптимизации
   - optimize_database.py

6. **database_maintenance.py** - устаревший
7. **fetch_and_store_*.py** - устаревшие (заменены парсерами)
   - fetch_and_store_events.py
   - fetch_and_store_news.py

8. **fill_ai_analysis.py** - дублирует fill_ai_analysis_all.py
9. **show_news.py** - устаревший
10. **run_all.py** - устаревший
11. **proc_utils.py** - устаревший

## План действий

### Этап 1: Удаление legacy файлов
Удалить файлы, которые больше не используются:
- debug_*.py
- fix_*.py (кроме активных)
- create_*.py
- cleanup_*.py
- optimize_*.py
- database_maintenance.py
- fetch_and_store_*.py
- fill_ai_analysis.py (дубликат)
- show_news.py
- run_all.py
- proc_utils.py

### Этап 2: Консолидация миграций
Создать единый migration tool:
- tools/migrations.py - объединяет все add_*.py и apply_*.py

### Этап 3: Консолидация проверок
Создать единый database inspector:
- tools/database_inspector.py - объединяет все check_*.py

### Этап 4: Консолидация тестов
Создать единый testing suite:
- tools/test_suite.py - объединяет все test_*.py

### Этап 5: Обновление документации
- Обновить README.md
- Создать docs/TOOLS.md с описанием активных инструментов

## Результат
После очистки в tools/ останется:
- 7 активных инструментов
- 4 консолидированных инструмента
- Вместо 40+ файлов будет ~11 файлов
- Лучшая организация и понимание назначения каждого инструмента
