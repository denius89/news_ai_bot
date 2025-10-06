/**
 * Index page JavaScript - вынесено из inline JS
 */

// Инициализация Lucide иконок
document.addEventListener('DOMContentLoaded', function() {
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
});

// Инициализация Reactor для главной страницы
function initPageReactor() {
    console.log('Инициализация Reactor для главной страницы');
    
    // Подписываемся на события для обновления UI
    if (window.reactor) {
        // Обновляем счетчик новостей
        window.reactor.on('news_processed', function(data) {
            console.log('Новости обработаны на главной странице:', data);
        });
        
        // Обновляем статус дайджеста
        window.reactor.on('digest_created', function(data) {
            console.log('Дайджест создан на главной странице:', data);
        });
        
        // Обновляем события
        window.reactor.on('event_detected', function(data) {
            console.log('Событие обнаружено на главной странице:', data);
        });
        
        // Обновляем метрики AI
        window.reactor.on('ai_metrics_updated', function(data) {
            console.log('AI метрики обновлены на главной странице:', data);
        });
    }
}

// Экспорт для использования в шаблонах
window.initPageReactor = initPageReactor;
