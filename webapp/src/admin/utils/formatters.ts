/**
 * Утилиты форматирования для Admin Panel
 */

/**
 * Форматирует длительность в секундах в читаемый формат
 */
export function formatDuration(seconds: number): string {
    if (seconds < 60) {
        return `${seconds} сек`;
    }

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    if (minutes < 60) {
        return remainingSeconds > 0
            ? `${minutes} мин ${remainingSeconds} сек`
            : `${minutes} мин`;
    }

    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;

    return `${hours} ч ${remainingMinutes} мин`;
}

/**
 * Форматирует время из ISO строки в локальный формат
 */
export function formatTime(isoString: string): string {
    try {
        const date = new Date(isoString);
        return date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return isoString;
    }
}

/**
 * Извлекает уровень лога из текста
 */
export function parseLogLevel(text: string): 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS' | 'DEBUG' {
    const upperText = text.toUpperCase();

    if (upperText.includes('ERROR') || upperText.includes('❌')) {
        return 'ERROR';
    }
    if (upperText.includes('WARNING') || upperText.includes('⚠️')) {
        return 'WARNING';
    }
    if (upperText.includes('SUCCESS') || upperText.includes('✅')) {
        return 'SUCCESS';
    }
    if (upperText.includes('DEBUG')) {
        return 'DEBUG';
    }

    return 'INFO';
}

/**
 * Подсвечивает важные слова в тексте лога
 */
export function highlightLogText(text: string): string {
    // Выделяем ключевые слова эмодзи и важные данные
    return text
        // Источники в кавычках
        .replace(/"([^"]+\.[a-z]+)"/g, '<span class="text-blue-600 font-mono">"$1"</span>')
        // Числовые значения
        .replace(/\b(\d+)\b/g, '<span class="text-green-600 font-semibold">$1</span>')
        // Временные метки
        .replace(/\[(\d{2}:\d{2}:\d{2})\]/g, '<span class="text-gray-500">[$1]</span>')
        // Статусы
        .replace(/\b(успех|error|success|завершен|запущен)\b/gi,
            '<span class="font-semibold">$1</span>')
        // URL и пути
        .replace(/(https?:\/\/[^\s]+)/g,
            '<span class="text-purple-600 underline">$1</span>');
}

/**
 * Получает цвет для уровня лога
 */
export function getLogLevelColor(level: string): string {
    switch (level) {
        case 'ERROR':
            return 'text-red-600 bg-red-50';
        case 'WARNING':
            return 'text-yellow-600 bg-yellow-50';
        case 'SUCCESS':
            return 'text-green-600 bg-green-50';
        case 'DEBUG':
            return 'text-gray-500 bg-gray-50';
        default:
            return 'text-blue-600 bg-blue-50';
    }
}

/**
 * Форматирует размер файла в читаемый формат
 */
export function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B';

    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

/**
 * Форматирует процент с ограничением знаков после запятой
 */
export function formatPercent(value: number, maxDecimals: number = 1): string {
    return `${Math.min(100, Math.max(0, value)).toFixed(maxDecimals)}%`;
}

/**
 * Форматирует большие числа с разделителями
 */
export function formatNumber(value: number): string {
    return value.toLocaleString('ru-RU');
}

/**
 * Получает иконку для статуса запуска
 */
export function getRunStatusIcon(status: string): string {
    switch (status) {
        case 'completed':
            return '✅';
        case 'failed':
            return '❌';
        case 'running':
            return '🔄';
        case 'stopped':
            return '⏸️';
        default:
            return '❓';
    }
}

/**
 * Получает текст статуса запуска
 */
export function getRunStatusText(status: string): string {
    switch (status) {
        case 'completed':
            return 'Завершен';
        case 'failed':
            return 'Ошибка';
        case 'running':
            return 'Выполняется';
        case 'stopped':
            return 'Остановлен';
        default:
            return 'Неизвестно';
    }
}
