/**
 * Hook для Server-Sent Events (SSE)
 */

import { useEffect, useState, useRef } from 'react';

export function useSSE<T>(url: string) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    // Создаем EventSource с AbortController для безопасного закрытия
    const eventSource = new EventSource(url);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data) as T;
        setData(parsed);
        setError(null);
      } catch (e) {
        setError(e as Error);
      }
    };

    eventSource.onerror = () => {
      setError(new Error('SSE connection failed'));
      setIsConnected(false);
      eventSource.close();
    };

    // Cleanup при размонтировании
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        eventSourceRef.current = null;
      }
      setIsConnected(false);
    };
  }, [url]);

  return { data, error, isConnected };
}

