# PulseAI CSS System Guide

**Версия:** 1.0.0  
**Дата:** 2024-12-19  
**Статус:** ✅ Готово к продакшену

## 📋 Содержание

1. [Обзор системы](#обзор-системы)
2. [Архитектура](#архитектура)
3. [Design Tokens](#design-tokens)
4. [Компоненты](#компоненты)
5. [Утилиты](#утилиты)
6. [Анимации](#анимации)
7. [Темная тема](#темная-тема)
8. [Адаптивность](#адаптивность)
9. [Инструменты](#инструменты)
10. [Миграция](#миграция)

## 🎯 Обзор системы

PulseAI использует современную CSS архитектуру с Design Tokens, компонентным подходом и поддержкой темной темы.

### Ключевые принципы:

- **🎨 Design Tokens** - единый источник истины для всех стилей
- **🧩 Компонентный подход** - переиспользуемые UI элементы
- **🌙 Темная тема** - автоматическое переключение
- **📱 Адаптивность** - мобильный first подход
- **⚡ Производительность** - оптимизированные стили

## 🏗️ Архитектура

```
static/css/
├── system/                 # Системные стили
│   ├── tokens.css         # Design Tokens (CSS переменные)
│   ├── variables.css      # Дополнительные переменные
│   ├── layout.css         # Сетка и layout утилиты
│   ├── components.css     # Базовые компоненты
│   ├── animations.css     # Анимации и переходы
│   ├── darkmode.css       # Темная тема
│   ├── progress.css       # Прогресс-бары
│   └── legacy.css         # Совместимость
├── reactor.css            # Reactor компоненты
├── components.css         # Общие компоненты
├── index.css              # Главная страница
├── live_dashboard.css     # Live Dashboard
└── calendar.css           # Календарь
```

## 🎨 Design Tokens

### Цветовая палитра

```css
/* Основные цвета */
--color-primary-500: #3b82f6;     /* Основной синий */
--color-secondary-500: #0ea5e9;   /* Вторичный голубой */

/* Семантические цвета */
--color-success-500: #22c55e;     /* Успех */
--color-warning-500: #f59e0b;     /* Предупреждение */
--color-danger-500: #ef4444;      /* Ошибка */
--color-info-500: #3b82f6;        /* Информация */

/* Фоновые цвета */
--color-bg: #f9fafb;              /* Основной фон */
--color-bg-secondary: #f3f4f6;    /* Вторичный фон */
--color-bg-elevated: #ffffff;     /* Возвышенные элементы */
```

### Типографика

```css
/* Размеры текста */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */

/* Веса шрифтов */
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
```

### Отступы (4px сетка)

```css
--sp-1: 0.25rem;   /* 4px */
--sp-2: 0.5rem;    /* 8px */
--sp-3: 0.75rem;   /* 12px */
--sp-4: 1rem;      /* 16px */
--sp-6: 1.5rem;    /* 24px */
--sp-8: 2rem;      /* 32px */
--sp-12: 3rem;     /* 48px */
```

### Радиусы

```css
--radius-sm: 0.125rem;   /* 2px */
--radius-base: 0.25rem;  /* 4px */
--radius-md: 0.375rem;   /* 6px */
--radius-lg: 0.5rem;     /* 8px */
--radius-xl: 0.75rem;    /* 12px */
--radius-2xl: 1rem;      /* 16px */
```

### Тени

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
```

## 🧩 Компоненты

### Кнопки

```html
<!-- Основная кнопка -->
<button class="btn btn-primary">Сохранить</button>

<!-- Вторичная кнопка -->
<button class="btn btn-secondary">Отмена</button>

<!-- Кнопка-призрак -->
<button class="btn btn-ghost">Подробнее</button>
```

### Карточки

```html
<!-- Базовая карточка -->
<div class="card">
  <div class="card-header">
    <h3 class="card-title">Заголовок</h3>
  </div>
  <div class="card-body">
    <p>Содержимое карточки</p>
  </div>
</div>
```

### Значки

```html
<!-- Статусные значки -->
<span class="badge badge-success">Активно</span>
<span class="badge badge-warning">Ожидание</span>
<span class="badge badge-danger">Ошибка</span>
```

### Алерты

```html
<!-- Информационный алерт -->
<div class="alert alert-info">
  <p>Информационное сообщение</p>
</div>

<!-- Предупреждение -->
<div class="alert alert-warning">
  <p>Предупреждение</p>
</div>
```

## 🛠️ Утилиты

### Flexbox

```html
<!-- Flex контейнер -->
<div class="flex items-center justify-between">
  <span>Левая часть</span>
  <span>Правая часть</span>
</div>

<!-- Flex колонка -->
<div class="flex flex-col gap-4">
  <div>Элемент 1</div>
  <div>Элемент 2</div>
</div>
```

### Grid

```html
<!-- Grid сетка -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <div class="card">Карточка 1</div>
  <div class="card">Карточка 2</div>
  <div class="card">Карточка 3</div>
</div>
```

### Отступы

```html
<!-- Внешние отступы -->
<div class="mt-4 mb-8 mx-auto">Контент</div>

<!-- Внутренние отступы -->
<div class="p-6">Контент с отступами</div>

<!-- Адаптивные отступы -->
<div class="px-4 md:px-6 lg:px-8">Адаптивные отступы</div>
```

### Размеры

```html
<!-- Ширина -->
<div class="w-full max-w-4xl mx-auto">Полная ширина с ограничением</div>

<!-- Высота -->
<div class="h-screen">Полная высота экрана</div>

<!-- Адаптивные размеры -->
<div class="w-full md:w-1/2 lg:w-1/3">Адаптивная ширина</div>
```

## ✨ Анимации

### Встроенные анимации

```html
<!-- Плавное появление -->
<div class="fade-in">Появляется плавно</div>

<!-- Слайд вверх -->
<div class="slide-up">Съезжает вверх</div>

<!-- Пульсация -->
<div class="pulse-soft">Мягкая пульсация</div>

<!-- Масштабирование -->
<div class="hover-scale">Увеличивается при наведении</div>
```

### Кастомные анимации

```css
@keyframes customAnimation {
  0% { transform: translateX(-100%); opacity: 0; }
  100% { transform: translateX(0); opacity: 1; }
}

.custom-element {
  animation: customAnimation 0.3s ease-out;
}
```

## 🌙 Темная тема

### Автоматическое переключение

Система автоматически определяет предпочтения пользователя:

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #111827;
    --color-text: #f9fafb;
    /* ... другие переменные для темной темы */
  }
}
```

### Ручное переключение

```javascript
// Переключение темы
function toggleTheme() {
  if (window.PulseAI && window.PulseAI.theme) {
    const newTheme = window.PulseAI.theme.toggle();
    console.log(`Тема переключена на: ${newTheme}`);
  }
}
```

### Поддержка в компонентах

Все компоненты автоматически адаптируются к темной теме:

```html
<!-- Кнопка в светлой теме -->
<button class="btn btn-primary">Кнопка</button>

<!-- Та же кнопка в темной теме -->
<!-- Стили автоматически изменятся через CSS переменные -->
```

## 📱 Адаптивность

### Breakpoints

```css
/* Мобильные устройства */
@media (max-width: 639px) { /* sm */ }

/* Планшеты */
@media (min-width: 640px) { /* md */ }

/* Десктопы */
@media (min-width: 1024px) { /* lg */ }

/* Большие экраны */
@media (min-width: 1280px) { /* xl */ }
```

### Адаптивные утилиты

```html
<!-- Скрыть на мобильных -->
<div class="hidden sm:block">Видно на планшетах и больше</div>

<!-- Показать только на мобильных -->
<div class="block sm:hidden">Видно только на мобильных</div>

<!-- Адаптивная сетка -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  <!-- 1 колонка на мобильных, 2 на планшетах, 3 на десктопах -->
</div>
```

## 🛠️ Инструменты

### CSS Optimizer

```bash
# Анализ использования CSS классов
python3 tools/optimize_css.py

# Очистка неиспользуемых стилей
python3 tools/cleanup_css.py
```

### Результаты оптимизации

- **Удалено неиспользуемых классов:** 281
- **Сэкономлено байт:** 36,059
- **Эффективность:** 75.6% классов используются

## 🔄 Миграция

### Из inline стилей

**Было:**
```html
<div style="margin-top: 1rem; padding: 1.5rem; background: #f3f4f6;">
  Контент
</div>
```

**Стало:**
```html
<div class="mt-4 p-6 bg-secondary">
  Контент
</div>
```

### Из legacy CSS

**Было:**
```css
.old-button {
  background-color: #3b82f6;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
}
```

**Стало:**
```css
.new-button {
  background-color: var(--color-primary-500);
  color: var(--color-text-inverse);
  padding: var(--sp-2) var(--sp-4);
  border-radius: var(--radius-md);
}
```

## 📊 Производительность

### Размеры файлов

| Файл | Оригинал | Минифицированный | Экономия |
|------|----------|------------------|----------|
| tokens.css | 9.0 KB | 6.4 KB | 28.9% |
| layout.css | 10.8 KB | 8.5 KB | 21.6% |
| components.css | 10.7 KB | 8.5 KB | 21.2% |
| **Всего** | **81.6 KB** | **59.3 KB** | **27.3%** |

### Рекомендации

1. **Используйте минифицированные версии** в продакшене
2. **Подключайте только нужные компоненты** на каждой странице
3. **Кешируйте CSS файлы** на CDN
4. **Регулярно очищайте неиспользуемые стили**

## 🎯 Лучшие практики

### ✅ Рекомендуется

- Используйте Design Tokens вместо хардкода
- Применяйте компонентный подход
- Тестируйте в обеих темах
- Оптимизируйте для мобильных устройств
- Используйте семантические имена классов

### ❌ Избегайте

- Inline стилей в HTML
- Хардкода цветов и размеров
- Дублирования CSS правил
- Неиспользуемых стилей
- Слишком специфичных селекторов

## 🔧 Поддержка

### Обновление системы

1. Добавьте новые Design Tokens в `tokens.css`
2. Создайте компоненты в `components.css`
3. Обновите документацию
4. Протестируйте в обеих темах

### Отладка

```css
/* Включить отладку CSS */
* {
  outline: 1px solid red !important;
}

/* Показать все CSS переменные */
:root {
  border: 2px dashed blue;
}
```

---

## 📞 Контакты

- **Автор:** PulseAI Team
- **Версия:** 1.0.0
- **Лицензия:** MIT

*Документация обновлена: 2024-12-19*
