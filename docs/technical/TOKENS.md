# PulseAI Design Tokens

**Версия:** 1.0  
**Дата:** 2025-10-06  
**Проект:** Day 14.5 PRO CSS Refactor

## 🎨 Обзор

Design Tokens - это централизованная система дизайна для PulseAI, обеспечивающая консистентность и масштабируемость UI компонентов.

## 📁 Структура

```
static/css/system/
├── tokens.css      # Основные токены (цвета, типографика, spacing)
└── variables.css   # Утилитарные переменные и подключение токенов
```

## 🎯 Цветовая палитра

### Primary Colors
```css
--color-primary-50   /* #eff6ff - очень светлый */
--color-primary-500  /* #3b82f6 - основной */
--color-primary-600  /* #2563eb - активный */
--color-primary-900  /* #1e3a8a - очень тёмный */
```

### Secondary Colors
```css
--color-secondary-50   /* #f5f3ff */
--color-secondary-500  /* #8b5cf6 */
--color-secondary-600  /* #7c3aed */
```

### Semantic Colors
```css
--color-success: var(--color-success-600);  /* #16a34a */
--color-warning: var(--color-warning-600);  /* #d97706 */
--color-danger: var(--color-danger-600);    /* #dc2626 */
--color-info: var(--color-info-600);        /* #2563eb */
```

### Neutral Colors
```css
--color-gray-50   /* #f9fafb - светлый фон */
--color-gray-500  /* #6b7280 - нейтральный */
--color-gray-900  /* #111827 - тёмный текст */
```

### Семантические маппинги
```css
--color-bg: var(--color-gray-50);           /* Фон */
--color-bg-elevated: #ffffff;               /* Поднятые элементы */
--color-text: var(--color-gray-900);        /* Основной текст */
--color-text-secondary: var(--color-gray-600); /* Вторичный текст */
--color-border: var(--color-gray-200);      /* Границы */
```

## 📝 Типографика

### Шрифты
```css
--font-sans: 'Inter', 'SF Pro Display', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'SF Mono', 'Monaco', 'Inconsolata', monospace;
```

### Размеры
```css
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
--text-5xl: 3rem;      /* 48px */
```

### Веса
```css
--font-light: 300;
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;
--font-extrabold: 800;
```

### Высота строк
```css
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
--leading-loose: 2;
```

## 📏 Spacing

```css
--sp-0: 0;
--sp-1: 0.25rem;     /* 4px */
--sp-2: 0.5rem;      /* 8px */
--sp-3: 0.75rem;     /* 12px */
--sp-4: 1rem;        /* 16px */
--sp-5: 1.25rem;     /* 20px */
--sp-6: 1.5rem;      /* 24px */
--sp-8: 2rem;        /* 32px */
--sp-10: 2.5rem;     /* 40px */
--sp-12: 3rem;       /* 48px */
--sp-16: 4rem;       /* 64px */
--sp-20: 5rem;       /* 80px */
--sp-24: 6rem;       /* 96px */
```

## 🔄 Border Radius

```css
--radius-none: 0;
--radius-sm: 0.125rem;   /* 2px */
--radius-base: 0.25rem;  /* 4px */
--radius-md: 0.375rem;   /* 6px */
--radius-lg: 0.5rem;     /* 8px */
--radius-xl: 0.75rem;    /* 12px */
--radius-2xl: 1rem;      /* 16px */
--radius-3xl: 1.5rem;    /* 24px */
--radius-full: 9999px;
```

## 🌫️ Shadows

### Базовые
```css
--shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
--shadow-base: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
```

### Специальные
```css
--shadow-card: 0 8px 24px rgba(15, 23, 42, 0.06);
--shadow-modal: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
--shadow-dropdown: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
```

## 📐 Z-Index

```css
--z-0: 0;
--z-10: 10;
--z-20: 20;
--z-30: 30;
--z-40: 40;
--z-50: 50;
--z-dropdown: 1000;
--z-sticky: 1020;
--z-fixed: 1030;
--z-modal-backdrop: 1040;
--z-modal: 1050;
--z-popover: 1060;
--z-skiplink: 1070;
--z-toast: 1080;
--z-tooltip: 1090;
```

## ⚡ Transitions

### Длительность
```css
--duration-75: 75ms;
--duration-100: 100ms;
--duration-150: 150ms;
--duration-200: 200ms;
--duration-300: 300ms;
--duration-500: 500ms;
--duration-700: 700ms;
--duration-1000: 1000ms;
```

### Easing
```css
--ease-linear: linear;
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
--ease-soft: cubic-bezier(0.22, 1, 0.36, 1);
```

### Готовые переходы
```css
--transition-all: all 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-colors: color 150ms cubic-bezier(0.4, 0, 0.2, 1), background-color 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-transform: transform 150ms cubic-bezier(0.4, 0, 0.2, 1);
```

## 📱 Breakpoints

```css
--breakpoint-sm: 640px;
--breakpoint-md: 768px;
--breakpoint-lg: 1024px;
--breakpoint-xl: 1280px;
--breakpoint-2xl: 1536px;
```

## 🌙 Dark Mode

### Автоматическое переключение
```css
:root[data-theme="dark"] {
  --color-bg: var(--color-gray-950);
  --color-text: var(--color-gray-100);
  /* ... остальные переопределения */
}
```

### Системные предпочтения
```css
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    /* Автоматическое переключение */
  }
}
```

### Управление темой
```javascript
// Переключение темы
document.documentElement.setAttribute('data-theme', 'dark');
document.documentElement.setAttribute('data-theme', 'light');
document.documentElement.setAttribute('data-theme', 'auto');
```

## 🎯 Использование

### В CSS
```css
.my-component {
  background: var(--color-bg-elevated);
  color: var(--color-text);
  padding: var(--sp-4);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: var(--transition-colors);
}
```

### В JavaScript
```javascript
// Получение значения токена
const primaryColor = getComputedStyle(document.documentElement)
  .getPropertyValue('--color-primary');

// Установка значения токена
document.documentElement.style.setProperty('--color-primary', '#ff0000');
```

### С Tailwind CSS
```css
/* В tailwind.config.js */
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'var(--color-primary-50)',
          500: 'var(--color-primary-500)',
          600: 'var(--color-primary-600)',
        }
      }
    }
  }
}
```

## ✅ Best Practices

1. **Используйте семантические токены** вместо прямых значений
2. **Следуйте иерархии** токенов (50-950 для цветов)
3. **Тестируйте в обеих темах** (light/dark)
4. **Уважайте prefers-reduced-motion** для анимаций
5. **Документируйте кастомные токены** при добавлении

## 🔄 Миграция

При переходе со старых токенов:

1. Замените `--color-primary` на `--color-primary-600`
2. Используйте `--color-bg` вместо `--color-bg-primary`
3. Примените новые spacing токены `--sp-*`
4. Обновите shadow токены на новые значения

---
*Документация обновлена: 2025-10-06*
