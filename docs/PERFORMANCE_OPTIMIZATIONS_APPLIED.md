# Оптимизации производительности веб-приложения

**Дата:** 17 октября 2025  
**Проблема:** Телефон греется при использовании веб-приложения  
**Статус:** ✅ Исправлено

---

## 🔥 Проблемы которые были найдены

### 1. Избыточный polling (HomePage)
**До:** API запросы каждые 30 секунд  
**После:** API запросы каждые 5 минут (300 секунд)  
**Экономия:** 90% сокращение сетевых запросов  

```typescript
// Было:
const interval = setInterval(fetchDashboardStats, 30000); // 30s

// Стало:
const interval = setInterval(fetchDashboardStats, 300000); // 5min
```

---

### 2. Слишком частые scroll handlers
**До:** Throttle 100ms (10 раз в секунду)  
**После:** Throttle 300ms (3 раза в секунду)  
**Экономия:** 70% сокращение обработки событий скролла  

**Файлы:**
- `NewsPage.tsx` (2 обработчика)
- `EventsPage.tsx` (2 обработчика)

```typescript
// Было:
timeoutId = setTimeout(handleScroll, 100);

// Стало:
timeoutId = setTimeout(handleScroll, 300);
```

---

### 3. Циклические зависимости в useEffect
**Проблема:** `fetchNews` в зависимостях → бесконечные перезагрузки  
**Решение:** Убран `fetchNews` из dependencies с явным комментарием  

```typescript
// Исправлено в NewsPage.tsx
useEffect(() => {
  if (isInitialized && categories.length > 0) {
    fetchNews(1);
  }
  // fetchNews убран из зависимостей чтобы избежать бесконечных циклов
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [selectedCategory, selectedSubcategory, isInitialized, categories.length]);
```

---

### 4. Избыточные Framer Motion анимации
**Проблема:** 
- `staggerChildren` для каждой карточки
- Анимации для каждого элемента списка
- Постоянные transform/scale при hover

**Решение:**
- Убран `staggerChildren` (экономит много CPU)
- Отключение анимаций на слабых устройствах
- Использование `useMemo` для variants

**Файлы:**
- `HomePage.tsx`
- `NewsPage.tsx`
- `App.tsx`

```typescript
// Добавлено определение производительности устройства
const reduceMotion = useMemo(() => shouldReduceMotion(), []);

const containerVariants = useMemo(() => {
  if (reduceMotion) {
    return { hidden: { opacity: 1 }, visible: { opacity: 1 } };
  }
  return {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { duration: 0.3 }
      // Убран staggerChildren
    }
  };
}, [reduceMotion]);
```

---

## 🛠️ Новые утилиты

### `/webapp/src/utils/performance.ts`

Утилиты для определения производительности устройства:

- **`isLowPerformanceDevice()`** - определяет слабое устройство по:
  - Доступной памяти (< 1GB heap)
  - Количеству ядер (≤ 2)
  - Типу соединения (2g, slow-2g)
  - User agent (старые Android/iOS)

- **`shouldReduceMotion()`** - проверяет:
  - Системные настройки `prefers-reduced-motion`
  - Производительность устройства

- **`getPerformanceLevel()`** - возвращает: `'low'` | `'medium'` | `'high'`

- **`logDevicePerformanceInfo()`** - логирует информацию об устройстве

---

## 📊 Результаты

### До оптимизации:
- ⚠️ Polling каждые 30 секунд
- ⚠️ Scroll events: 10/сек
- ⚠️ Анимации для каждой карточки с stagger
- ⚠️ Возможные бесконечные циклы обновлений

### После оптимизации:
- ✅ Polling каждые 5 минут (-90%)
- ✅ Scroll events: 3/сек (-70%)
- ✅ Анимации отключаются на слабых устройствах
- ✅ Исправлены циклические зависимости
- ✅ Мемоизация вариантов анимаций

---

## 🎯 Дальнейшие рекомендации

### Краткосрочные (1-2 недели):

1. **Виртуализация длинных списков**
   - Использовать `react-window` или `react-virtualized`
   - Рендерить только видимые элементы
   - Критично для NewsPage и EventsPage при >100 элементах

2. **Мемоизация компонентов**
   ```typescript
   const NewsCard = React.memo(({ item }) => {
     // ...
   }, (prev, next) => prev.item.id === next.item.id);
   ```

3. **Lazy loading изображений**
   - Добавить `loading="lazy"` для всех изображений
   - Использовать Intersection Observer

4. **Code splitting по страницам**
   ```typescript
   const NewsPage = lazy(() => import('./pages/NewsPage'));
   ```

### Среднесрочные (1 месяц):

1. **Service Worker для кэширования**
   - Кэшировать API ответы
   - Offline-first стратегия

2. **Оптимизация bundle size**
   - Проверить размер с `webpack-bundle-analyzer`
   - Tree-shaking неиспользуемого кода

3. **Debouncing для API запросов**
   - Использовать debounce для фильтров
   - Избегать множественных запросов

### Долгосрочные (2-3 месяца):

1. **Server-Side Rendering (SSR)**
   - Next.js или Remix
   - Быстрее первая загрузка

2. **Progressive Web App (PWA)**
   - Установка на устройство
   - Push notifications

3. **Мониторинг производительности**
   - Web Vitals
   - Real User Monitoring (RUM)

---

## 🧪 Как протестировать

### Chrome DevTools:

1. **Performance**:
   ```
   DevTools → Performance → Record
   → Взаимодействие с приложением
   → Stop → Анализ FPS, Long Tasks
   ```

2. **CPU Throttling**:
   ```
   DevTools → Performance → CPU: 4x slowdown
   → Проверить плавность
   ```

3. **Memory**:
   ```
   DevTools → Memory → Take Heap Snapshot
   → Проверить утечки памяти
   ```

### Lighthouse:

```bash
# В консоли DevTools
npx lighthouse http://localhost:5173 --view
```

Целевые метрики:
- Performance: >90
- FCP (First Contentful Paint): <1.8s
- LCP (Largest Contentful Paint): <2.5s
- TBT (Total Blocking Time): <200ms

---

## 📝 Checklist для будущих фич

При добавлении новых компонентов проверить:

- [ ] Нет ли избыточных re-renders?
- [ ] Используется ли `React.memo` для тяжелых компонентов?
- [ ] Есть ли `useMemo`/`useCallback` для дорогих вычислений?
- [ ] Анимации отключаются на слабых устройствах?
- [ ] Scroll handlers используют throttle/debounce?
- [ ] Нет циклических зависимостей в useEffect?
- [ ] Polling интервалы разумные (>1 минуты)?

---

## 🔗 Полезные ссылки

- [React Performance Optimization](https://react.dev/learn/render-and-commit)
- [Framer Motion Performance](https://www.framer.com/motion/guide-reduce-bundle-size/)
- [Web Vitals](https://web.dev/vitals/)
- [React DevTools Profiler](https://react.dev/learn/react-developer-tools)

---

**Автор:** Cursor AI  
**Последнее обновление:** 2025-10-17

