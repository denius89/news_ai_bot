import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';

interface NewsItem {
    id: string;
    title: string;
    content: string;
    source: string;
    category: string;
    publishedAt: string;
    credibility: number;
    importance: number;
}

const NewsPageSafe: React.FC = () => {
    const [news, setNews] = useState<NewsItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { authHeaders } = useAuth();

    useEffect(() => {
        const fetchNews = async () => {
            try {
                setLoading(true);
                console.log('[NewsPageSafe] Fetching news...');

                const response = await fetch('/api/news/latest?page=1&limit=10', {
                    headers: authHeaders
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                console.log('[NewsPageSafe] API response:', data);

                // Безопасная проверка данных
                if (data && data.status === 'success' && Array.isArray(data.data)) {
                    const transformedNews: NewsItem[] = data.data.map((item: any) => ({
                        id: item.id || Math.random().toString(),
                        title: item.title || 'Без заголовка',
                        content: item.content || 'Содержимое недоступно',
                        source: item.source || 'Неизвестный источник',
                        category: item.category || 'general',
                        publishedAt: item.published_at || new Date().toISOString(),
                        credibility: typeof item.credibility === 'number' ? item.credibility : 0.5,
                        importance: typeof item.importance === 'number' ? item.importance : 0.5,
                    }));

                    setNews(transformedNews);
                    console.log('[NewsPageSafe] News loaded:', transformedNews.length);
                } else {
                    console.warn('[NewsPageSafe] Invalid data structure:', data);
                    setNews([]);
                }
            } catch (err) {
                console.error('[NewsPageSafe] Error:', err);
                setError(err instanceof Error ? err.message : 'Unknown error');
                setNews([]);
            } finally {
                setLoading(false);
            }
        };

        fetchNews();
    }, [authHeaders]);

    if (loading) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Загрузка новостей...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
                <div className="text-center">
                    <p className="text-red-600 dark:text-red-400 mb-4">Ошибка: {error}</p>
                    <button
                        onClick={() => window.location.reload()}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        Перезагрузить
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                Новости ({news.length})
            </h1>

            <div className="space-y-4">
                {news.map((item) => (
                    <div key={item.id} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                            {item.title}
                        </h2>
                        <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">
                            {item.content.substring(0, 150)}...
                        </p>
                        <div className="flex justify-between items-center text-xs text-gray-500">
                            <span>Источник: {item.source}</span>
                            <span>Категория: {item.category}</span>
                        </div>
                        <div className="flex justify-between items-center text-xs text-gray-500 mt-1">
                            <span>Важность: {item.importance.toFixed(2)}</span>
                            <span>Достоверность: {item.credibility.toFixed(2)}</span>
                        </div>
                    </div>
                ))}
            </div>

            {news.length === 0 && (
                <div className="text-center py-12">
                    <p className="text-gray-600 dark:text-gray-400">Нет новостей для отображения</p>
                </div>
            )}
        </div>
    );
};

export default NewsPageSafe;
