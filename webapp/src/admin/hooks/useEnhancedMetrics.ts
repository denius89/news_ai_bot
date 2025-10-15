/**
 * React hooks для расширенных метрик (Phase 1)
 */

import { useQuery } from '@tanstack/react-query';

// News Metrics Types
interface NewsTimeline {
  date: string;
  count: number;
}

interface CategoryStats {
  category: string;
  count: number;
  avg_importance: number;
  avg_credibility: number;
}

interface SourceStats {
  source: string;
  count: number;
  avg_credibility: number;
}

interface NewsMetricsData {
  timeline: NewsTimeline[];
  by_category: CategoryStats[];
  by_source: SourceStats[];
  total_news: number;
}

// Events Metrics Types
interface UpcomingEvent {
  event_time: string;
  title: string;
  priority: string;
  category: string;
  importance: number;
  country: string;
}

interface PriorityDist {
  priority: string;
  count: number;
}

interface CategoryDist {
  category: string;
  count: number;
}

interface EventsMetricsData {
  upcoming: UpcomingEvent[];
  by_priority: PriorityDist[];
  by_category: CategoryDist[];
  total_upcoming: number;
  total_analyzed: number;
}

// User Engagement Types
interface ActiveUsers {
  daily: number;
  weekly: number;
  monthly: number;
}

interface GrowthTimeline {
  date: string;
  count: number;
}

interface SubscriptionDist {
  category: string;
  count: number;
}

interface UserEngagementData {
  active_users: ActiveUsers;
  growth_timeline: GrowthTimeline[];
  subscriptions_dist: SubscriptionDist[];
  total_users: number;
  total_subscriptions: number;
}

/**
 * Hook для News Analytics
 */
export function useNewsMetrics(days: number = 7) {
  return useQuery<NewsMetricsData>({
    queryKey: ['admin', 'metrics', 'news', days],
    queryFn: async () => {
      const res = await fetch(`/admin/api/metrics/news?days=${days}`);
      if (!res.ok) throw new Error('Failed to fetch news metrics');
      return res.json();
    },
    staleTime: 60000, // 1 минута
  });
}

/**
 * Hook для Events Analytics
 */
export function useEventsMetrics(days: number = 7, upcomingDays: number = 7) {
  return useQuery<EventsMetricsData>({
    queryKey: ['admin', 'metrics', 'events', days, upcomingDays],
    queryFn: async () => {
      const res = await fetch(`/admin/api/metrics/events?days=${days}&upcoming_days=${upcomingDays}`);
      if (!res.ok) throw new Error('Failed to fetch events metrics');
      return res.json();
    },
    staleTime: 60000, // 1 минута
  });
}

/**
 * Hook для User Engagement
 */
export function useUserEngagement() {
  return useQuery<UserEngagementData>({
    queryKey: ['admin', 'metrics', 'user-engagement'],
    queryFn: async () => {
      const res = await fetch('/admin/api/metrics/user-engagement');
      if (!res.ok) throw new Error('Failed to fetch user engagement');
      return res.json();
    },
    staleTime: 60000, // 1 минута
  });
}

// ==================== Phase 2: Additional Metrics ====================

// Digest Metrics Types
interface DigestTimeline {
  date: string;
  count: number;
}

interface FeedbackStats {
  avg_score: number;
  total_feedback: number;
}

interface DigestMetricsData {
  total_digests: number;
  timeline: DigestTimeline[];
  avg_length_words: number;
  feedback_stats: FeedbackStats;
}

/**
 * Hook для Digest Analytics (Phase 2)
 */
export function useDigestMetrics(days: number = 30) {
  return useQuery<DigestMetricsData>({
    queryKey: ['admin', 'metrics', 'digests', days],
    queryFn: async () => {
      const res = await fetch(`/admin/api/metrics/digests?days=${days}`);
      if (!res.ok) throw new Error('Failed to fetch digest metrics');
      return res.json();
    },
    staleTime: 60000,
  });
}

// AI Performance Detailed Types
interface AIPerformanceTimeline {
  date: string;
  calls: number;
  tokens: number;
  cost: number;
}

interface AIPerformanceData {
  total_ai_calls: number;
  avg_quality_score: number;
  estimated_tokens: number;
  estimated_cost_usd: number;
  timeline: AIPerformanceTimeline[];
}

/**
 * Hook для AI Performance Detailed (Phase 2)
 */
export function useAIPerformanceDetailed(days: number = 7) {
  return useQuery<AIPerformanceData>({
    queryKey: ['admin', 'metrics', 'ai-performance', days],
    queryFn: async () => {
      const res = await fetch(`/admin/api/metrics/ai-performance?days=${days}`);
      if (!res.ok) throw new Error('Failed to fetch AI performance');
      return res.json();
    },
    staleTime: 60000,
  });
}

// System Health Types
interface ProcessStatus {
  status: string;
  pid?: number;
  uptime_seconds: number;
}

interface SystemResources {
  cpu_percent: number;
  memory_percent: number;
  memory_mb: number;
  disk_percent: number;
}

interface APIHealth {
  database_latency_ms: number;
}

interface SystemHealthData {
  processes: {
    flask: ProcessStatus;
    bot: ProcessStatus;
    cloudflare: { status: string };
  };
  resources: SystemResources;
  api_health: APIHealth;
  uptime: {
    flask_uptime_seconds: number;
  };
}

/**
 * Hook для System Health (Phase 2)
 */
export function useSystemHealth() {
  return useQuery<SystemHealthData>({
    queryKey: ['admin', 'system', 'health'],
    queryFn: async () => {
      const res = await fetch('/admin/api/system/health');
      if (!res.ok) throw new Error('Failed to fetch system health');
      return res.json();
    },
    staleTime: 10000, // 10 секунд для более частого обновления
    refetchInterval: 30000, // auto-refresh каждые 30 секунд
  });
}

