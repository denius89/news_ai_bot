/**
 * Hook для получения метрик (AI и пользователи)
 */

import { useQuery } from '@tanstack/react-query';
import { getAIMetrics, getUserMetrics } from '../api/admin';

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


