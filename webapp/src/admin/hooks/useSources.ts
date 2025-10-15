/**
 * React hooks для работы с источниками новостей
 */

import { useQuery, useMutation } from '@tanstack/react-query';

interface Source {
  name: string;
  url: string;
}

interface Subcategory {
  icon: string;
  sources: Source[];
}

interface CategoryStructure {
  [subcategory: string]: Subcategory;
}

interface SourcesStructure {
  [category: string]: CategoryStructure;
}

interface SourcesStatistics {
  categories: number;
  subcategories: number;
  sources: number;
  avg_sources_per_subcategory: number;
}

interface SourcesData {
  structure: SourcesStructure;
  statistics: SourcesStatistics;
}

interface ParsedItem {
  title: string;
  link: string;
  published_at: string;
  source: string;
}

interface TestSourceResult {
  success: boolean;
  items_count?: number;
  sample?: ParsedItem[];
  error?: string;
}

/**
 * Получить структуру источников новостей
 */
export function useSources() {
  return useQuery<SourcesData>({
    queryKey: ['admin', 'sources'],
    queryFn: async () => {
      const res = await fetch('/admin/api/sources');
      if (!res.ok) throw new Error('Failed to fetch sources');
      return res.json();
    },
    staleTime: 60000, // 1 минута
  });
}

/**
 * Протестировать RSS парсер для указанного URL
 */
export function useTestSource() {
  return useMutation<TestSourceResult, Error, { url: string }>({
    mutationFn: async ({ url }) => {
      const res = await fetch('/admin/api/sources/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.error || 'Failed to test source');
      }
      
      return data;
    }
  });
}

