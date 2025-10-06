/**
 * Reactor Components JavaScript - вынесено из inline JS
 */

// Функции для управления лентой событий
function clearEventsFeed() {
    const container = document.querySelector('[data-reactor="events-container"]');
    if (container) {
        container.innerHTML = '<div class="event-item welcome"><div class="event-icon">👋</div><div class="event-content"><div class="event-title">Лента событий очищена</div><div class="event-time">Готов к новым событиям</div></div></div>';
        document.getElementById('events-counter').textContent = '0';
    }
}

function pauseEvents() {
    // Реализация паузы событий
    console.log('Пауза событий');
}

function testEvent() {
    if (window.reactor) {
        window.reactor.emit('test_event', {
            message: 'Тестовое событие',
            timestamp: Date.now()
        });
    }
}

// Обновляем счетчик событий
let eventCounter = 0;
document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('[data-reactor="events-container"]');
    if (container) {
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    eventCounter = container.querySelectorAll('.event-item').length;
                    const counterElement = document.getElementById('events-counter');
                    if (counterElement) {
                        counterElement.textContent = eventCounter;
                    }
                }
            });
        });
        
        observer.observe(container, { childList: true });
    }
});

// Экспорт для использования в шаблонах
window.clearEventsFeed = clearEventsFeed;
window.pauseEvents = pauseEvents;
window.testEvent = testEvent;
