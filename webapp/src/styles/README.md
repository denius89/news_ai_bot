# Система стилей PulseAI

Централизованная система стилей с адаптивными размерами для разных устройств.

## Breakpoints

| Breakpoint | Размер | Устройства |
|------------|--------|------------|
| `xs:` | 390px | iPhone 15 Pro и меньше |
| `sm:` | 640px | Desktop, большие телефоны |
| `md:` | 768px | Планшеты |
| `lg:` | 1024px | Desktop |
| `xl:` | 1280px | Большие экраны |
| `2xl:` | 1400px | Очень большие экраны |

## Именованные размеры шрифтов

| Класс | Размер | Использование |
|-------|--------|---------------|
| `text-xxs` | 10px (0.625rem) | Очень мелкие элементы |
| `text-xxxs` | 11px (0.6875rem) | Метаданные, вспомогательный текст |
| `text-xs` | 12px (0.75rem) | Стандартный мелкий текст |
| `text-sm` | 14px (0.875rem) | Основной текст на mobile |
| `text-base` | 16px (1rem) | Основной текст на desktop |
| `text-lg` | 18px (1.125rem) | Заголовки |

## Семантические классы карточек

### Типографика

```css
.card-title        /* Заголовок карточки */
.card-badge        /* Бейджи (importance, credibility) */
.card-meta         /* Метаданные (источник, дата, организатор) */
.card-description  /* Основной текст/описание */
.card-footer       /* Футер (звёзды, категория, кнопки) */
```

### Иконки

```css
.card-icon-sm      /* Маленькие иконки (2px → 2.5px → 3px) */
.card-icon-md      /* Средние иконки (3px → 3.5px → 4px) */
```

## Примеры использования

### Карточка новости

```tsx
<div className="card p-3 sm:p-4">
    <h3 className="card-title text-text dark:text-white">
        Заголовок новости
    </h3>

    <span className="card-badge bg-green-50 text-green-600 px-2 py-0.5 rounded-full">
        85%
    </span>

    <p className="card-meta text-gray-500">
        Bloomberg • 26.10.2025
    </p>

    <p className="card-description text-text/90">
        Описание новости...
    </p>

    <div className="card-footer">
        <button className="text-primary">
            Читать полностью
            <ExternalLink className="card-icon-sm" />
        </button>
    </div>
</div>
```

### Адаптивные размеры

Все семантические классы автоматически адаптируются под размер экрана:

- **<390px:** Самые компактные размеры
- **390-640px:** Промежуточные размеры (оптимально для iPhone)
- **≥640px:** Полные размеры (desktop)

## Как добавить новый семантический класс

1. Откройте `webapp/src/styles/cards.css`
2. Добавьте класс в `@layer components`:

```css
@layer components {
    .my-new-class {
        @apply text-xxxs xs:text-xs sm:text-sm;
    }
}
```

3. Пересоберите проект:

```bash
cd webapp && npm run build
```

## Структура файлов стилей

```
webapp/src/styles/
├── index.css           # Главный файл, импортирует все остальные
├── design-tokens.css   # CSS переменные (цвета, тени)
├── base.css           # Базовые стили (body, typography)
├── components.css     # Компоненты (.card, .btn, .input)
├── utilities.css      # Утилиты (.interactive, .safe-bottom)
├── cards.css          # Семантические классы карточек
└── README.md          # Эта документация
```

## Лучшие практики

### ✅ Хорошо

```tsx
// Используем семантические классы
<h3 className="card-title text-text">Заголовок</h3>

// Используем именованные размеры
<span className="text-xxxs">Метаданные</span>

// Адаптивные размеры через breakpoints
<div className="px-3 xs:px-4 sm:px-6">...</div>
```

### ❌ Плохо

```tsx
// Избегаем inline размеров
<h3 className="text-[14px]">Заголовок</h3>

// Избегаем дублирования стилей
<h3 className="text-xs xs:text-sm sm:text-base font-semibold leading-snug">
    Заголовок
</h3>
```

## Производительность

- **Tailwind JIT:** Генерирует только используемые классы
- **PurgeCSS:** Автоматически удаляет неиспользуемые стили в production
- **Размер бандла:** ~75KB (gzipped ~13KB)

## Проверка размера бандла

```bash
# После сборки
ls -lh webapp/dist/css/main-*.css

# Должно быть примерно:
# main-*.css  75.45 kB │ gzip: 13.18 kB
```

## Дальнейшее развитие

Планируемые улучшения:
- Добавить классы для кнопок (`.btn-text-sm`, `.btn-text-base`)
- Добавить классы для форм (`.input-text`, `.label-text`)
- Расширить систему иконок (`.icon-xs`, `.icon-sm`, `.icon-md`, `.icon-lg`)
- Добавить классы для навигации (`.nav-text`)

---

**Версия:** 1.0
**Последнее обновление:** 26.10.2025
