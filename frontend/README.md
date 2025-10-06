# PulseAI React Frontend

Современный React frontend для PulseAI с поддержкой Reactor WebSocket.

## Технологии

- **React 18** - UI библиотека
- **Tailwind CSS** - стилизация
- **Framer Motion** - анимации
- **Recharts** - графики и диаграммы
- **Socket.IO Client** - WebSocket подключение к Reactor
- **Vite** - сборка и разработка

## Установка

```bash
cd frontend
npm install
```

## Разработка

```bash
npm run dev
```

Frontend будет доступен на http://localhost:3000

## Сборка

```bash
npm run build
```

Собранные файлы будут в папке `dist/`

## Структура

```
src/
├── components/          # Переиспользуемые компоненты
│   ├── ReactorProvider.jsx  # WebSocket контекст
│   ├── Header.jsx           # Навигация
│   ├── MetricsCard.jsx      # Карточка метрик
│   ├── EventsFeed.jsx       # Лента событий
│   └── StatusIndicator.jsx  # Индикатор статуса
├── pages/               # Страницы приложения
│   ├── Dashboard.jsx        # Главная страница
│   └── LiveDashboard.jsx    # Live дашборд
├── App.jsx              # Главный компонент
├── main.jsx             # Точка входа
└── index.css            # Глобальные стили
```

## Reactor Integration

Frontend подключается к Reactor через WebSocket и получает события в реальном времени:

- `ai_metrics_updated` - обновления AI метрик
- `news_processed` - обработка новостей
- `digest_created` - создание дайджестов
- `event_detected` - обнаружение событий

## API

Frontend использует следующие API endpoints:

- `GET /api/metrics` - метрики системы
- `GET /api/health/reactor` - здоровье Reactor
- `WebSocket /ws/stream` - поток событий Reactor
