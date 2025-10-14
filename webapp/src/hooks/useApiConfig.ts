import { useState, useEffect } from 'react';

interface ApiConfig {
  tunnel_url: string;
  webapp_url: string;
  api_url: string;
  allowed_hosts: string[];
}

interface UseApiConfigResult {
  config: ApiConfig | null;
  loading: boolean;
  error: string | null;
}

const STORAGE_KEY = 'pulseai_api_config';
const CACHE_DURATION = 5 * 60 * 1000; // 5 минут

/**
 * Hook для получения и кэширования API конфигурации.
 * 
 * Получает конфигурацию URL'ов от backend при монтировании.
 * Кэширует результат в localStorage на 5 минут.
 * 
 * @returns {UseApiConfigResult} Конфигурация, состояние загрузки и ошибки
 */
export function useApiConfig(): UseApiConfigResult {
  const [config, setConfig] = useState<ApiConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadConfig = async () => {
      try {
        // Проверяем кэш
        const cached = localStorage.getItem(STORAGE_KEY);
        if (cached) {
          const { data, timestamp } = JSON.parse(cached);
          const age = Date.now() - timestamp;
          
          if (age < CACHE_DURATION) {
            setConfig(data);
            setLoading(false);
            return;
          }
        }

        // Загружаем свежую конфигурацию
        const response = await fetch('/api/config/urls');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch config: ${response.status}`);
        }

        const result = await response.json();
        
        if (result.status === 'success') {
          const configData = result.data;
          
          // Сохраняем в кэш
          localStorage.setItem(
            STORAGE_KEY,
            JSON.stringify({
              data: configData,
              timestamp: Date.now(),
            })
          );
          
          setConfig(configData);
        } else {
          throw new Error(result.message || 'Unknown error');
        }
      } catch (err) {
        console.error('Error loading API config:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    loadConfig();
  }, []);

  return { config, loading, error };
}

/**
 * Очищает кэш конфигурации.
 * Используйте при смене URL Cloudflare.
 */
export function clearApiConfigCache(): void {
  localStorage.removeItem(STORAGE_KEY);
}

