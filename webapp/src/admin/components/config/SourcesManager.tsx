/**
 * Компонент для управления источниками новостей
 */

import { Badge } from '@/components/ui/Badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Calendar, Newspaper } from 'lucide-react';
import { useState } from 'react';
import { useSources, useTestSource } from '../../hooks/useSources';
import { EventsProviders } from './EventsProviders';

export function SourcesManager() {
    const { data: sources, isLoading, error } = useSources();
    const testSource = useTestSource();
    const [testUrl, setTestUrl] = useState('');
    const [testResult, setTestResult] = useState<any>(null);
    const [activeSubTab, setActiveSubTab] = useState<'news' | 'events'>('news');

    if (isLoading) {
        return <div className="p-8">Загрузка источников...</div>;
    }

    if (error) {
        return (
            <div className="p-8">
                <div className="text-error">Ошибка загрузки источников: {error.message}</div>
            </div>
        );
    }

    if (!sources) {
        return <div className="p-8">Нет данных</div>;
    }

    const handleTestSource = async () => {
        if (!testUrl) return;

        try {
            const result = await testSource.mutateAsync({ url: testUrl });
            setTestResult(result);
        } catch (err: any) {
            setTestResult({ success: false, error: err.message });
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Управление источниками</h2>
            </div>

            {/* Подвкладки с правильными цветами */}
            <div className="flex gap-2">
                <button
                    onClick={() => setActiveSubTab('news')}
                    className={`btn flex-1 flex items-center justify-center gap-2 ${activeSubTab === 'news' ? 'btn-primary' : 'btn-secondary'
                        }`}
                >
                    <Newspaper className="w-4 h-4" />
                    Источники новостей
                </button>
                <button
                    onClick={() => setActiveSubTab('events')}
                    className={`btn flex-1 flex items-center justify-center gap-2 ${activeSubTab === 'events' ? 'btn-primary' : 'btn-secondary'
                        }`}
                >
                    <Calendar className="w-4 h-4" />
                    Провайдеры событий
                </button>
            </div>

            {/* Контент */}
            {activeSubTab === 'news' ? (
                <div className="space-y-6 mt-6">

                    {/* Статистика */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Статистика источников</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-4 gap-4">
                                <div>
                                    <div className="text-3xl font-bold text-success">{sources.statistics.categories}</div>
                                    <div className="text-sm text-muted">Категорий</div>
                                </div>
                                <div>
                                    <div className="text-3xl font-bold text-primary">{sources.statistics.subcategories}</div>
                                    <div className="text-sm text-muted">Подкатегорий</div>
                                </div>
                                <div>
                                    <div className="text-3xl font-bold text-[#8b5cf6]">{sources.statistics.sources}</div>
                                    <div className="text-sm text-muted">Источников</div>
                                </div>
                                <div>
                                    <div className="text-3xl font-bold text-warning">{sources.statistics.avg_sources_per_subcategory}</div>
                                    <div className="text-sm text-muted">Среднее / подкатегория</div>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Тест парсера */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Тест RSS парсера</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div className="flex gap-2">
                                    <input
                                        type="url"
                                        placeholder="https://example.com/feed"
                                        className="input flex-1"
                                        value={testUrl}
                                        onChange={(e) => setTestUrl(e.target.value)}
                                    />
                                    <button
                                        onClick={handleTestSource}
                                        disabled={!testUrl || testSource.isPending}
                                        className="btn btn-primary"
                                    >
                                        {testSource.isPending ? 'Тестирование...' : 'Тест'}
                                    </button>
                                </div>

                                {testResult && (
                                    <div className={`p-4 rounded ${testResult.success ? 'status-success' : 'status-error'}`}>
                                        {testResult.success ? (
                                            <div>
                                                <div className="font-semibold mb-2">✅ Парсер работает!</div>
                                                <div className="text-sm">Найдено новостей: {testResult.items_count}</div>
                                                {testResult.sample && testResult.sample.length > 0 && (
                                                    <div className="mt-3">
                                                        <div className="text-xs font-semibold mb-2">Примеры:</div>
                                                        <div className="space-y-2">
                                                            {testResult.sample.map((item: any, idx: number) => (
                                                                <div key={idx} className="text-xs bg-background p-2 rounded">
                                                                    <div className="font-semibold">{item.title}</div>
                                                                    <div className="text-muted mt-1">{item.published_at}</div>
                                                                </div>
                                                            ))}
                                                        </div>
                                                    </div>
                                                )}
                                            </div>
                                        ) : (
                                            <div>
                                                <div className="font-semibold mb-1">❌ Ошибка</div>
                                                <div className="text-sm">{testResult.error}</div>
                                            </div>
                                        )}
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    {/* Структура источников */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Структура источников</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {sources.structure && typeof sources.structure === 'object' && Object.entries(sources.structure).map(([category, subcategories]) => (
                                    <div key={category} className="border rounded p-4">
                                        <h3 className="text-lg font-semibold capitalize mb-3">{category}</h3>
                                        <div className="space-y-3">
                                            {subcategories && typeof subcategories === 'object' && Object.entries(subcategories).map(([subcat, data]) => (
                                                <div key={subcat} className="pl-4 border-l-2 border-muted">
                                                    <div className="flex items-center gap-2 mb-2">
                                                        <span className="font-medium">{subcat}</span>
                                                        <Badge variant="outline" className="text-xs">
                                                            {data.sources.length} источников
                                                        </Badge>
                                                    </div>
                                                    <div className="space-y-1">
                                                        {data.sources.map((source, idx) => (
                                                            <div key={idx} className="text-sm text-muted flex items-center gap-2">
                                                                <span>•</span>
                                                                <span className="font-medium">{source.name}</span>
                                                                <span className="text-xs">({source.url})</span>
                                                            </div>
                                                        ))}
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            ) : (
                <div className="mt-6">
                    <EventsProviders />
                </div>
            )}
        </div>
    );
}
