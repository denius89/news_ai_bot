/**
 * API client для Admin Panel
 */

import type {
    AdminConfig,
    AdminInfo,
    AdminStats,
    AIMetrics,
    EventsFetchConfig,
    EventsFetchResponse,
    EventsFetchSettings,
    EventsFetchStatus,
    EventsStatistics,
    ExportStatsResponse,
    LogFile,
    LogsResponse,
    NewsFetchConfig,
    NewsFetchResponse,
    NewsFetchSettings,
    NewsFetchStatus,
    NewsLiveStats,
    PauseActionResponse,
    RecentRunsResponse,
    RSSLiveMetrics,
    RSSParserMetrics,
    UserMetrics
} from '../types/admin';

const API_BASE = '/admin/api';

/**
 * Обработка ответа от API
 */
async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(error.error || `HTTP error! status: ${response.status}`);
    }
    return response.json();
}

/**
 * Получить информацию о текущем админе
 */
export async function getAdminInfo(): Promise<AdminInfo> {
    const response = await fetch(`${API_BASE}/me`);
    return handleResponse<AdminInfo>(response);
}

/**
 * Получить общую статистику
 */
export async function getAdminStats(): Promise<AdminStats> {
    const response = await fetch(`${API_BASE}/stats`);
    return handleResponse<AdminStats>(response);
}

/**
 * Получить AI метрики
 */
export async function getAIMetrics(days: number = 7): Promise<AIMetrics> {
    const response = await fetch(`${API_BASE}/metrics/ai?days=${days}`);
    return handleResponse<AIMetrics>(response);
}

/**
 * Получить метрики пользователей
 */
export async function getUserMetrics(): Promise<UserMetrics> {
    const response = await fetch(`${API_BASE}/metrics/users`);
    return handleResponse<UserMetrics>(response);
}

/**
 * Получить логи
 */
export async function getLogs(file: string = 'app.log', lines: number = 100): Promise<LogsResponse> {
    const response = await fetch(`${API_BASE}/logs/tail?file=${file}&lines=${lines}`);
    return handleResponse<LogsResponse>(response);
}

/**
 * Получить список лог-файлов
 */
export async function getLogFiles(): Promise<{ files: LogFile[] }> {
    const response = await fetch(`${API_BASE}/logs/files`);
    return handleResponse<{ files: LogFile[] }>(response);
}

/**
 * Получить конфигурацию
 */
export async function getConfig(): Promise<AdminConfig> {
    const response = await fetch(`${API_BASE}/config`);
    return handleResponse<AdminConfig>(response);
}

/**
 * Обновить конфигурацию
 */
export async function updateConfig(config: Partial<AdminConfig>): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE}/config`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
    });
    return handleResponse<{ status: string; message: string }>(response);
}

/**
 * Получить RSS парсер метрики
 */
export async function getRSSParserMetrics(hours: number = 24): Promise<RSSParserMetrics> {
    const response = await fetch(`${API_BASE}/metrics/rss-parser?hours=${hours}`);
    return handleResponse<RSSParserMetrics>(response);
}

/**
 * Получить live RSS парсер метрики
 */
export async function getRSSLiveMetrics(): Promise<RSSLiveMetrics> {
    const response = await fetch(`${API_BASE}/metrics/rss-parser/live`);
    return handleResponse<RSSLiveMetrics>(response);
}

/**
 * Запустить загрузку новостей
 */
export async function startNewsFetch(settings: Partial<NewsFetchSettings>): Promise<NewsFetchResponse> {
    const response = await fetch(`${API_BASE}/news/start-fetch`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
    });
    return handleResponse<NewsFetchResponse>(response);
}

/**
 * Остановить загрузку новостей
 */
export async function stopNewsFetch(): Promise<NewsFetchResponse> {
    const response = await fetch(`${API_BASE}/news/stop-fetch`, {
        method: 'POST',
    });
    return handleResponse<NewsFetchResponse>(response);
}

/**
 * Получить статус загрузки новостей
 */
export async function getNewsFetchStatus(): Promise<NewsFetchStatus> {
    const response = await fetch(`${API_BASE}/news/status`);
    return handleResponse<NewsFetchStatus>(response);
}

/**
 * Получить конфигурацию загрузки новостей
 */
export async function getNewsFetchConfig(): Promise<NewsFetchConfig> {
    const response = await fetch(`${API_BASE}/news/config`);
    return handleResponse<NewsFetchConfig>(response);
}

/**
 * Получить логи загрузки новостей
 */
export async function getNewsFetchLogs(lines: number = 100): Promise<LogsResponse> {
    const response = await fetch(`${API_BASE}/news/logs?lines=${lines}`);
    return handleResponse<LogsResponse>(response);
}

/**
 * Health check
 */
export async function healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await fetch(`${API_BASE}/health`);
    return handleResponse<{ status: string; timestamp: string }>(response);
}

// ==================== Events Fetch API ====================

/**
 * Запустить загрузку событий
 */
export async function startEventsFetch(settings: Partial<EventsFetchSettings>): Promise<EventsFetchResponse> {
    const response = await fetch(`${API_BASE}/events/start-fetch`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
    });
    return handleResponse<EventsFetchResponse>(response);
}

/**
 * Остановить загрузку событий
 */
export async function stopEventsFetch(): Promise<EventsFetchResponse> {
    const response = await fetch(`${API_BASE}/events/stop-fetch`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });
    return handleResponse<EventsFetchResponse>(response);
}

/**
 * Получить статус загрузки событий
 */
export async function getEventsFetchStatus(): Promise<EventsFetchStatus> {
    const response = await fetch(`${API_BASE}/events/status`);
    return handleResponse<EventsFetchStatus>(response);
}

/**
 * Получить конфигурацию загрузки событий
 */
export async function getEventsFetchConfig(): Promise<EventsFetchConfig> {
    const response = await fetch(`${API_BASE}/events/config`);
    return handleResponse<EventsFetchConfig>(response);
}

/**
 * Получить статистику событий
 */
export async function getEventsStatistics(): Promise<EventsStatistics> {
    const response = await fetch(`${API_BASE}/events/statistics`);
    return handleResponse<EventsStatistics>(response);
}

/**
 * Получить логи загрузки событий
 */
export async function getEventsFetchLogs(lines: number = 100): Promise<LogsResponse> {
    const response = await fetch(`${API_BASE}/events/logs?lines=${lines}`);
    return handleResponse<LogsResponse>(response);
}

// ==================== News Live Statistics API ====================

/**
 * Получить live статистику парсинга новостей
 */
export async function getNewsLiveStats(): Promise<NewsLiveStats> {
    const response = await fetch(`${API_BASE}/news/live-stats`);
    return handleResponse<NewsLiveStats>(response);
}

/**
 * Пауза/возобновление парсинга новостей
 */
export async function pauseNewsFetch(action: 'pause' | 'resume'): Promise<PauseActionResponse> {
    const response = await fetch(`${API_BASE}/news/pause`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action }),
    });
    return handleResponse<PauseActionResponse>(response);
}

/**
 * Пропустить текущий источник
 */
export async function skipCurrentSource(): Promise<{ success: boolean; message: string }> {
    const response = await fetch(`${API_BASE}/news/skip-source`, {
        method: 'POST',
    });
    return handleResponse<{ success: boolean; message: string }>(response);
}

/**
 * Экспорт статистики парсинга
 */
export async function exportNewsStats(): Promise<ExportStatsResponse> {
    const response = await fetch(`${API_BASE}/news/export-stats`);
    return handleResponse<ExportStatsResponse>(response);
}

/**
 * Получить историю последних запусков
 */
export async function getRecentRuns(): Promise<RecentRunsResponse> {
    const response = await fetch(`${API_BASE}/news/recent-runs`);
    return handleResponse<RecentRunsResponse>(response);
}
