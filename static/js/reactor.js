/**
 * PulseAI Reactor Client - фронтенд клиент для подключения к Reactor Core
 * Обеспечивает real-time связь с сервером через WebSocket
 */

class PulseAIReactor {
    constructor(options = {}) {
        this.options = {
            wsUrl: options.wsUrl || this.getWebSocketUrl(),
            reconnectInterval: options.reconnectInterval || 5000,
            maxReconnectAttempts: options.maxReconnectAttempts || 10,
            debug: options.debug || false,
            ...options
        };
        
        this.socket = null;
        this.connected = false;
        this.reconnectAttempts = 0;
        this.eventListeners = new Map();
        this.subscribedEvents = new Set();
        
        this.log('PulseAI Reactor Client инициализирован', this.options);
    }
    
    getWebSocketUrl() {
        // Определяем URL для WebSocket подключения
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        return `${protocol}//${host}/socket.io/?EIO=4&transport=websocket`;
    }
    
    log(message, data = null) {
        if (this.options.debug) {
            console.log(`[PulseAI Reactor] ${message}`, data);
        }
    }
    
    error(message, error = null) {
        console.error(`[PulseAI Reactor] ${message}`, error);
    }
    
    connect() {
        return new Promise((resolve, reject) => {
            try {
                this.log('Подключение к Reactor WebSocket...');
                
                // Импортируем socket.io-client динамически
                if (typeof io === 'undefined') {
                    this.loadSocketIO().then(() => {
                        this.initSocket(resolve, reject);
                    }).catch(reject);
                } else {
                    this.initSocket(resolve, reject);
                }
                
            } catch (error) {
                this.error('Ошибка при подключении', error);
                reject(error);
            }
        });
    }
    
    loadSocketIO() {
        return new Promise((resolve, reject) => {
            if (document.querySelector('script[src*="socket.io"]')) {
                resolve();
                return;
            }
            
            const script = document.createElement('script');
            // Используем CDN для совместимости с Flask-SocketIO 5.5.1
            script.src = 'https://cdn.socket.io/4.7.5/socket.io.min.js';
            script.onload = () => {
                this.log('Socket.IO клиент загружен с CDN');
                resolve();
            };
            script.onerror = () => {
                this.error('Ошибка загрузки Socket.IO клиента');
                reject(new Error('Не удалось загрузить socket.io'));
            };
            document.head.appendChild(script);
        });
    }
    
    initSocket(resolve, reject) {
        try {
            this.socket = io();
            
            this.socket.on('connect', () => {
                this.connected = true;
                this.reconnectAttempts = 0;
                this.log('Подключен к Reactor WebSocket');
                
                // Уведомляем о подключении
                this.emit('reactor_connected', { timestamp: Date.now() });
                
                // Переподписываемся на события
                if (this.subscribedEvents.size > 0) {
                    this.socket.emit('reactor_subscribe', {
                        events: Array.from(this.subscribedEvents)
                    });
                }
                
                resolve();
            });
            
            this.socket.on('disconnect', (reason) => {
                this.connected = false;
                this.log('Отключен от Reactor WebSocket', reason);
                
                this.emit('reactor_disconnected', { reason, timestamp: Date.now() });
                
                // Автоматическое переподключение
                if (this.reconnectAttempts < this.options.maxReconnectAttempts) {
                    setTimeout(() => this.reconnect(), this.options.reconnectInterval);
                }
            });
            
            this.socket.on('reactor_event', (data) => {
                this.log('Получено событие от Reactor', data);
                this.handleReactorEvent(data);
            });
            
            this.socket.on('reactor_connected', (data) => {
                this.log('Reactor подтвердил подключение', data);
            });
            
            this.socket.on('reactor_subscribed', (data) => {
                this.log('Подписка подтверждена', data);
            });
            
            this.socket.on('reactor_unsubscribed', (data) => {
                this.log('Отписка подтверждена', data);
            });
            
            this.socket.on('pong', (data) => {
                this.log('Pong получен', data);
            });
            
            this.socket.on('connect_error', (error) => {
                this.error('Ошибка подключения', error);
                reject(error);
            });
            
        } catch (error) {
            this.error('Ошибка инициализации socket', error);
            reject(error);
        }
    }
    
    reconnect() {
        this.reconnectAttempts++;
        this.log(`Попытка переподключения ${this.reconnectAttempts}/${this.options.maxReconnectAttempts}`);
        
        if (this.socket) {
            this.socket.disconnect();
        }
        
        this.connect().catch((error) => {
            this.error('Ошибка переподключения', error);
        });
    }
    
    handleReactorEvent(eventData) {
        const { event, data, source, timestamp, id } = eventData;
        
        // Создаем кастомное событие для браузера
        const customEvent = new CustomEvent(`reactor:${event}`, {
            detail: {
                event,
                data,
                source,
                timestamp,
                id,
                originalEvent: eventData
            }
        });
        
        // Диспетчим событие через window
        window.dispatchEvent(customEvent);
        
        // Также вызываем обработчики из Map
        const listeners = this.eventListeners.get(event) || [];
        listeners.forEach(callback => {
            try {
                callback(eventData);
            } catch (error) {
                this.error(`Ошибка в обработчике события ${event}`, error);
            }
        });
    }
    
    // Публичные методы для подписки на события
    
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
        
        // Подписываемся на сервере, если подключены
        if (this.connected && !this.subscribedEvents.has(event)) {
            this.subscribedEvents.add(event);
            this.socket.emit('reactor_subscribe', { events: [event] });
        }
        
        this.log(`Подписка на событие: ${event}`);
        return this;
    }
    
    off(event, callback) {
        const listeners = this.eventListeners.get(event);
        if (listeners) {
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
            
            // Если обработчиков больше нет, отписываемся от сервера
            if (listeners.length === 0) {
                this.eventListeners.delete(event);
                if (this.connected && this.subscribedEvents.has(event)) {
                    this.subscribedEvents.delete(event);
                    this.socket.emit('reactor_unsubscribe', { events: [event] });
                }
            }
        }
        
        this.log(`Отписка от события: ${event}`);
        return this;
    }
    
    emit(event, data) {
        // Эмитим событие в браузере
        const customEvent = new CustomEvent(event, { detail: data });
        window.dispatchEvent(customEvent);
        
        this.log(`Событие эмитировано: ${event}`, data);
        return this;
    }
    
    // Методы для работы с комнатами
    
    joinRoom(room) {
        if (this.connected) {
            this.socket.emit('join_room', { room });
            this.log(`Подключение к комнате: ${room}`);
        }
        return this;
    }
    
    leaveRoom(room) {
        if (this.connected) {
            this.socket.emit('leave_room', { room });
            this.log(`Отключение от комнаты: ${room}`);
        }
        return this;
    }
    
    // Ping/Pong для проверки соединения
    
    ping() {
        if (this.connected) {
            this.socket.emit('ping');
            this.log('Ping отправлен');
        }
        return this;
    }
    
    // Получение статуса
    
    getStatus() {
        return {
            connected: this.connected,
            reconnectAttempts: this.reconnectAttempts,
            subscribedEvents: Array.from(this.subscribedEvents),
            eventListeners: Array.from(this.eventListeners.keys()),
            wsUrl: this.options.wsUrl
        };
    }
    
    // Отключение
    
    disconnect() {
        if (this.socket) {
            this.socket.disconnect();
            this.socket = null;
        }
        this.connected = false;
        this.log('Отключен от Reactor');
        return this;
    }
}

// Создаем глобальный экземпляр
window.PulseAIReactor = PulseAIReactor;

// Автоматическая инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    // Создаем глобальный экземпляр Reactor
    window.reactor = new PulseAIReactor({
        debug: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    });
    
    // Автоматическое подключение
    window.reactor.connect().then(() => {
        console.log('PulseAI Reactor подключен');
    }).catch((error) => {
        console.error('Ошибка подключения к PulseAI Reactor:', error);
    });
    
    // Добавляем обработчики для глобальных событий
    window.reactor.on('ai_metrics_updated', (data) => {
        console.log('AI метрики обновлены:', data);
    });
    
    window.reactor.on('news_processed', (data) => {
        console.log('Новости обработаны:', data);
    });
    
    window.reactor.on('digest_created', (data) => {
        console.log('Дайджест создан:', data);
    });
});

// Экспорт для модульных систем
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PulseAIReactor;
}
