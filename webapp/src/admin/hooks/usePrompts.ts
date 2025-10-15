/**
 * React hooks для работы с промптами
 */

import { useQuery } from '@tanstack/react-query';

interface StyleCard {
  name: string;
  description: string;
  characteristics: string[];
  expert_persona: string;
  writing_style: string;
}

interface ToneProfile {
  name: string;
  description: string;
  voice: string;
  characteristics: string[];
}

interface PromptsData {
  styles: { [key: string]: StyleCard };
  tones: { [key: string]: ToneProfile };
  editable: boolean;
}

/**
 * Получить все промпты из prompts_v2.py
 */
export function usePrompts() {
  return useQuery<PromptsData>({
    queryKey: ['admin', 'prompts'],
    queryFn: async () => {
      const res = await fetch('/admin/api/prompts');
      if (!res.ok) throw new Error('Failed to fetch prompts');
      return res.json();
    },
    staleTime: 60000, // 1 минута (промпты редко меняются)
  });
}

