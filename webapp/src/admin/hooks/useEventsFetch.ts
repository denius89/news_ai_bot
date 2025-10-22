/**
 * React Query hooks для управления событиями
 */

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
    getEventsFetchConfig,
    getEventsFetchLogs,
    getEventsFetchStatus,
    getEventsStatistics,
    startEventsFetch,
    stopEventsFetch
} from '../api/admin';
import type {
    EventsFetchSettings
} from '../types/admin';

// Query keys
const QUERY_KEYS = {
    config: ['events', 'config'] as const,
    status: ['events', 'status'] as const,
    statistics: ['events', 'statistics'] as const,
    logs: (lines: number) => ['events', 'logs', lines] as const,
} as const;

/**
 * Получить конфигурацию загрузки событий
 */
export function useEventsFetchConfig() {
    return useQuery({
        queryKey: QUERY_KEYS.config,
        queryFn: getEventsFetchConfig,
        staleTime: Infinity,
    });
}

/**
 * Получить статус загрузки событий (real-time)
 */
export function useEventsFetchStatus() {
    return useQuery({
        queryKey: QUERY_KEYS.status,
        queryFn: getEventsFetchStatus,
        staleTime: 2000,
        refetchInterval: 3000,
        refetchOnWindowFocus: true,
        refetchOnMount: true,
    });
}

/**
 * Получить статистику событий
 */
export function useEventsStatistics() {
    return useQuery({
        queryKey: QUERY_KEYS.statistics,
        queryFn: getEventsStatistics,
        staleTime: 10000,
        refetchInterval: 30000,
    });
}

/**
 * Получить логи загрузки событий
 */
export function useEventsFetchLogs(lines: number = 100) {
    return useQuery({
        queryKey: QUERY_KEYS.logs(lines),
        queryFn: () => getEventsFetchLogs(lines),
        staleTime: 5000,
        refetchInterval: 5000,
    });
}

/**
 * Mutation для запуска загрузки событий
 */
export function useStartEventsFetch() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (settings: Partial<EventsFetchSettings>) => startEventsFetch(settings),
        onSuccess: () => {
            // Немедленно инвалидируем статус и принудительно обновляем
            queryClient.invalidateQueries({ queryKey: QUERY_KEYS.status });
            // Также обновляем логи
            queryClient.invalidateQueries({ queryKey: ['events', 'logs'] });

            // Добавляем небольшую задержку для обновления статуса
            setTimeout(() => {
                queryClient.refetchQueries({ queryKey: QUERY_KEYS.status });
            }, 1000);
        },
        onError: (error) => {
            console.error('Failed to start events fetch:', error);
        },
    });
}

/**
 * Mutation для остановки загрузки событий
 */
export function useStopEventsFetch() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: stopEventsFetch,
        onSuccess: () => {
            // Инвалидируем статус для обновления в реальном времени
            queryClient.invalidateQueries({ queryKey: QUERY_KEYS.status });
        },
        onError: (error) => {
            console.error('Failed to stop events fetch:', error);
        },
    });
}
