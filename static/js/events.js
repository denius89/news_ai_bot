/**
 * Events page JavaScript - вынесено из inline JS
 */

function updateTimeRemaining() {
    const now = new Date();
    const todayStr = now.toISOString().slice(0, 10);
    let todayCount = 0;

    document.querySelectorAll(".time-remaining").forEach(el => {
        const targetTime = new Date(el.dataset.time);
        if (isNaN(targetTime)) return;

        const diffMs = targetTime - now;
        if (diffMs <= 0) {
            el.textContent = "⏳ Уже прошло";
            return;
        }

        const mins = Math.floor(diffMs / 60000);
        const hrs = Math.floor(mins / 60);
        const days = Math.floor(hrs / 24);

        if (days > 0) {
            el.textContent = `через ${days} дн. ${hrs % 24} ч.`;
        } else if (hrs > 0) {
            el.textContent = `через ${hrs} ч. ${mins % 60} мин.`;
        } else {
            el.textContent = `через ${mins} мин.`;
        }
    });

    document.querySelectorAll(".event-row, .event-card").forEach(row => {
        const targetTime = new Date(row.dataset.time);
        if (!isNaN(targetTime)) {
            if (targetTime.toISOString().slice(0, 10) === todayStr) {
                row.classList.add("event-today");
                todayCount++;
            }
        }
    });

    document.getElementById("today-count").textContent = todayCount;
}

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    updateTimeRemaining();
    setInterval(updateTimeRemaining, 60000);
});

// Экспорт для использования в шаблонах
window.updateTimeRemaining = updateTimeRemaining;
