# 🤝 Contributing Guide

Спасибо, что хотите помочь развивать **PulseAI**!  
Этот проект открыт для pull requests, предложений и улучшений.

---

## 📌 Как начать

1. **Форкните** репозиторий и клонируйте его:
   ```bash
   git clone https://github.com/<ваш-аккаунт>/news_ai_bot.git
   cd news_ai_bot
   ```

2.	**Создайте виртуальное окружение** и установите зависимости:
	```bash
	python -m venv venv
	source venv/bin/activate   # macOS/Linux
	venv\Scripts\activate      # Windows
	pip install -r requirements.txt
	```

3.	Настройте переменные окружения:
- скопируйте .env.example → .env
- добавьте ключи для **Supabase, OpenAI, DeepL**

---

## 🧪 Тесты

Запуск **unit-тестов**:
```bash
pytest -m "not integration"
```
Запуск **интеграционных тестов** (требуют реальных ключей):
```bash
pytest -m "integration"
```

---

## 🧹 Стиль кода

Мы используем **flake8** и **black**:

```bash
flake8 .
black --check .
```
Автоформатирование:
```bash
black .
```

---

## 🔀 Git flow

- Ветки называем по формату:

day-XX-feature-name
fix/bug-description
docs/update-readme


- Сообщения коммитов:

feat: добавил поддержку фильтров
fix: исправил баг в rss_parser
docs: обновил README.md
chore: обновил CI pipeline


- Перед PR убедитесь, что CI зелёный ✅

## 💡 Советы

- Все задачи фиксируйте в `TASKS.md`.  
- Важные решения заносите в `MASTER_FILE.md`.  
- Если добавляете новые файлы → автохук обновит `CODEMAP.md`.  

---

## 📜 Лицензия

Проект распространяется под лицензией [MIT](LICENSE).