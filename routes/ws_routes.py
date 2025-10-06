"""
WebSocket маршруты для Reactor Core.
Обеспечивает real-time передачу событий между сервером и клиентами.
"""

import asyncio
import json
import logging
from typing import Set
from flask import Blueprint, request
from flask_socketio import SocketIO, emit as socket_emit, join_room, leave_room

from core.reactor import reactor, Events

logger = logging.getLogger(__name__)

# Blueprint для WebSocket маршрутов
ws_bp = Blueprint('ws', __name__, url_prefix='/ws')

# Глобальный экземпляр SocketIO (будет инициализирован в webapp.py)
socketio: SocketIO = None

# Множество подключенных клиентов
connected_clients: Set[str] = set()


def init_socketio(app, **kwargs):
    """Инициализация SocketIO для Flask приложения."""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", **kwargs)
    
    # Регистрируем обработчики WebSocket событий
    register_websocket_handlers()
    
    # Подписываемся на события Reactor для передачи клиентам
    reactor.on(Events.AI_METRICS_UPDATED, handle_reactor_event)
    reactor.on(Events.NEWS_PROCESSED, handle_reactor_event)
    reactor.on(Events.DIGEST_CREATED, handle_reactor_event)
    reactor.on(Events.EVENT_DETECTED, handle_reactor_event)
    reactor.on(Events.USER_ACTION, handle_reactor_event)
    reactor.on(Events.SYSTEM_HEALTH_CHECK, handle_reactor_event)
    reactor.on(Events.REACTOR_HEARTBEAT, handle_reactor_event)
    
    logger.info("WebSocket Hub инициализирован")


def register_websocket_handlers():
    """Регистрация обработчиков WebSocket событий."""
    
    @socketio.on('connect')
    def handle_connect():
        """Обработка подключения клиента."""
        client_id = request.sid
        connected_clients.add(client_id)
        
        logger.info(f"Клиент подключился: {client_id}")
        logger.info(f"Всего подключенных клиентов: {len(connected_clients)}")
        
        # Уведомляем о подключении
        reactor.emit_sync(Events.WEBSOCKET_CONNECTED, client_id=client_id)
        
        # Отправляем приветственное сообщение
        socket_emit('reactor_connected', {
            'message': 'Подключен к PulseAI Reactor',
            'client_id': client_id,
            'timestamp': asyncio.get_event_loop().time()
        })
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Обработка отключения клиента."""
        client_id = request.sid
        connected_clients.discard(client_id)
        
        logger.info(f"Клиент отключился: {client_id}")
        logger.info(f"Всего подключенных клиентов: {len(connected_clients)}")
        
        # Уведомляем об отключении
        reactor.emit_sync(Events.WEBSOCKET_DISCONNECTED, client_id=client_id)
    
    @socketio.on('join_room')
    def handle_join_room(data):
        """Подключение клиента к комнате."""
        room = data.get('room', 'default')
        join_room(room)
        
        client_id = request.sid
        logger.info(f"Клиент {client_id} подключился к комнате '{room}'")
        
        socket_emit('room_joined', {
            'room': room,
            'message': f'Подключен к комнате {room}'
        }, room=room)
    
    @socketio.on('leave_room')
    def handle_leave_room(data):
        """Отключение клиента от комнаты."""
        room = data.get('room', 'default')
        leave_room(room)
        
        client_id = request.sid
        logger.info(f"Клиент {client_id} отключился от комнаты '{room}'")
    
    @socketio.on('reactor_subscribe')
    def handle_reactor_subscribe(data):
        """Подписка клиента на определенные события."""
        events = data.get('events', [])
        client_id = request.sid
        
        logger.info(f"Клиент {client_id} подписался на события: {events}")
        
        socket_emit('reactor_subscribed', {
            'events': events,
            'message': f'Подписка на события {events} активирована'
        })
    
    @socketio.on('reactor_unsubscribe')
    def handle_reactor_unsubscribe(data):
        """Отписка клиента от событий."""
        events = data.get('events', [])
        client_id = request.sid
        
        logger.info(f"Клиент {client_id} отписался от событий: {events}")
        
        socket_emit('reactor_unsubscribed', {
            'events': events,
            'message': f'Отписка от событий {events} выполнена'
        })
    
    @socketio.on('ping')
    def handle_ping():
        """Обработка ping от клиента."""
        client_id = request.sid
        socket_emit('pong', {'timestamp': asyncio.get_event_loop().time()})


def handle_reactor_event(event):
    """Обработчик событий Reactor для передачи клиентам через WebSocket."""
    if not socketio:
        return
    
    try:
        # Преобразуем событие в формат для WebSocket
        event_data = {
            'event': event.name,
            'data': event.data,
            'source': event.source,
            'timestamp': event.timestamp.isoformat(),
            'id': event.id
        }
        
        # Отправляем событие всем подключенным клиентам
        socketio.emit('reactor_event', event_data, namespace='/')
        
        # Логируем отправку события
        logger.debug(f"Событие '{event.name}' отправлено {len(connected_clients)} клиентам")
        
    except Exception as e:
        logger.error(f"Ошибка при отправке события через WebSocket: {e}")


def broadcast_event(event_name: str, data: dict, room: str = None):
    """Прямая отправка события всем клиентам или в конкретную комнату."""
    if not socketio:
        logger.warning("SocketIO не инициализирован")
        return
    
    event_data = {
        'event': event_name,
        'data': data,
        'timestamp': asyncio.get_event_loop().time(),
        'type': 'broadcast'
    }
    
    if room:
        socketio.emit('reactor_event', event_data, room=room)
        logger.info(f"Событие '{event_name}' отправлено в комнату '{room}'")
    else:
        socketio.emit('reactor_event', event_data)
        logger.info(f"Событие '{event_name}' отправлено всем клиентам ({len(connected_clients)})")


def get_connected_clients_count() -> int:
    """Получение количества подключенных клиентов."""
    return len(connected_clients)


def get_websocket_stats() -> dict:
    """Получение статистики WebSocket подключений."""
    return {
        'connected_clients': len(connected_clients),
        'socketio_initialized': socketio is not None,
        'reactor_events_subscribed': len([
            Events.AI_METRICS_UPDATED,
            Events.NEWS_PROCESSED,
            Events.DIGEST_CREATED,
            Events.EVENT_DETECTED,
            Events.USER_ACTION,
            Events.SYSTEM_HEALTH_CHECK,
            Events.REACTOR_HEARTBEAT
        ])
    }


# Маршрут для проверки статуса WebSocket
@ws_bp.route('/status')
def websocket_status():
    """Эндпоинт для проверки статуса WebSocket Hub."""
    from flask import jsonify
    
    return jsonify({
        'status': 'active',
        'connected_clients': len(connected_clients),
        'socketio_initialized': socketio is not None,
        'reactor_events': [
            Events.AI_METRICS_UPDATED,
            Events.NEWS_PROCESSED,
            Events.DIGEST_CREATED,
            Events.EVENT_DETECTED,
            Events.USER_ACTION,
            Events.SYSTEM_HEALTH_CHECK,
            Events.REACTOR_HEARTBEAT
        ]
    })


# Маршрут для получения статистики
@ws_bp.route('/stats')
def websocket_stats():
    """Эндпоинт для получения статистики WebSocket."""
    from flask import jsonify
    
    return jsonify(get_websocket_stats())
