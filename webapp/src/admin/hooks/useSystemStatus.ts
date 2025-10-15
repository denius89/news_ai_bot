/**
 * React hooks для мониторинга системы
 */

import { useQuery } from '@tanstack/react-query';

interface ServiceStatus {
  running: boolean;
  status: string;
  pid_file?: string;
}

interface SystemResources {
  cpu_percent: number;
  memory_percent: number;
  memory_used_mb: number;
  memory_available_mb: number;
  disk_percent: number;
  disk_free_gb: number;
}

interface SystemStatusData {
  services: {
    flask: ServiceStatus;
    bot: ServiceStatus;
    database: ServiceStatus;
  };
  resources: SystemResources;
  uptime: string;
  uptime_seconds: number;
  timestamp: string;
}

/**
 * Получить статус системы с автообновлением каждые 10 секунд
 */
export function useSystemStatus() {
  return useQuery<SystemStatusData>({
    queryKey: ['admin', 'system', 'status'],
    queryFn: async () => {
      const res = await fetch('/admin/api/system/status');
      if (!res.ok) throw new Error('Failed to fetch system status');
      return res.json();
    },
    refetchInterval: 10000, // Обновление каждые 10 секунд
    staleTime: 5000, // 5 секунд
  });
}

