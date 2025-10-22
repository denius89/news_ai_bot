/**
 * Hook для получения метрик (AI и пользователи)
 */

import { useQuery } from '@tanstack/react-query';
import { getAIMetrics, getRSSLiveMetrics, getRSSParserMetrics, getUserMetrics } from '../api/admin';

/**
 * Получить AI метрики
 */
export function useAIMetrics(days: number = 7) {
    return useQuery({
        queryKey: ['ai-metrics', days],
        queryFn: () => getAIMetrics(days),
        staleTime: 60000, // Кешируем на 1 минуту
    });
}

/**
 * Получить метрики пользователей
 */
export function useUserMetrics() {
    return useQuery({
        queryKey: ['user-metrics'],
        queryFn: getUserMetrics,
        staleTime: 60000,
    });
}

/**
 * Получить RSS парсер метрики
 */
export function useRSSParserMetrics(hours: number = 24) {
    return useQuery({
        queryKey: ['rss-parser-metrics', hours],
        queryFn: () => getRSSParserMetrics(hours),
        staleTime: 60000, // Кешируем на 1 минуту
        refetchInterval: 30000, // Обновляем каждые 30 секунд
    });
}

/**
 * Получить live RSS парсер метрики
 */
export function useRSSLiveMetrics() {
    return useQuery({
        queryKey: ['rss-live-metrics'],
        queryFn: getRSSLiveMetrics,
        staleTime: 10000, // Кешируем на 10 секунд
        refetchInterval: 10000, // Обновляем каждые 10 секунд
    });
}
