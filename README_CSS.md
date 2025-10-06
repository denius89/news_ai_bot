# PulseAI CSS System - Quick Start

## 🚀 Быстрый старт

### Использование компонентов

```html
<!-- Кнопки -->
<button class="btn btn-primary">Основная</button>
<button class="btn btn-secondary">Вторичная</button>

<!-- Карточки -->
<div class="card">
  <div class="card-body">
    <h3 class="card-title">Заголовок</h3>
    <p>Содержимое</p>
  </div>
</div>

<!-- Значки -->
<span class="badge badge-success">Активно</span>
<span class="badge badge-warning">Ожидание</span>
```

### Адаптивная сетка

```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  <div class="card">Элемент 1</div>
  <div class="card">Элемент 2</div>
  <div class="card">Элемент 3</div>
</div>
```

### Темная тема

```html
<!-- Переключатель темы -->
<button class="theme-toggle" onclick="toggleTheme()">
  <svg class="theme-icon-light">☀️</svg>
  <svg class="theme-icon-dark">🌙</svg>
</button>
```

## 🎨 Design Tokens

```css
/* Используйте CSS переменные */
.my-element {
  background-color: var(--color-primary-500);
  padding: var(--sp-4);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}
```

## 📱 Адаптивность

```html
<!-- Адаптивные классы -->
<div class="hidden sm:block">Скрыто на мобильных</div>
<div class="text-sm md:text-base lg:text-lg">Адаптивный текст</div>
<div class="p-4 md:p-6 lg:p-8">Адаптивные отступы</div>
```

## ✨ Анимации

```html
<!-- Встроенные анимации -->
<div class="fade-in">Появление</div>
<div class="slide-up">Слайд вверх</div>
<div class="pulse-soft">Пульсация</div>
<div class="hover-scale">Масштабирование</div>
```

## 🛠️ Инструменты

```bash
# Анализ CSS
python3 tools/optimize_css.py

# Очистка неиспользуемых стилей
python3 tools/cleanup_css.py
```

## 📚 Полная документация

См. [CSS_SYSTEM_GUIDE.md](CSS_SYSTEM_GUIDE.md) для подробного руководства.

---

*PulseAI CSS System v1.0.0*
