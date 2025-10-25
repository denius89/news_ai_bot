import React, { useEffect, useState } from 'react';

interface DashboardStats {
    news_today: {
        count: number;
        change: number;
    };
    active_sources: {
        count: number;
        change: number;
    };
    categories: {
        count: number;
        change: number;
    };
    ai_digests: {
        count: number;
        change: number;
    };
}

interface NewsTrendData {
    date: string;
    count: number;
}

interface RecentNewsItem {
    id: string;
    title: string;
    source: string;
    category: string;
    published_at: string;
    credibility: number;
    importance: number;
}

interface SourceBreakdown {
    source: string;
    count: number;
}

export const Dashboard: React.FC = () => {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [trendData, setTrendData] = useState<NewsTrendData[]>([]);
    const [recentNews, setRecentNews] = useState<RecentNewsItem[]>([]);
    const [sourcesBreakdown, setSourcesBreakdown] = useState<SourceBreakdown[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchDashboardData();

        // Обновляем данные каждые 30 секунд
        const interval = setInterval(fetchDashboardData, 30000);

        return () => clearInterval(interval);
    }, []);

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            setError(null);

            // Параллельно загружаем все данные
            const [statsResponse, trendResponse, newsResponse, sourcesResponse] = await Promise.all([
                fetch('/api/dashboard/stats'),
                fetch('/api/dashboard/news_trend'),
                fetch('/api/dashboard/latest_news'),
                fetch('/api/dashboard/sources_breakdown')
            ]);

            // Обрабатываем статистику
            if (statsResponse.ok) {
                const statsData = await statsResponse.json();
                if (statsData.success) {
                    setStats(statsData.data);
                } else {
                    throw new Error(statsData.message || statsData.error || 'Ошибка получения статистики');
                }
            } else {
                throw new Error(`HTTP ${statsResponse.status}: ${statsResponse.statusText}`);
            }

            // Обрабатываем тренд
            if (trendResponse.ok) {
                const trendData = await trendResponse.json();
                if (trendData.success && trendData.data) {
                    setTrendData(trendData.data);
                } else {
                    // Если нет данных, устанавливаем пустой массив
                    setTrendData([]);
                }
            } else {
                // Если ошибка API, устанавливаем пустой массив
                setTrendData([]);
            }

            // Обрабатываем последние новости
            if (newsResponse.ok) {
                const newsData = await newsResponse.json();
                if (newsData.success) {
                    setRecentNews(newsData.data);
                }
            }

            // Обрабатываем разбивку по источникам
            if (sourcesResponse.ok) {
                const sourcesData = await sourcesResponse.json();
                if (sourcesData.success && sourcesData.data) {
                    setSourcesBreakdown(sourcesData.data);
                } else {
                    // Если нет данных, устанавливаем пустой массив
                    setSourcesBreakdown([]);
                }
            } else {
                // Если ошибка API, устанавливаем пустой массив
                setSourcesBreakdown([]);
            }

        } catch (err) {
            console.error('Ошибка загрузки данных дашборда:', err);
            setError(err instanceof Error ? err.message : 'Неизвестная ошибка');
        } finally {
            setLoading(false);
        }
    };

    const formatChange = (change: number): string => {
        if (change > 0) {
            return `+${change}%`;
        } else if (change < 0) {
            return `${change}%`;
        } else {
            return 'стабильно';
        }
    };

    const getChangeColor = (change: number): string => {
        if (change > 0) return 'text-green-600';
        if (change < 0) return 'text-red-600';
        return 'text-gray-600';
    };

    const formatDate = (dateString: string): string => {
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('ru-RU', {
                day: '2-digit',
                month: '2-digit',
                year: 'numeric'
            });
        } catch {
            return dateString;
        }
    };

    const formatTime = (dateString: string): string => {
        try {
            const date = new Date(dateString);
            return date.toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return '';
        }
    };

    if (loading && !stats) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Загрузка данных дашборда...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="text-red-600 text-6xl mb-4">⚠️</div>
                    <h2 className="text-xl font-semibold text-gray-800 mb-2">Ошибка загрузки данных</h2>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button
                        onClick={fetchDashboardData}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                    >
                        Попробовать снова
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-6">
            <div className="max-w-7xl mx-auto">
                {/* Заголовок */}
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-gray-900">Статистика</h1>
                    <p className="text-gray-600 mt-2">
                        Последнее обновление: {new Date().toLocaleTimeString('ru-RU')}
                    </p>
                </div>

                {/* Основные метрики */}
                {stats && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        {/* Новости сегодня */}
                        <div className="bg-white rounded-lg shadow-sm p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Новостей сегодня</p>
                                    <p className="text-3xl font-bold text-gray-900">{stats.news_today.count}</p>
                                </div>
                                <div className={`text-sm font-medium ${getChangeColor(stats.news_today.change)}`}>
                                    {formatChange(stats.news_today.change)}
                                </div>
                            </div>
                        </div>

                        {/* Активные источники */}
                        <div className="bg-white rounded-lg shadow-sm p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Активных источников</p>
                                    <p className="text-3xl font-bold text-gray-900">{stats.active_sources.count}</p>
                                </div>
                                <div className={`text-sm font-medium ${getChangeColor(stats.active_sources.change)}`}>
                                    {stats.active_sources.change > 0 ? `+${stats.active_sources.change}` :
                                        stats.active_sources.change < 0 ? `${stats.active_sources.change}` : 'стабильно'}
                                </div>
                            </div>
                        </div>

                        {/* Категории */}
                        <div className="bg-white rounded-lg shadow-sm p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Категорий</p>
                                    <p className="text-3xl font-bold text-gray-900">{stats.categories.count}</p>
                                </div>
                                <div className="text-sm font-medium text-gray-600">
                                    стабильно
                                </div>
                            </div>
                        </div>

                        {/* AI дайджестов */}
                        <div className="bg-white rounded-lg shadow-sm p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">AI дайджестов</p>
                                    <p className="text-3xl font-bold text-gray-900">{stats.ai_digests.count}</p>
                                </div>
                                <div className={`text-sm font-medium ${getChangeColor(stats.ai_digests.change)}`}>
                                    {stats.ai_digests.change > 0 ? `+${stats.ai_digests.change}` :
                                        stats.ai_digests.change < 0 ? `${stats.ai_digests.change}` : 'стабильно'}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Графики и дополнительные данные */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Тренд новостей */}
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Тренд новостей (7 дней)</h3>
                        {trendData.length > 0 ? (
                            <div className="space-y-2">
                                {trendData.map((item, index) => (
                                    <div key={index} className="flex items-center justify-between">
                                        <span className="text-sm text-gray-600">{formatDate(item.date)}</span>
                                        <div className="flex items-center">
                                            <div className="w-32 bg-gray-200 rounded-full h-2 mr-2">
                                                <div
                                                    className="bg-blue-600 h-2 rounded-full"
                                                    style={{
                                                        width: `${Math.min(100, trendData.length > 0 ? (item.count / Math.max(1, ...trendData.map(d => d.count))) * 100 : 0)}%`
                                                    }}
                                                ></div>
                                            </div>
                                            <span className="text-sm font-medium text-gray-900 w-8 text-right">{item.count}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500">Нет данных для отображения</p>
                        )}
                    </div>

                    {/* Разбивка по источникам */}
                    <div className="bg-white rounded-lg shadow-sm p-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Топ источников (7 дней)</h3>
                        {sourcesBreakdown.length > 0 ? (
                            <div className="space-y-3">
                                {sourcesBreakdown.slice(0, 5).map((item, index) => (
                                    <div key={index} className="flex items-center justify-between">
                                        <span className="text-sm text-gray-600 truncate flex-1 mr-2">{item.source}</span>
                                        <div className="flex items-center">
                                            <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                                                <div
                                                    className="bg-green-600 h-2 rounded-full"
                                                    style={{
                                                        width: `${Math.min(100, sourcesBreakdown.length > 0 ? (item.count / Math.max(1, ...sourcesBreakdown.map(s => s.count))) * 100 : 0)}%`
                                                    }}
                                                ></div>
                                            </div>
                                            <span className="text-sm font-medium text-gray-900 w-8 text-right">{item.count}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-gray-500">Нет данных для отображения</p>
                        )}
                    </div>
                </div>

                {/* Последние новости */}
                <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Последние новости</h3>
                    {recentNews.length > 0 ? (
                        <div className="space-y-4">
                            {recentNews.map((news) => (
                                <div key={news.id} className="border-b border-gray-200 pb-4 last:border-b-0">
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <h4 className="text-sm font-medium text-gray-900 mb-1">{news.title}</h4>
                                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                                                <span>{news.source}</span>
                                                <span>{news.category}</span>
                                                <span>{formatDate(news.published_at)} {formatTime(news.published_at)}</span>
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-2 ml-4">
                                            <span className="text-xs text-gray-500">Достоверность:</span>
                                            <span className="text-xs font-medium text-blue-600">
                                                {Math.round(news.credibility * 100)}%
                                            </span>
                                            <span className="text-xs text-gray-500">Важность:</span>
                                            <span className="text-xs font-medium text-green-600">
                                                {Math.round(news.importance * 100)}%
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-gray-500">Нет новостей для отображения</p>
                    )}
                </div>

                {/* Кнопка обновления */}
                <div className="mt-6 text-center">
                    <button
                        onClick={fetchDashboardData}
                        disabled={loading}
                        className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                        {loading ? 'Обновление...' : 'Обновить данные'}
                    </button>
                </div>
            </div>
        </div>
    );
};
