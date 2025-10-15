/**
 * React hooks для работы с Events API
 */

import { useQuery, useMutation } from '@tanstack/react-query';

export function useEventsProviders() {
  return useQuery({
    queryKey: ['admin', 'events', 'providers'],
    queryFn: async () => {
      const res = await fetch('/admin/api/events/providers');
      if (!res.ok) throw new Error('Failed to fetch events providers');
      return res.json();
    },
    staleTime: 30000,
  });
}

export function useTestEventsProvider() {
  return useMutation({
    mutationFn: async (provider: string) => {
      const res = await fetch('/admin/api/events/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider }),
      });
      if (!res.ok) throw new Error('Failed to test provider');
      return res.json();
    },
  });
}
