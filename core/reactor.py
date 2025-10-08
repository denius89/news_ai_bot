"""
Reactor Core - асинхронный event bus для PulseAI.
Обеспечивает реактивную архитектуру с событиями и WebSocket интеграцией.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ReactorEvent:
    """Событие Reactor с метаданными."""

    def __init__(self, name: str, data: Dict[str, Any], source: str = "system"):
        self.name = name
        self.data = data
        self.source = source
        self.timestamp = datetime.utcnow()
        self.id = f"{self.timestamp.isoformat()}_{self.name}_{id(self)}"

    def to_dict(self) -> Dict[str, Any]:
        """Преобразование события в словарь для JSON сериализации."""
        return {
            "id": self.id,
            "name": self.name,
            "data": self.data,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
        }


class ReactorCore:
    """
    Асинхронный event bus для реактивной архитектуры PulseAI.

    Основные возможности:
    - Подписка на события через on(event_name, callback)
    - Эмиссия событий через emit(event_name, **data)
    - Логирование всех событий в logs/reactor.log
    - Метрики и статистика событий
    """

    def __init__(self, log_file: Optional[str] = None):
        self._listeners: Dict[str, List[Callable]] = {}
        self._metrics: Dict[str, int] = {}
        self._log_file = log_file or "logs/reactor.log"
        self._setup_logging()

        # Запускаем фоновую задачу для периодических событий
        self._background_task = None
        self._running = False

    def _setup_logging(self):
        """Настройка логирования Reactor."""
        reactor_logger = logging.getLogger("reactor")
        reactor_logger.setLevel(logging.INFO)

        # Создаем директорию logs если её нет
        log_path = Path(self._log_file)
        log_path.parent.mkdir(exist_ok=True)

        # Файловый хендлер для Reactor
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        file_handler.setFormatter(formatter)

        reactor_logger.addHandler(file_handler)
        self._logger = reactor_logger

    def on(self, event_name: str, callback: Callable[[ReactorEvent], None]):
        """
        Подписка на событие.

        Args:
            event_name: Название события для подписки
            callback: Функция-обработчик события
        """
        if event_name not in self._listeners:
            self._listeners[event_name] = []

        self._listeners[event_name].append(callback)
        logger.debug(f"Подписка на событие '{event_name}' добавлена")

    def off(self, event_name: str, callback: Callable[[ReactorEvent], None]):
        """
        Отписка от события.

        Args:
            event_name: Название события
            callback: Функция-обработчик для удаления
        """
        if event_name in self._listeners:
            try:
                self._listeners[event_name].remove(callback)
                logger.debug(f"Подписка на событие '{event_name}' удалена")
            except ValueError:
                logger.warning(f"Попытка удалить несуществующую подписку на '{event_name}'")

    async def emit(self, event_name: str, **data) -> ReactorEvent:
        """
        Эмиссия события.

        Args:
            event_name: Название события
            **data: Данные события

        Returns:
            ReactorEvent: Созданное событие
        """
        event = ReactorEvent(event_name, data)

        # Обновляем метрики
        self._metrics[event_name] = self._metrics.get(event_name, 0) + 1

        # Логируем событие
        self._logger.info(f"EMIT: {event_name} | {json.dumps(data, ensure_ascii=False)}")

        # Уведомляем всех подписчиков
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"Ошибка в обработчике события '{event_name}': {e}")

        # PULSE-WS: WebSocket broadcast removed - not used in Flask app
        # WebSocket functionality was removed as it's not used in production

        return event

    def emit_sync(self, event_name: str, **data) -> ReactorEvent:
        """
        Синхронная эмиссия события (для использования в синхронном коде).

        Args:
            event_name: Название события
            **data: Данные события

        Returns:
            ReactorEvent: Созданное событие
        """
        event = ReactorEvent(event_name, data)

        # Обновляем метрики
        self._metrics[event_name] = self._metrics.get(event_name, 0) + 1

        # Логируем событие
        self._logger.info(f"EMIT_SYNC: {event_name} | {json.dumps(data, ensure_ascii=False)}")

        # Уведомляем всех подписчиков (только синхронные)
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                try:
                    if not asyncio.iscoroutinefunction(callback):
                        callback(event)
                except Exception as e:
                    logger.error(f"Ошибка в синхронном обработчике события '{event_name}': {e}")

        # PULSE-WS: WebSocket broadcast removed - not used in Flask app
        # WebSocket functionality was removed as it's not used in production

        return event

    def get_metrics(self) -> Dict[str, Any]:
        """Получение метрик Reactor."""
        return {
            "events_emitted": sum(
                self._metrics.values()),
            "event_types": len(
                self._metrics),
            "listeners_count": sum(
                len(listeners) for listeners in self._listeners.values()),
            "event_breakdown": self._metrics.copy(),
            "listeners_breakdown": {
                name: len(listeners) for name,
                listeners in self._listeners.items()},
        }

    def get_health(self) -> Dict[str, Any]:
        """Получение статуса здоровья Reactor."""
        return {
            "status": "healthy" if self._running else "stopped",
            "listeners": len(self._listeners),
            "events_emitted": sum(self._metrics.values()),
            "log_file": self._log_file,
            "uptime": "N/A",  # TODO: добавить отслеживание времени работы
        }

    async def start(self):
        """Запуск фоновых задач Reactor."""
        self._running = True
        self._background_task = asyncio.create_task(self._background_loop())
        logger.info("Reactor Core запущен")

    async def stop(self):
        """Остановка Reactor."""
        self._running = False
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
        logger.info("Reactor Core остановлен")

    async def _background_loop(self):
        """Фоновая задача для периодических событий."""
        while self._running:
            try:
                # Эмитируем heartbeat каждые 30 секунд
                await self.emit("reactor_heartbeat", timestamp=datetime.utcnow().isoformat())
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в фоновой задаче Reactor: {e}")
                await asyncio.sleep(5)


# Глобальный экземпляр Reactor
reactor = ReactorCore()


# Удобные функции для использования в модулях
def on(event_name: str, callback: Callable[[ReactorEvent], None]):
    """Подписка на событие через глобальный reactor."""
    reactor.on(event_name, callback)


def emit(event_name: str, **data) -> ReactorEvent:
    """Синхронная эмиссия события через глобальный reactor."""
    return reactor.emit_sync(event_name, **data)


async def emit_async(event_name: str, **data) -> ReactorEvent:
    """Асинхронная эмиссия события через глобальный reactor."""
    return await reactor.emit(event_name, **data)


# Предопределенные события PulseAI
class Events:
    """Константы для событий PulseAI."""

    # AI события
    AI_METRICS_UPDATED = "ai_metrics_updated"
    AI_PREDICTION_COMPLETED = "ai_prediction_completed"
    AI_MODEL_TRAINED = "ai_model_trained"

    # Новости и контент
    NEWS_PROCESSED = "news_processed"
    NEWS_REJECTED = "news_rejected"
    NEWS_ACCEPTED = "news_accepted"

    # Дайджесты
    DIGEST_CREATED = "digest_created"
    DIGEST_PUBLISHED = "digest_published"

    # События
    EVENT_DETECTED = "event_detected"
    EVENT_FORECAST = "event_forecast"

    # Пользователи
    USER_ACTION = "user_action"
    USER_FEEDBACK = "user_feedback"

    # Система
    SYSTEM_HEALTH_CHECK = "system_health_check"
    REACTOR_HEARTBEAT = "reactor_heartbeat"
    WEBSOCKET_CONNECTED = "websocket_connected"
    WEBSOCKET_DISCONNECTED = "websocket_disconnected"
