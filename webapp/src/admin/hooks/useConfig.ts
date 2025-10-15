/**
 * React hooks для работы с конфигурацией системы
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface ConfigValue {
  value: any;
  description: string;
  updated_at: string;
  full_key: string;
}

interface ConfigCategory {
  [key: string]: ConfigValue;
}

interface AllConfig {
  ai?: ConfigCategory;
  system?: ConfigCategory;
  sources?: ConfigCategory;
  users?: ConfigCategory;
  monitoring?: ConfigCategory;
}

/**
 * Получить все настройки из БД
 */
export function useAllConfig() {
  return useQuery<AllConfig>({
    queryKey: ['admin', 'config', 'all'],
    queryFn: async () => {
      const res = await fetch('/admin/api/config/all');
      if (!res.ok) throw new Error('Failed to fetch config');
      return res.json();
    },
    staleTime: 30000, // 30 секунд
  });
}

/**
 * Обновить конкретную настройку
 */
export function useUpdateConfig() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ category, key, value }: { category: string; key: string; value: any }) => {
      const res = await fetch(`/admin/api/config/${category}/${key}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value })
      });
      
      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.error || 'Failed to update config');
      }
      
      return res.json();
    },
    onSuccess: () => {
      // Обновляем кэш после успешного сохранения
      queryClient.invalidateQueries({ queryKey: ['admin', 'config'] });
    }
  });
}

