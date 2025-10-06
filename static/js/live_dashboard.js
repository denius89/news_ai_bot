/**
 * Live Dashboard JavaScript - вынесено из inline JS
 */

// Инициализация для live dashboard
function initPageReactor() {
    console.log('Инициализация Reactor для Live Dashboard');
    
    if (window.reactor) {
        // Подписываемся на все события для демонстрации
        window.reactor.on('ai_metrics_updated', function(data) {
            console.log('AI метрики обновлены:', data);
            addEventToFeed('AI метрики обновлены', 'success');
        });
        
        window.reactor.on('news_processed', function(data) {
            console.log('Новости обработаны:', data);
            document.getElementById('processing-time').textContent = data.processing_time + 's';
            addEventToFeed(`Обработано ${data.count} новостей`, 'info');
        });
        
        window.reactor.on('digest_created', function(data) {
            console.log('Дайджест создан:', data);
            addEventToFeed(`Дайджест "${data.title}" создан`, 'success');
        });
        
        window.reactor.on('event_detected', function(data) {
            console.log('Событие обнаружено:', data);
            if (data.title) {
                addEventToFeed(`Событие: ${data.title}`, 'info');
            }
        });
        
        window.reactor.on('system_health_check', function(data) {
            console.log('Проверка здоровья системы:', data);
            document.getElementById('last-health-check').textContent = new Date().toLocaleTimeString();
            addEventToFeed('Проверка здоровья системы', 'info');
        });
        
        window.reactor.on('reactor_heartbeat', function(data) {
            console.log('Heartbeat Reactor:', data);
            updateUptime();
        });
        
        window.reactor.on('reactor_connected', function(data) {
            console.log('Reactor подключен:', data);
            addEventToFeed('Подключение к Reactor установлено', 'success');
        });
        
        window.reactor.on('reactor_disconnected', function(data) {
            console.log('Reactor отключен:', data);
            addEventToFeed('Соединение с Reactor потеряно', 'error');
        });
        
        // Обновляем uptime каждую секунду
        setInterval(updateUptime, 1000);
    }
}

// Функции для управления
function testEvent() {
    if (window.reactor) {
        window.reactor.emit('test_event', {
            message: 'Тестовое событие отправлено',
            timestamp: Date.now()
        });
        addEventToFeed('Тестовое событие отправлено', 'info');
    }
}

function pingReactor() {
    if (window.reactor) {
        window.reactor.ping();
        addEventToFeed('Ping отправлен', 'info');
    }
}

function toggleNotifications() {
    const notifications = document.querySelector('.reactor-notifications');
    if (notifications) {
        notifications.style.display = notifications.style.display === 'none' ? 'block' : 'none';
    }
    addEventToFeed('Уведомления переключены', 'info');
}

// Вспомогательные функции
function addEventToFeed(title, type = 'info') {
    const container = document.querySelector('[data-reactor="events-container"]');
    if (!container) return;
    
    const eventElement = document.createElement('div');
    eventElement.className = `event-item ${type}`;
    eventElement.innerHTML = `
        <div class="event-title">${title}</div>
        <div class="event-time">${new Date().toLocaleTimeString()}</div>
    `;
    
    container.insertBefore(eventElement, container.firstChild);
    
    // Ограничиваем количество событий
    const events = container.querySelectorAll('.event-item');
    if (events.length > 10) {
        events[events.length - 1].remove();
    }
}

function updateUptime() {
    const uptimeElement = document.getElementById('uptime');
    if (uptimeElement && window.reactor) {
        const status = window.reactor.getStatus();
        const uptimeSeconds = status.uptime || 0;
        const minutes = Math.floor(uptimeSeconds / 60);
        const seconds = Math.floor(uptimeSeconds % 60);
        uptimeElement.textContent = `${minutes}m ${seconds}s`;
    }
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    updateUptime();
});

// Экспорт для использования в шаблонах
window.initPageReactor = initPageReactor;
window.testEvent = testEvent;
window.pingReactor = pingReactor;
window.toggleNotifications = toggleNotifications;
