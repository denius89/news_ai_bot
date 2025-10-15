/**
 * TypeScript типы для Admin Panel
 */

// Статистика системы
export interface AdminStats {
  news_today: number;
  digests_today: number;
  total_users: number;
  avg_importance: number;
  avg_credibility: number;
}

// AI метрики
export interface AIMetrics {
  importance_distribution: DistributionItem[];
  credibility_distribution: DistributionItem[];
  avg_importance: number;
  avg_credibility: number;
  total_items: number;
  days_analyzed: number;
}

export interface DistributionItem {
  range: string;
  count: number;
}

// Метрики пользователей
export interface UserMetrics {
  total_users: number;
  total_subscriptions: number;
  category_distribution: CategoryDistribution[];
}

export interface CategoryDistribution {
  category: string;
  count: number;
}

// Логи
export interface LogEntry {
  text: string;
  timestamp: string;
}

export interface LogsResponse {
  logs: LogEntry[];
  file: string;
  total_lines: number;
  returned_lines: number;
}

export interface LogFile {
  name: string;
  size: number;
  modified: string;
}

// Конфигурация
export interface AdminConfig {
  ai_settings: AISettings;
  system_settings: SystemSettings;
  api_keys: APIKeys;
}

export interface AISettings {
  model_summary: string;
  model_scoring: string;
  max_tokens: number;
}

export interface SystemSettings {
  reactor_enabled: boolean;
  debug_mode: boolean;
  environment: string;
}

export interface APIKeys {
  openai: string;
  telegram_bot: string;
}

// Информация об админе
export interface AdminInfo {
  telegram_id: number;
  username: string;
  is_admin: boolean;
  is_active: boolean;
  last_login: string;
  created_at: string;
}

// SSE данные
export interface SSEMetrics {
  timestamp: string;
  news_today: number;
  server_time: string;
}


