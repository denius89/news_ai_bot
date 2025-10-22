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

// RSS Parser метрики
export interface RSSParserMetrics {
    sources_status: SourceStatus[];
    performance: PerformanceMetrics;
    ai_optimization: AIOptimization;
    errors: ErrorMetric[];
    cache_stats: CacheStats;
    timestamp: string;
}

export interface SourceStatus {
    source: string;
    success_rate: number;
    items_processed: number;
    avg_importance: number;
    avg_credibility: number;
    status: 'healthy' | 'degraded' | 'error';
}

export interface PerformanceMetrics {
    total_processed: number;
    success_rate: number;
    avg_processing_time_ms: number;
    period_hours: number;
}

export interface AIOptimization {
    total_ai_requests: number;
    estimated_saved_requests: number;
    estimated_tokens_saved: number;
    estimated_cost_savings_usd: number;
    local_prediction_rate: number;
}

export interface ErrorMetric {
    error_type: string;
    count: number;
    last_occurrence: string | null;
}

export interface CacheStats {
    hit_rate: number;
    size_mb: number;
    total_requests: number;
}

export interface RSSLiveMetrics {
    current_sources_processing: number;
    news_last_hour: number;
    last_successful_fetch: string | null;
    status: 'active' | 'idle';
    timestamp: string;
}

// News Fetching Control
export interface NewsFetchSettings {
    max_concurrent: number;
    min_importance: number;
    per_subcategory: number;
    force_train: boolean;
    skip_train: boolean;
    categories?: string[];
    subcategories?: string[];
}

export interface NewsFetchStatus {
    running: boolean;
    processes: Array<{
        pid: number;
        command: string;
        start_time: number;
    }>;
    last_run: string | null;
    processed_stats: {
        total_processed: number;
        last_hour: number;
        current_session: number;
    };
}

export interface NewsFetchConfig {
    settings: {
        default_max_concurrent: number;
        default_min_importance: number;
        default_per_subcategory: number;
        ai_model: string;
        available_categories: string[];
        available_subcategories: string[];
        category_structure: Record<string, string[]>;
    };
    available_options: {
        max_concurrent: { min: number; max: number; default: number };
        min_importance: { min: number; max: number; default: number; step: number };
        per_subcategory: { min: number; max: number; default: number };
    };
}

export interface NewsFetchResponse {
    success: boolean;
    process_id?: string;
    message?: string;
    error?: string;
}

export interface EventsFetchSettings {
    days_ahead: number;
    categories?: string[];
    providers?: string[];
    dry_run: boolean;
}

export interface EventsFetchStatus {
    running: boolean;
    processes: Array<{ pid: number; command: string; start_time: number }>;
    last_run: string | null;
    events_stats: {
        total_events: number;
        last_hour: number;
        upcoming_count: number;
    };
}

export interface EventsFetchConfig {
    settings: {
        default_days_ahead: number;
        available_categories: string[];
        available_providers: Record<string, Array<{ name: string; enabled: boolean }>>;
    };
    available_options: {
        days_ahead: { min: number; max: number; default: number };
    };
}

export interface EventsStatistics {
    total: number;
    by_category: Array<{ category: string; count: number; avg_importance: number }>;
    by_provider: Array<{ provider: string; count: number; avg_importance: number }>;
    upcoming_7days: number;
    last_24hours: number;
}

export interface EventsFetchResponse {
    success: boolean;
    process_id?: string;
    message?: string;
    error?: string;
}

// News Live Statistics (Real-time)
export interface NewsLiveStats {
    sources_total: number;
    sources_processed: number;
    sources_remaining: number;
    progress_percent: number;
    news_found: number;
    news_saved: number;
    news_filtered: number;
    errors_count: number;
    current_source: string;
    eta_seconds: number;
    top_sources: TopSource[];
    recent_errors: ParseError[];
    category_stats: CategoryStats[];
    ai_stats: NewsAIStats;
    timestamp: string;
}

export interface TopSource {
    name: string;
    count: number;
    avg_time: number;
}

export interface ParseError {
    source: string;
    error_type: string;
    message: string;
    timestamp: string;
}

export interface CategoryStats {
    name: string;
    count: number;
}

export interface NewsAIStats {
    local_predictions: number;
    openai_calls: number;
    local_percent: number;
    tokens_saved: number;
    estimated_cost: number;
    cost_saved: number;
}

// Run History
export interface RunHistory {
    id: number;
    started_at: string;
    status: 'completed' | 'failed' | 'running' | 'stopped';
    sources_total: number;
    sources_processed: number;
    news_saved: number;
    duration: number;
}

export interface RecentRunsResponse {
    runs: RunHistory[];
}

// Pause/Resume actions
export interface PauseActionRequest {
    action: 'pause' | 'resume';
}

export interface PauseActionResponse {
    success: boolean;
    message: string;
    action: string;
}

// Export Stats
export interface ExportStatsResponse {
    export_timestamp: string;
    version: string;
    live_stats: NewsLiveStats;
    system_info: {
        python_version: string;
        platform: string;
    };
}
