/**
 * Hook для работы с логами
 */

import { useQuery } from '@tanstack/react-query';
import { getLogs, getLogFiles } from '../api/admin';

/**
 * Получить логи
 */
export function useLogs(file: string = 'app.log', lines: number = 100, refetchInterval = 5000) {
  return useQuery({
    queryKey: ['logs', file, lines],
    queryFn: () => getLogs(file, lines),
    refetchInterval, // Auto-refresh каждые 5 сек для live updates
    staleTime: 3000,
  });
}

/**
 * Получить список лог-файлов
 */
export function useLogFiles() {
  return useQuery({
    queryKey: ['log-files'],
    queryFn: getLogFiles,
    staleTime: 30000, // Кешируем на 30 сек
  });
}


