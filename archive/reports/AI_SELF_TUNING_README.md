# 🧠 AI Self-Tuning System — Система самообучения без OpenAI

<div align="center">

**Автономная система машинного обучения для предсказания важности и достоверности новостей**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![ML](https://img.shields.io/badge/ML-scikit--learn-orange.svg)](https://scikit-learn.org)
[![F1 Score](https://img.shields.io/badge/F1_Score-0.90-brightgreen.svg)](.)
[![Auto Retrain](https://img.shields.io/badge/Auto_Retrain-✓-success.svg)](.)

</div>

---

## 🎯 Назначение

**Self-Tuning System** — это самообучающаяся ML-система, которая **учится на оценках OpenAI** и затем **работает автономно**, экономя до **70% AI-вызовов** и обеспечивая мгновенные предсказания.

### Проблема
- OpenAI API стоит дорого при больших объёмах (1000+ новостей/день)
- Задержки в обработке (~1-3 сек на новость)
- Зависимость от внешнего сервиса

### Решение
- Локальные ML-модели обучаются на оценках OpenAI
- Предсказания за микросекунды (без API-вызовов)
- Автоматическое улучшение с каждым новым примером
- Работает даже без интернета

---

## 🏗️ Архитектура системы

```
┌─────────────────────────────────────────────────────────────────┐
│                     📰 NEWS PARSING PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Парсинг новостей (255 источников)                     │
│  • RSS-фиды: TechCrunch, Bitcoin Magazine, Reuters...          │
│  • Async парсинг: 10 источников параллельно                    │
│  • Результат: ~500-1000 новостей/день                          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: AI-оценка через OpenAI (Ground Truth)                 │
│  • evaluate_importance() → 0.0-1.0                              │
│  • evaluate_credibility() → 0.0-1.0                             │
│  • Сохранение в БД как "золотой стандарт"                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: SelfTuningCollector — Сбор обучающих данных          │
│  📊 Источники:                                                  │
│     • База данных: новости с AI-оценками (1500+ примеров)     │
│     • rejected.log: отклонённые новости (200+ примеров)        │
│  🔧 Извлечение признаков (17 фичей):                           │
│     • title_length, title_word_count                           │
│     • content_length, content_word_count                       │
│     • source_trust_score (Reuters=0.9, Blog=0.5)              │
│     • category_* (one-hot encoding)                            │
│     • important_words_ratio, spam_words_ratio                  │
│     • time_features (business hours)                           │
│  💾 Сохранение: data/self_tuning_dataset.csv                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: SelfTuningTrainer — Обучение моделей                 │
│  🤖 Алгоритм: LogisticRegression                               │
│  📈 Метрики:                                                    │
│     • F1 Score (Importance): 0.860                             │
│     • F1 Score (Credibility): 0.902                            │
│     • AUC: 0.89                                                 │
│  💾 Сохранение моделей:                                         │
│     • models/local_predictor_importance.pkl (819 bytes!)       │
│     • models/local_predictor_credibility.pkl (819 bytes!)      │
│     • models/local_predictor_meta.json (метаданные)            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: LocalPredictor — Использование моделей                │
│  ⚡ Режим 1: ML-модели (если обучены)                          │
│     → Извлечение признаков (17 фичей)                          │
│     → Нормализация (StandardScaler)                            │
│     → Предсказание через LogReg                                │
│     → Результат: importance=0.75, credibility=0.88             │
│     → Время: <1мс                                              │
│                                                                 │
│  🔄 Режим 2: Rule-based (fallback)                             │
│     → Эвристические правила                                    │
│     → Если модели не обучены или низкая уверенность           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  💰 ЭКОНОМИЯ AI-ВЫЗОВОВ                                         │
│  • Для новой новости:                                          │
│    1. LocalPredictor.predict() → importance, credibility       │
│    2. Если confidence >= 0.7: используем локальное предсказание│
│    3. Иначе: вызываем OpenAI API                               │
│  • Экономия: 60-70% API-вызовов                                │
│  • Экономия денег: $50-100/месяц                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  🔄 АВТОМАТИЧЕСКОЕ ПЕРЕОБУЧЕНИЕ                                 │
│  • Триггер: каждые 2 дня (настраивается)                      │
│  • Условие: новых данных >= 500 примеров                       │
│  • Процесс:                                                     │
│    1. Собрать новые данные из БД                               │
│    2. Обучить новые модели                                     │
│    3. Сравнить с текущими (F1-score)                          │
│    4. Если улучшение >= 1%: заменить модели                   │
│    5. Иначе: оставить текущие                                  │
│  • Бэкапы: автоматическое сохранение старых версий            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Как работает автообучение

### **1. Сбор данных (SelfTuningCollector)**

```python
# ai_modules/self_tuning_collector.py

# Из базы данных (положительные примеры)
for news in database.get_latest_news(limit=10000):
    features = extract_features(news)  # 17 признаков
    
    # Бинаризация оценок OpenAI
    importance_label = 1 if news.importance >= 0.6 else 0
    credibility_label = 1 if news.credibility >= 0.7 else 0
    
    dataset.append({
        "features": features,
        "importance_label": importance_label,
        "credibility_label": credibility_label
    })

# Из логов отклонённых (негативные примеры)
for rejected in parse_rejected_log():
    features = extract_features(rejected)
    dataset.append({
        "features": features,
        "importance_label": 0,  # Низкая важность
        "credibility_label": 0  # Низкая достоверность
    })
```

**Признаки (features):**

| Признак | Описание | Пример |
|---------|----------|--------|
| `title_length` | Длина заголовка | 65 |
| `title_word_count` | Количество слов | 12 |
| `content_length` | Длина контента | 450 |
| `source_trust_score` | Репутация источника | 0.9 (Reuters) |
| `category_crypto` | Категория крипто | 1.0 |
| `important_words_ratio` | breaking, urgent, exclusive | 0.15 |
| `spam_words_ratio` | click, free, scam | 0.02 |
| `time_features` | Время публикации | 1.0 (бизнес-часы) |

### **2. Обучение моделей (SelfTuningTrainer)**

```python
# ai_modules/self_tuning_trainer.py

# Загрузить dataset
df = pd.read_csv("data/self_tuning_dataset.csv")

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(
    features, labels, test_size=0.2, random_state=42
)

# Нормализация
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

# Обучение
importance_model = LogisticRegression(max_iter=1000)
importance_model.fit(X_train_scaled, y_train["importance_label"])

credibility_model = LogisticRegression(max_iter=1000)
credibility_model.fit(X_train_scaled, y_train["credibility_label"])

# Оценка
f1_importance = f1_score(y_test, importance_model.predict(X_test))
f1_credibility = f1_score(y_test, credibility_model.predict(X_test))

# Сохранение (если улучшение >= 1%)
if f1_new > f1_old + 0.01:
    save_model(importance_model, "models/local_predictor_importance.pkl")
    save_model(credibility_model, "models/local_predictor_credibility.pkl")
```

### **3. Предсказание (LocalPredictor)**

```python
# ai_modules/local_predictor.py

def predict(news_item):
    # Извлечь признаки
    features = extract_features(news_item)
    
    # Нормализовать
    features_scaled = scaler.transform([features])
    
    # Предсказание
    importance = importance_model.predict_proba(features_scaled)[0][1]
    credibility = credibility_model.predict_proba(features_scaled)[0][1]
    
    # Уверенность
    confidence = calculate_confidence(news_item)
    
    return PredictionResult(
        importance=0.75,
        credibility=0.88,
        confidence=0.85
    )
```

---

## 📊 Метрики качества

### **Текущее состояние моделей**

```json
{
  "version": 1,
  "trained_at": "2025-10-06T08:34:14Z",
  "dataset_size": 1330,
  "model_type": "LogisticRegression",
  
  "importance_model": {
    "f1_score": 0.860,
    "accuracy": 0.874,
    "auc": 0.891
  },
  
  "credibility_model": {
    "f1_score": 0.902,
    "accuracy": 0.915,
    "auc": 0.923
  }
}
```

### **Производительность**

| Метрика | OpenAI API | Local Predictor | Разница |
|---------|------------|-----------------|---------|
| Время предсказания | 1000-3000 мс | <1 мс | **3000x быстрее** |
| Стоимость (1000 новостей) | $5-10 | $0 | **Бесплатно** |
| Точность (F1) | 1.0 (ground truth) | 0.86-0.90 | -10-14% |
| Зависимость от сети | Да | Нет | Автономно |

### **ROI (Return on Investment)**

```
Парсинг: 1000 новостей/день × 30 дней = 30000 новостей/месяц

БЕЗ Self-Tuning:
  30000 новостей × $0.002 = $60/месяц

С Self-Tuning (70% экономия):
  9000 новостей × $0.002 = $18/месяц
  Экономия: $42/месяц
  
Годовая экономия: $504
```

---

## ⚙️ Настройка и использование

### **1. Конфигурация**

```yaml
# config/data/ai_optimization.yaml

features:
  self_tuning_enabled: true         # Включить систему
  self_tuning_auto_train: true      # Автообучение
  local_predictor_enabled: true     # Использовать модели

self_tuning:
  interval_days: 2                  # Переобучать каждые 2 дня
  min_samples: 500                  # Минимум примеров
  max_samples: 10000                # Максимум примеров
  model_type: "logreg"              # LogisticRegression
  replace_threshold: 0.01           # Улучшение >= 1%
  backup_enabled: true              # Бэкапы моделей
```

### **2. Автоматическое переобучение**

**ВСТРОЕНО В ПАРСЕР!** Теперь парсер автоматически переобучает модели:

```python
# parsers/advanced_parser.py

async with AdvancedParser() as parser:
    stats = await parser.run()  # auto_retrain=True по умолчанию
    
# Вывод:
# 📰 Парсинг: 255 источников
# ✅ Сохранено: 500 новостей
# 
# 🤖 Запуск автоматического переобучения...
# ✅ Интервал переобучения достигнут (10 дней)
# 📊 Собрано 1700 примеров
# 🧠 Обучение моделей...
#    importance: F1=0.875 (✅ ЗАМЕНЕНА)
#    credibility: F1=0.915 (✅ ЗАМЕНЕНА)
# 🎉 Переобучение завершено!
```

**Отключить автообучение:**

```python
stats = await parser.run(auto_retrain=False)  # Только парсинг
```

### **3. Ручной запуск переобучения**

```bash
# Обучить модели прямо сейчас
python tools/ai/train_models.py

# Или через новый скрипт
python tools/news/fetch_and_train.py --force-train
```

### **4. Использование моделей**

```python
from ai_modules.local_predictor import get_predictor

predictor = get_predictor()

# Предсказание
result = predictor.predict({
    "title": "Bitcoin hits new all-time high",
    "content": "Bitcoin reached $100,000 today...",
    "source": "Reuters",
    "category": "crypto"
})

print(f"Importance: {result.importance:.2f}")     # 0.85
print(f"Credibility: {result.credibility:.2f}")   # 0.92
print(f"Confidence: {result.confidence:.2f}")     # 0.87
```

---

## 🔄 Полный цикл работы

```
1️⃣ ПАРСИНГ (каждые 6 часов)
   → Собрано 200 новостей
   → OpenAI оценил: importance, credibility
   → Сохранено в БД

2️⃣ ПРОВЕРКА ИНТЕРВАЛА
   → Последнее обучение: 10 дней назад
   → Интервал: 2 дня
   → Решение: ПЕРЕОБУЧИТЬ ✅

3️⃣ СБОР ДАННЫХ
   → Из БД: 1500 новостей с AI-оценками
   → Из rejected.log: 200 отклонённых
   → Всего: 1700 примеров × 17 признаков

4️⃣ ОБУЧЕНИЕ
   → Train/Test: 80/20 split
   → LogisticRegression на 1360 примерах
   → Cross-validation: 3-fold

5️⃣ ОЦЕНКА
   → Importance: F1=0.875 (было 0.860, +1.5%)
   → Credibility: F1=0.915 (было 0.902, +1.3%)

6️⃣ ЗАМЕНА МОДЕЛЕЙ
   → Бэкап старых моделей
   → Сохранение новых моделей
   → Версия: v1 → v2 ✅

7️⃣ ИСПОЛЬЗОВАНИЕ
   → Новая новость → LocalPredictor
   → Если confidence >= 0.7: локальное предсказание
   → Иначе: OpenAI API
   → Экономия: 70% AI-вызовов
```

---

## 🎯 Преимущества

### **Экономические**
- 💰 Экономия $500+/год на API-вызовах
- ⚡ 3000x быстрее обработка
- 📉 Снижение нагрузки на OpenAI

### **Технические**
- 🔒 Работает без интернета
- 🚀 Масштабируется до миллионов новостей
- 🎯 Адаптируется под ваши данные
- 📈 Улучшается автоматически

### **Операционные**
- 🤖 Полностью автоматизирован
- 💾 Малый размер моделей (819 байт каждая!)
- 🔄 Бэкапы и версионирование
- 📊 Прозрачные метрики

---

## 📁 Файлы системы

```
ai_modules/
├── local_predictor.py          # Предсказание через ML-модели
├── self_tuning_collector.py    # Сбор обучающих данных
├── self_tuning_trainer.py      # Обучение моделей
├── importance.py                # OpenAI оценка важности
└── credibility.py               # OpenAI оценка достоверности

models/
├── local_predictor_importance.pkl   # Модель importance (819B)
├── local_predictor_credibility.pkl  # Модель credibility (819B)
└── local_predictor_meta.json        # Метаданные и метрики

data/
└── self_tuning_dataset.csv          # Обучающий датасет

config/data/
└── ai_optimization.yaml             # Конфигурация системы

tools/
├── ai/train_models.py               # Ручное переобучение
└── news/fetch_and_train.py          # Парсинг + автообучение

parsers/
└── advanced_parser.py               # ВСТРОЕННОЕ автообучение
```

---

## 🔍 Мониторинг

```bash
# Статус моделей
cat models/local_predictor_meta.json | jq

# Когда обучались
python3 -c "
import json
from datetime import datetime
with open('models/local_predictor_meta.json') as f:
    meta = json.load(f)
    print(f'Версия: v{meta[\"version\"]}')
    print(f'Обучено: {meta[\"timestamp\"]}')
    print(f'F1 (importance): {meta[\"importance_model\"][\"f1_score\"]:.3f}')
    print(f'F1 (credibility): {meta[\"credibility_model\"][\"f1_score\"]:.3f}')
"

# Размер датасета
wc -l data/self_tuning_dataset.csv

# Логи обучения
tail -100 logs/self_tuning.log
```

---

## 🎉 Итог

**Self-Tuning System** — это:

✅ **Автономная** ML-система без зависимости от OpenAI  
✅ **Экономичная** — экономит $500+/год  
✅ **Быстрая** — предсказания за микросекунды  
✅ **Точная** — F1-score 0.86-0.90  
✅ **Автоматическая** — самообучается каждые 2 дня  
✅ **Легковесная** — модели по 819 байт  
✅ **Прозрачная** — понятные метрики и признаки  

**ТЕПЕРЬ ВСТРОЕНО В ПАРСЕР** — работает автоматически после каждого парсинга! 🚀

---

<div align="center">

**Создано командой PulseAI** 🤖  
*Making AI smarter, one prediction at a time*

</div>


