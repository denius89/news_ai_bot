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

const NewsPageSimple: React.FC = () => {
    const [news, setNews] = useState<NewsItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const { authHeaders } = useAuth();

    useEffect(() => {
        console.log('[NewsPageSimple] Component mounted');
        fetchNews();
    }, []);

    const fetchNews = async () => {
        try {
            console.log('[NewsPageSimple] Starting fetch...');
            setLoading(true);
            setError(null);

            const apiUrl = `/api/news/latest?page=1&limit=10`;
            console.log('[NewsPageSimple] API URL:', apiUrl);

            const response = await fetch(apiUrl, {
                headers: authHeaders
            });

            console.log('[NewsPageSimple] Response status:', response.status);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('[NewsPageSimple] API response:', data);

            if (data.status === 'success' && data.data) {
                setNews(data.data);
                console.log('[NewsPageSimple] News loaded:', data.data.length);
            } else {
                setError('Failed to load news');
            }
        } catch (err) {
            console.error('[NewsPageSimple] Error:', err);
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

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
                        onClick={fetchNews}
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        Попробовать снова
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <div className="max-w-4xl mx-auto p-4">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                    Новости ({news.length})
                </h1>

                <div className="space-y-4">
                    {news.map((item) => (
                        <div key={item.id} className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                                {item.title}
                            </h3>
                            <p className="text-gray-600 dark:text-gray-300 mb-2">
                                {item.content.substring(0, 200)}...
                            </p>
                            <div className="flex justify-between items-center text-sm text-gray-500 dark:text-gray-400">
                                <span>{item.source}</span>
                                <span>{item.category}</span>
                                <span>⭐ {item.importance.toFixed(2)}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default NewsPageSimple;
