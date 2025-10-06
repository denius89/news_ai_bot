/**
 * PulseAI Reactor Hooks - обработчики событий для HTML элементов
 * Обеспечивает реактивное обновление UI при получении событий от Reactor
 */

class PulseAIReactorHooks {
    constructor(reactor) {
        this.reactor = reactor;
        this.hooks = new Map();
        this.initialized = false;
        
        this.init();
    }
    
    init() {
        if (this.initialized) return;
        
        this.registerDefaultHooks();
        this.setupEventListeners();
        this.initialized = true;
        
        console.log('PulseAI Reactor Hooks инициализированы');
    }
    
    registerDefaultHooks() {
        // Hook для обновления метрик AI
        this.registerHook('ai_metrics_updated', (data) => {
            this.updateMetricsDisplay(data.data);
            this.animateMetricsUpdate();
        });
        
        // Hook для обработки новостей
        this.registerHook('news_processed', (data) => {
            this.updateNewsCounter(data.data);
            this.showNewsNotification(data.data);
        });
        
        // Hook для дайджестов
        this.registerHook('digest_created', (data) => {
            this.updateDigestStatus(data.data);
            this.showDigestNotification(data.data);
        });
        
        // Hook для событий
        this.registerHook('event_detected', (data) => {
            this.updateEventsDisplay(data.data);
            this.highlightEvent(data.data);
        });
        
        // Hook для пользовательских действий
        this.registerHook('user_action', (data) => {
            this.trackUserAction(data.data);
        });
        
        // Hook для системного здоровья
        this.registerHook('system_health_check', (data) => {
            this.updateSystemStatus(data.data);
        });
        
        // Hook для heartbeat
        this.registerHook('reactor_heartbeat', (data) => {
            this.updateConnectionStatus(true);
        });
        
        // Hook для отключения
        this.registerHook('reactor_disconnected', (data) => {
            this.updateConnectionStatus(false);
        });
    }
    
    registerHook(eventName, callback) {
        if (!this.hooks.has(eventName)) {
            this.hooks.set(eventName, []);
        }
        this.hooks.get(eventName).push(callback);
        
        // Подписываемся на событие в Reactor
        this.reactor.on(eventName, callback);
        
        console.log(`Hook зарегистрирован: ${eventName}`);
    }
    
    setupEventListeners() {
        // Слушаем глобальные события браузера
        window.addEventListener('reactor:ai_metrics_updated', (event) => {
            this.handleGlobalEvent('ai_metrics_updated', event.detail);
        });
        
        window.addEventListener('reactor:news_processed', (event) => {
            this.handleGlobalEvent('news_processed', event.detail);
        });
        
        window.addEventListener('reactor:digest_created', (event) => {
            this.handleGlobalEvent('digest_created', event.detail);
        });
        
        window.addEventListener('reactor:event_detected', (event) => {
            this.handleGlobalEvent('event_detected', event.detail);
        });
        
        window.addEventListener('reactor:user_action', (event) => {
            this.handleGlobalEvent('user_action', event.detail);
        });
        
        window.addEventListener('reactor:system_health_check', (event) => {
            this.handleGlobalEvent('system_health_check', event.detail);
        });
        
        window.addEventListener('reactor:reactor_heartbeat', (event) => {
            this.handleGlobalEvent('reactor_heartbeat', event.detail);
        });
    }
    
    handleGlobalEvent(eventName, eventDetail) {
        const hooks = this.hooks.get(eventName) || [];
        hooks.forEach(hook => {
            try {
                hook(eventDetail);
            } catch (error) {
                console.error(`Ошибка в hook для события ${eventName}:`, error);
            }
        });
    }
    
    // Методы для обновления UI элементов
    
    updateMetricsDisplay(data) {
        // Обновляем отображение метрик AI
        const elements = document.querySelectorAll('[data-reactor="metrics"]');
        elements.forEach(element => {
            if (data.credibility !== undefined) {
                const credibilityEl = element.querySelector('[data-metric="credibility"]');
                if (credibilityEl) {
                    credibilityEl.textContent = (data.credibility * 100).toFixed(1) + '%';
                }
            }
            
            if (data.importance !== undefined) {
                const importanceEl = element.querySelector('[data-metric="importance"]');
                if (importanceEl) {
                    importanceEl.textContent = (data.importance * 100).toFixed(1) + '%';
                }
            }
            
            if (data.timestamp) {
                const timestampEl = element.querySelector('[data-metric="timestamp"]');
                if (timestampEl) {
                    timestampEl.textContent = new Date(data.timestamp).toLocaleTimeString();
                }
            }
        });
    }
    
    animateMetricsUpdate() {
        // Анимация обновления метрик
        const elements = document.querySelectorAll('[data-reactor="metrics"]');
        elements.forEach(element => {
            element.classList.add('metrics-updated');
            setTimeout(() => {
                element.classList.remove('metrics-updated');
            }, 1000);
        });
    }
    
    updateNewsCounter(data) {
        // Обновляем счетчик новостей
        const counters = document.querySelectorAll('[data-reactor="news-counter"]');
        counters.forEach(counter => {
            const currentCount = parseInt(counter.textContent) || 0;
            counter.textContent = currentCount + (data.count || 1);
            
            // Анимация
            counter.classList.add('counter-updated');
            setTimeout(() => {
                counter.classList.remove('counter-updated');
            }, 500);
        });
    }
    
    showNewsNotification(data) {
        // Показываем уведомление о новых новостях
        this.showNotification('Новые новости', `Обработано ${data.count || 1} новостей`, 'info');
    }
    
    updateDigestStatus(data) {
        // Обновляем статус дайджеста
        const digestElements = document.querySelectorAll('[data-reactor="digest-status"]');
        digestElements.forEach(element => {
            element.textContent = data.status || 'Готов';
            element.className = `digest-status ${data.status || 'ready'}`;
        });
    }
    
    showDigestNotification(data) {
        // Показываем уведомление о создании дайджеста
        this.showNotification('Дайджест создан', data.title || 'Новый дайджест готов', 'success');
    }
    
    updateEventsDisplay(data) {
        // Обновляем отображение событий
        const eventsContainer = document.querySelector('[data-reactor="events-container"]');
        if (eventsContainer && data.events) {
            // Добавляем новые события в контейнер
            data.events.forEach(event => {
                const eventElement = this.createEventElement(event);
                eventsContainer.insertBefore(eventElement, eventsContainer.firstChild);
                
                // Ограничиваем количество отображаемых событий
                const maxEvents = 10;
                const events = eventsContainer.querySelectorAll('.event-item');
                if (events.length > maxEvents) {
                    events[events.length - 1].remove();
                }
            });
        }
    }
    
    createEventElement(event) {
        const element = document.createElement('div');
        element.className = 'event-item';
        element.innerHTML = `
            <div class="event-title">${event.title || 'Событие'}</div>
            <div class="event-time">${new Date(event.timestamp).toLocaleTimeString()}</div>
        `;
        return element;
    }
    
    highlightEvent(data) {
        // Подсвечиваем событие
        const eventElements = document.querySelectorAll('[data-event-id]');
        eventElements.forEach(element => {
            if (element.dataset.eventId === data.id) {
                element.classList.add('event-highlighted');
                setTimeout(() => {
                    element.classList.remove('event-highlighted');
                }, 3000);
            }
        });
    }
    
    trackUserAction(data) {
        // Отслеживаем действия пользователя
        console.log('Пользовательское действие:', data);
        
        // Можно добавить аналитику или другие действия
        if (data.action === 'click') {
            // Отслеживание кликов
        } else if (data.action === 'scroll') {
            // Отслеживание скролла
        }
    }
    
    updateSystemStatus(data) {
        // Обновляем статус системы
        const statusElements = document.querySelectorAll('[data-reactor="system-status"]');
        statusElements.forEach(element => {
            element.textContent = data.status || 'OK';
            element.className = `system-status ${data.status || 'ok'}`;
        });
    }
    
    updateConnectionStatus(connected) {
        // Обновляем статус подключения
        const connectionElements = document.querySelectorAll('[data-reactor="connection-status"]');
        connectionElements.forEach(element => {
            element.textContent = connected ? 'Подключено' : 'Отключено';
            element.className = `connection-status ${connected ? 'connected' : 'disconnected'}`;
        });
        
        // Показываем уведомление об изменении статуса
        if (connected) {
            this.showNotification('Подключение', 'Соединение с PulseAI Reactor восстановлено', 'success');
        } else {
            this.showNotification('Отключение', 'Соединение с PulseAI Reactor потеряно', 'warning');
        }
    }
    
    showNotification(title, message, type = 'info') {
        // Создаем уведомление
        const notification = document.createElement('div');
        notification.className = `reactor-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
            <button class="notification-close">&times;</button>
        `;
        
        // Добавляем в контейнер уведомлений
        let container = document.querySelector('.reactor-notifications');
        if (!container) {
            container = document.createElement('div');
            container.className = 'reactor-notifications';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Автоматическое удаление через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
        
        // Обработчик закрытия
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });
    }
    
    // Методы для работы с элементами
    
    findElement(selector) {
        return document.querySelector(selector);
    }
    
    findElements(selector) {
        return document.querySelectorAll(selector);
    }
    
    updateElement(element, content) {
        if (typeof element === 'string') {
            element = this.findElement(element);
        }
        if (element) {
            element.innerHTML = content;
        }
    }
    
    addClass(element, className) {
        if (typeof element === 'string') {
            element = this.findElement(element);
        }
        if (element) {
            element.classList.add(className);
        }
    }
    
    removeClass(element, className) {
        if (typeof element === 'string') {
            element = this.findElement(element);
        }
        if (element) {
            element.classList.remove(className);
        }
    }
    
    toggleClass(element, className) {
        if (typeof element === 'string') {
            element = this.findElement(element);
        }
        if (element) {
            element.classList.toggle(className);
        }
    }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
    // Ждем инициализации Reactor
    const initHooks = () => {
        if (window.reactor) {
            window.reactorHooks = new PulseAIReactorHooks(window.reactor);
        } else {
            setTimeout(initHooks, 100);
        }
    };
    
    initHooks();
});

// Экспорт для модульных систем
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PulseAIReactorHooks;
}
