/**
 * Hook для управления загрузкой новостей
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
    exportNewsStats,
    getNewsFetchConfig,
    getNewsFetchLogs,
    getNewsFetchStatus,
    getNewsLiveStats,
    getRecentRuns,
    pauseNewsFetch,
    skipCurrentSource,
    startNewsFetch,
    stopNewsFetch
} from '../api/admin';
import type { NewsFetchSettings } from '../types/admin';

/**
 * Получить статус загрузки новостей
 */
export function useNewsFetchStatus() {
    return useQuery({
        queryKey: ['news-fetch-status'],
        queryFn: getNewsFetchStatus,
        staleTime: 2000, // Кешируем на 2 секунды для более свежих данных
        refetchInterval: 3000, // Обновляем каждые 3 секунды
        refetchOnWindowFocus: true, // Обновляем при фокусе окна
        refetchOnMount: true, // Обновляем при монтировании
    });
}

/**
 * Получить конфигурацию загрузки новостей
 */
export function useNewsFetchConfig() {
    return useQuery({
        queryKey: ['news-fetch-config'],
        queryFn: getNewsFetchConfig,
        staleTime: 60000, // Кешируем на 1 минуту
    });
}

/**
 * Получить логи загрузки новостей
 */
export function useNewsFetchLogs(lines: number = 100) {
    return useQuery({
        queryKey: ['news-fetch-logs', lines],
        queryFn: () => getNewsFetchLogs(lines),
        staleTime: 10000, // Кешируем на 10 секунд
        refetchInterval: 10000, // Обновляем каждые 10 секунд
    });
}

/**
 * Мутация для запуска загрузки новостей
 */
export function useStartNewsFetch() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (settings?: Partial<NewsFetchSettings>) => startNewsFetch(settings || {}),
        onSuccess: () => {
            // Инвалидируем статус после запуска
            queryClient.invalidateQueries({ queryKey: ['news-fetch-status'] });
            queryClient.invalidateQueries({ queryKey: ['news-fetch-logs'] });
        },
    });
}

/**
 * Мутация для остановки загрузки новостей
 */
export function useStopNewsFetch() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: stopNewsFetch,
        onSuccess: () => {
            // Инвалидируем статус после остановки
            queryClient.invalidateQueries({ queryKey: ['news-fetch-status'] });
            queryClient.invalidateQueries({ queryKey: ['news-fetch-logs'] });
        },
    });
}

// ==================== Live Statistics Hooks ====================

/**
 * Получить live статистику парсинга новостей
 */
export function useNewsLiveStats() {
    return useQuery({
        queryKey: ['news-live-stats'],
        queryFn: getNewsLiveStats,
        staleTime: 0, // Всегда свежие данные
        refetchInterval: 2000, // Обновляем каждые 2 секунды
        enabled: true, // Включено всегда
    });
}

/**
 * Получить историю последних запусков
 */
export function useRecentRuns() {
    return useQuery({
        queryKey: ['news-recent-runs'],
        queryFn: getRecentRuns,
        staleTime: 30000, // Кешируем на 30 секунд
        refetchInterval: 60000, // Обновляем каждую минуту
    });
}

/**
 * Мутация для паузы/возобновления парсинга
 */
export function usePauseNewsFetch() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (action: 'pause' | 'resume') => pauseNewsFetch(action),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['news-fetch-status'] });
            queryClient.invalidateQueries({ queryKey: ['news-live-stats'] });
        },
    });
}

/**
 * Мутация для пропуска текущего источника
 */
export function useSkipSource() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: skipCurrentSource,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['news-live-stats'] });
        },
    });
}

/**
 * Мутация для экспорта статистики
 */
export function useExportStats() {
    return useMutation({
        mutationFn: exportNewsStats,
    });
}
