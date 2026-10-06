# 🤖 Настройка автоматического переобучения Self-Tuning моделей

## 📅 Текущее состояние

```
Последнее обучение: 6 октября 2025, 08:34 UTC (10 дней назад)
Версия модели: v1
Точность: F1=0.86 (importance), F1=0.90 (credibility)
Размер датасета: 1330 примеров
```

**Проблема:** Модели устарели, автоматическое переобучение не настроено.

---

## ✅ Решение: Автоматический парсинг с переобучением

Создан новый скрипт `tools/news/fetch_and_train.py`, который:

1. ✅ Парсит свежие новости из всех 255 источников
2. ✅ Проверяет, нужно ли переобучение (по интервалу из конфига)
3. ✅ Собирает новые обучающие данные из БД
4. ✅ Автоматически переобучает модели
5. ✅ Заменяет старые модели, если новые лучше

---

## 🚀 Способы запуска

### **Вариант 1: Ручной запуск**

```bash
# Обычный запуск (парсинг + автоматическое переобучение)
python tools/news/fetch_and_train.py

# Принудительное переобучение (игнорировать интервал)
python tools/news/fetch_and_train.py --force-train

# Только парсинг (без переобучения)
python tools/news/fetch_and_train.py --skip-train

# Подробный вывод
python tools/news/fetch_and_train.py --verbose
```

### **Вариант 2: Через shell-скрипт**

```bash
# Запуск с логированием
./scripts/auto_fetch_and_train.sh
```

### **Вариант 3: Автоматический запуск по расписанию (CRON)**

#### **3.1. Настройка crontab (Linux/macOS)**

```bash
# Открыть редактор crontab
crontab -e

# Добавить одну из следующих строк:

# Каждые 6 часов в 00:00, 06:00, 12:00, 18:00
0 */6 * * * cd /home/user/news_ai_bot && ./scripts/auto_fetch_and_train.sh >> logs/cron.log 2>&1

# Каждые 12 часов в 08:00 и 20:00
0 8,20 * * * cd /home/user/news_ai_bot && ./scripts/auto_fetch_and_train.sh >> logs/cron.log 2>&1

# Раз в день в 03:00 ночи
0 3 * * * cd /home/user/news_ai_bot && ./scripts/auto_fetch_and_train.sh >> logs/cron.log 2>&1

# Каждые 3 часа
0 */3 * * * cd /home/user/news_ai_bot && ./scripts/auto_fetch_and_train.sh >> logs/cron.log 2>&1
```

**Рекомендуемое расписание:** Каждые 6-12 часов

#### **3.2. Проверка работы cron**

```bash
# Посмотреть установленные задачи
crontab -l

# Проверить логи cron
tail -f logs/cron.log

# Проверить логи переобучения
tail -f logs/fetch_and_train.log

# Посмотреть последние логи автозапуска
ls -lt logs/auto_fetch_train_*.log | head -5
```

#### **3.3. Настройка systemd timer (Linux альтернатива)**

Создать файл `/etc/systemd/system/pulseai-retrain.service`:

```ini
[Unit]
Description=PulseAI News Fetch and Model Retraining
After=network.target

[Service]
Type=oneshot
User=project-user
WorkingDirectory=/home/user/news_ai_bot
ExecStart=/home/user/news_ai_bot/scripts/auto_fetch_and_train.sh
StandardOutput=append:/home/user/news_ai_bot/logs/systemd_retrain.log
StandardError=append:/home/user/news_ai_bot/logs/systemd_retrain_error.log
```

Создать файл `/etc/systemd/system/pulseai-retrain.timer`:

```ini
[Unit]
Description=Run PulseAI retraining every 6 hours
Requires=pulseai-retrain.service

[Timer]
OnCalendar=*-*-* 0,6,12,18:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Активировать timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pulseai-retrain.timer
sudo systemctl start pulseai-retrain.timer

# Проверить статус
sudo systemctl status pulseai-retrain.timer
sudo systemctl list-timers pulseai-retrain.timer
```

---

## ⚙️ Конфигурация

Настройки в `config/data/ai_optimization.yaml`:

```yaml
features:
  self_tuning_enabled: true         # Включить self-tuning
  self_tuning_auto_train: true      # Автоматическое переобучение

self_tuning:
  interval_days: 2                  # Интервал переобучения (дни)
  min_samples: 500                  # Минимум примеров для обучения
  max_samples: 10000                # Максимум примеров
  model_type: "logreg"              # Тип модели (logreg | randomforest)
  replace_threshold: 0.01           # Минимальное улучшение для замены (1%)
  backup_enabled: true              # Создавать резервные копии моделей
```

### **Изменение интервала переобучения:**

```yaml
# Каждый день
interval_days: 1

# Каждые 2 дня (по умолчанию)
interval_days: 2

# Раз в неделю
interval_days: 7
```

---

## 🔍 Логика принятия решения о переобучении

```python
def should_retrain():
    # 1. Проверить, включено ли самообучение
    if not self_tuning_enabled:
        return False
    
    # 2. Проверить интервал
    days_since_last_training = now - last_training_date
    if days_since_last_training >= interval_days:
        return True  # Интервал достигнут
    
    # 3. Проверить количество новых данных
    if new_examples_count >= min_samples:
        return True  # Достаточно данных
    
    return False
```

**Условия переобучения:**

1. ✅ `self_tuning_enabled = true`
2. ✅ Прошло >= `interval_days` с последнего обучения
3. ✅ Собрано >= `min_samples` примеров (500)

**Условия замены модели:**

1. ✅ Новая модель обучена успешно
2. ✅ F1-score новой модели > F1-score старой + `replace_threshold`
3. ✅ Если улучшение >= 1%, модель заменяется

---

## 📊 Процесс переобучения

```
ШАГ 1: Парсинг новостей
  ↓ Собрано 200 новых новостей
  ↓ Оценены через OpenAI (importance, credibility)
  ↓ Сохранены в БД

ШАГ 2: Проверка интервала
  ↓ Последнее обучение: 10 дней назад
  ↓ Интервал: 2 дня
  ↓ Решение: ПЕРЕОБУЧИТЬ ✅

ШАГ 3: Сбор данных
  ↓ Из БД: 1500 примеров (новости с AI-оценками)
  ↓ Из rejected.log: 200 примеров (отклонённые новости)
  ↓ Всего: 1700 примеров
  ↓ Извлечено 17 признаков на каждый пример

ШАГ 4: Обучение моделей
  ↓ Train/Test split: 80/20
  ↓ Нормализация признаков (StandardScaler)
  ↓ LogisticRegression обучение
  ↓ Cross-validation оценка

ШАГ 5: Оценка качества
  ↓ Importance: F1=0.875 (старая 0.860, улучшение +1.5%)
  ↓ Credibility: F1=0.915 (старая 0.902, улучшение +1.3%)
  ↓ Решение: ЗАМЕНИТЬ модели ✅

ШАГ 6: Сохранение
  ↓ Создан бэкап старых моделей
  ↓ Сохранены новые модели (.pkl)
  ↓ Обновлены метаданные (meta.json)
  ↓ Версия: v1 → v2
```

---

## 📈 Мониторинг работы

### **Проверить статус моделей:**

```bash
# Метаданные последнего обучения
cat models/local_predictor_meta.json

# Когда обучалась последний раз
python3 -c "
import json
from datetime import datetime
with open('models/local_predictor_meta.json') as f:
    meta = json.load(f)
    last = datetime.fromisoformat(meta['timestamp'])
    print(f'Последнее обучение: {last}')
    print(f'Версия: v{meta[\"version\"]}')
    print(f'F1 Importance: {meta[\"importance_model\"][\"f1_score\"]:.3f}')
    print(f'F1 Credibility: {meta[\"credibility_model\"][\"f1_score\"]:.3f}')
"
```

### **Посмотреть датасет:**

```bash
# Количество примеров
wc -l data/self_tuning_dataset.csv

# Первые строки датасета
head -20 data/self_tuning_dataset.csv
```

### **Проверить логи:**

```bash
# Последние переобучения
tail -100 logs/self_tuning.log

# Последний автозапуск
ls -lt logs/auto_fetch_train_*.log | head -1 | xargs tail -50
```

---

## 🎯 Рекомендации по настройке

### **Для production (стабильная работа):**

```yaml
interval_days: 7              # Раз в неделю
min_samples: 1000             # Больше данных = стабильнее
replace_threshold: 0.02       # 2% улучшение для замены
```

### **Для активного улучшения (быстрая адаптация):**

```yaml
interval_days: 1              # Каждый день
min_samples: 500              # Быстрее начинает обучаться
replace_threshold: 0.005      # 0.5% улучшение достаточно
```

### **Для экономии ресурсов:**

```yaml
interval_days: 14             # Раз в две недели
min_samples: 2000             # Реже, но качественнее
replace_threshold: 0.03       # Только значительные улучшения
```

---

## 🔄 Интеграция в существующий workflow

### **Добавить в Makefile:**

```makefile
# Парсинг с переобучением
fetch-and-train:
	@echo "🚀 Парсинг новостей + переобучение моделей"
	python3 tools/news/fetch_and_train.py

# Только переобучение (без парсинга)
retrain:
	@echo "🤖 Переобучение моделей"
	python3 tools/ai/train_models.py

# Принудительное переобучение
retrain-force:
	@echo "🔄 Принудительное переобучение"
	python3 tools/news/fetch_and_train.py --force-train --skip-fetch
```

Использование:

```bash
make fetch-and-train   # Парсинг + авто-переобучение
make retrain           # Только переобучение
make retrain-force     # Принудительное переобучение
```

---

## ✅ Быстрый старт

```bash
# 1. Запустить парсинг с переобучением прямо сейчас
python tools/news/fetch_and_train.py --force-train

# 2. Проверить результат
cat models/local_predictor_meta.json

# 3. Настроить автозапуск каждые 6 часов
crontab -e
# Добавить: 0 */6 * * * cd /home/user/news_ai_bot && ./scripts/auto_fetch_and_train.sh >> logs/cron.log 2>&1

# 4. Проверить, что cron работает
crontab -l
```

---

## 📞 Уведомления (опционально)

Раскомментировать в `scripts/auto_fetch_and_train.sh`:

```bash
# При успехе
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    -d chat_id="$ADMIN_CHAT_ID" \
    -d text="✅ Модели переобучены! F1: 0.87 (+2%)"

# При ошибке
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    -d chat_id="$ADMIN_CHAT_ID" \
    -d text="❌ Ошибка переобучения. Проверьте логи."
```

---

## 🎉 Итог

После настройки система будет:

1. ✅ Автоматически парсить новости каждые 6-12 часов
2. ✅ Собирать новые обучающие данные из БД
3. ✅ Переобучать модели каждые 2 дня (или по вашему расписанию)
4. ✅ Улучшать точность предсказаний со временем
5. ✅ Экономить 60-70% AI-вызовов к OpenAI

**Результат:** Самообучающаяся система, которая работает БЕЗ ручного вмешательства! 🚀

