# 🚀 Быстрый старт: Загрузка новостей

## 📊 Текущее состояние системы

**70 субкатегорий, 255 RSS-источников** распределены по категориям:
- 🪙 **crypto**: 10 субкатегорий, 49 источников
- ⚽ **sports**: 30 субкатегорий, 91 источник (включая киберспорт)
- 🌍 **world**: 10 субкатегорий, 49 источников
- 📈 **markets**: 12 субкатегорий, 37 источников
- 💻 **tech**: 8 субкатегорий, 29 источников

---

## ⚡ Быстрые команды

### 1. Сбалансированная загрузка (РЕКОМЕНДУЕТСЯ)

Загрузить **по 50 новостей** из каждой субкатегории (~2,500-3,000 новостей):
```bash
python tools/news/fetch_balanced.py --per-subcategory 50
```

### 2. Умный режим с самообучением

Парсинг + автоматическое переобучение моделей каждые 2 дня:
```bash
python tools/news/fetch_and_train.py
```

### 3. Обучение локальных моделей

После первой загрузки обучите модели для экономии AI токенов:
```bash
python tools/ai/train_models.py
```

### 4. Использование с локальным предиктором

Экономьте **60-70% AI вызовов**:
```bash
python tools/news/fetch_balanced.py --per-subcategory 50 --use-local-predictor
```

---

## 📝 Полный workflow для первого запуска

```bash
# 1. Загрузить начальный датасет (100 новостей на категорию)
python tools/news/fetch_balanced.py --per-subcategory 100

# 2. Обучить локальные модели
python tools/ai/train_models.py

# 3. Далее использовать с локальным предиктором для экономии
python tools/news/fetch_balanced.py --per-subcategory 50 --use-local-predictor
```

---

## ⚙️ Настройка автоматического обновления (cron)

### Вариант 1: Умный режим (рекомендуется)
```bash
# Каждые 6 часов - парсинг + автообучение
0 */6 * * * cd /home/user/news_ai_bot && python3 tools/news/fetch_and_train.py
```

### Вариант 2: Сбалансированная загрузка
```bash
# Каждые 6 часов - по 50 новостей с предиктором
0 */6 * * * cd /home/user/news_ai_bot && python3 tools/news/fetch_balanced.py --per-subcategory 50 --use-local-predictor

# Раз в сутки - глубокая загрузка
0 2 * * * cd /home/user/news_ai_bot && python3 tools/news/fetch_balanced.py --per-subcategory 100 --use-local-predictor
```

---

## 📊 Расчет объема

| Команда | Целевой объем | Реальный объем* | Время** |
|---------|---------------|-----------------|----------|
| `--per-subcategory 30` | 2,100 | ~1,500-1,800 | ~3-5 мин |
| `--per-subcategory 50` | 3,500 | ~2,500-3,000 | ~5-8 мин |
| `--per-subcategory 100` | 7,000 | ~5,000-6,000 | ~10-15 мин |

*Реальный объем меньше из-за AI-фильтрации (importance ≥ 0.3, credibility ≥ 0.7)  
**При использовании `--use-local-predictor` время может быть меньше

---

## 🎯 Экономия AI токенов

### Без локального предиктора:
- Каждая новость = 2 AI вызова (importance + credibility)
- 3,000 новостей = **6,000 AI вызовов** 💸

### С локальным предиктором:
- ~30% новостей проходят через AI
- 3,000 новостей = **~1,800 AI вызовов** 💰
- **Экономия: 70%!**

---

## 🔍 Мониторинг

### Проверка логов:
```bash
# Общие логи парсера
tail -f logs/advanced_parser.log

# Логи сбалансированной загрузки
tail -f logs/fetch_balanced.log

# Логи самообучения
tail -f logs/self_tuning.log

# Логи умного режима
tail -f logs/fetch_and_train.log
```

### Проверка моделей:
```bash
# Список обученных моделей
ls -lh models/

# Метаданные моделей
cat models/local_predictor_meta.json
```

### Проверка датасета:
```bash
# Датасет для обучения
wc -l data/self_tuning_dataset.csv
head -20 data/self_tuning_dataset.csv
```

---

## ⚡ Типичные сценарии

### Сценарий 1: Первый запуск системы
```bash
# Загрузка большого датасета
python tools/news/fetch_balanced.py --per-subcategory 100

# Обучение моделей
python tools/ai/train_models.py

# Проверка работы с предиктором
python tools/news/fetch_balanced.py --per-subcategory 30 --use-local-predictor
```

### Сценарий 2: Регулярное обновление
```bash
# Умный режим (рекомендуется для cron)
python tools/news/fetch_and_train.py
```

### Сценарий 3: Быстрое обновление
```bash
# Загрузить только свежие новости
python tools/news/fetch_balanced.py --per-subcategory 30 --use-local-predictor
```

### Сценарий 4: Глубокая загрузка
```bash
# Один раз в день - максимум новостей
python tools/news/fetch_balanced.py --per-subcategory 100 --min-importance 0.3
```

---

## 📚 Полная документация

Подробная документация: [tools/news/README.md](README.md)

---

**Готово! Начните с команды:**
```bash
python tools/news/fetch_balanced.py --per-subcategory 50
```

