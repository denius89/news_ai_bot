/**
 * Hook для получения админской статистики
 */

import { useQuery } from '@tanstack/react-query';
import { getAdminStats, getAdminInfo } from '../api/admin';

/**
 * Получить общую статистику системы
 */
export function useAdminStats(refetchInterval = 30000) {
  return useQuery({
    queryKey: ['admin-stats'],
    queryFn: getAdminStats,
    refetchInterval, // Auto-refresh каждые 30 сек
    staleTime: 20000,
  });
}

/**
 * Получить информацию о текущем админе
 */
export function useAdminInfo() {
  return useQuery({
    queryKey: ['admin-info'],
    queryFn: getAdminInfo,
    staleTime: 60000, // Кешируем на 1 минуту
  });
}


