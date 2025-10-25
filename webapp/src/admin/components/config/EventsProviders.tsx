/**
 * Компонент для отображения провайдеров событий
 */

import { Badge } from '@/components/ui/Badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Activity, Bitcoin, Calendar, Laptop, Trophy } from 'lucide-react';
import { useState } from 'react';
import { useEventsProviders, useTestEventsProvider } from '../../hooks/useEventsConfig';

export function EventsProviders() {
    const { data: eventsData, isLoading, error } = useEventsProviders();
    const testProvider = useTestEventsProvider();
    const [testResults, setTestResults] = useState<{ [key: string]: any }>({});
    const [testingProviders, setTestingProviders] = useState<Set<string>>(new Set());
    const [selectedCategory, setSelectedCategory] = useState<string>('all');

    const handleTestProvider = async (providerName: string) => {
        setTestingProviders(prev => new Set(prev).add(providerName));
        try {
            const result = await testProvider.mutateAsync(providerName);
            setTestResults(prev => ({ ...prev, [providerName]: result }));
        } catch (err: any) {
            setTestResults(prev => ({ ...prev, [providerName]: { success: false, error: err.message } }));
        } finally {
            setTestingProviders(prev => {
                const newSet = new Set(prev);
                newSet.delete(providerName);
                return newSet;
            });
        }
    };

    // Фильтруем провайдеров по выбранной категории
    const filteredProviders = eventsData?.providers?.filter((provider: any) =>
        selectedCategory === 'all' || provider.category === selectedCategory
    ) || [];

    if (isLoading) return <div className="p-8">Загрузка провайдеров событий...</div>;
    if (error) return <div className="p-8 text-error">Ошибка: {error.message}</div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-2">
                <Calendar className="w-6 h-6" />
                <h2 className="text-2xl font-bold">Провайдеры событий</h2>
            </div>

            {/* Статистика по категориям */}
            <div className="grid grid-cols-3 gap-4">
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3">
                            <Trophy className="w-8 h-8 text-success" />
                            <div>
                                <div className="text-2xl font-bold">{eventsData?.categories?.sports || 0}</div>
                                <div className="text-sm text-muted">Спортивные события</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3">
                            <Bitcoin className="w-8 h-8 text-warning" />
                            <div>
                                <div className="text-2xl font-bold">{eventsData?.categories?.crypto || 0}</div>
                                <div className="text-sm text-muted">Крипто события</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <Card>
                    <CardContent className="pt-6">
                        <div className="flex items-center gap-3">
                            <Laptop className="w-8 h-8 text-primary" />
                            <div>
                                <div className="text-2xl font-bold">{eventsData?.categories?.tech || 0}</div>
                                <div className="text-sm text-muted">Технологические события</div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Табы для фильтрации по категориям */}
            <Card>
                <CardHeader>
                    <CardTitle>Провайдеры событий</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="flex border-b">
                        <button
                            onClick={() => setSelectedCategory('all')}
                            className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${selectedCategory === 'all'
                                ? 'border-b-2 border-primary text-primary bg-primary/5'
                                : 'text-muted hover:text-text hover:bg-muted/50'
                                }`}
                        >
                            <div className="flex items-center justify-center gap-2">
                                <Calendar className="w-4 h-4" />
                                <span>Все ({eventsData?.providers?.length || 0})</span>
                            </div>
                        </button>

                        {eventsData?.categories && typeof eventsData.categories === 'object' && Object.entries(eventsData.categories).map(([category, count]: [string, any]) => {
                            const categoryNames: { [key: string]: string } = {
                                'sports': 'Спорт',
                                'crypto': 'Криптовалюты',
                                'tech': 'Технологии',
                                'markets': 'Финансы',
                                'world': 'Мир',
                                'other': 'Другие'
                            };

                            const icons: { [key: string]: any } = {
                                'sports': Trophy,
                                'crypto': Bitcoin,
                                'tech': Laptop,
                                'markets': Activity,
                                'world': Calendar,
                                'other': Activity
                            };

                            const IconComponent = icons[category] || Activity;

                            return (
                                <button
                                    key={category}
                                    onClick={() => setSelectedCategory(category)}
                                    className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${selectedCategory === category
                                        ? 'border-b-2 border-primary text-primary bg-primary/5'
                                        : 'text-muted hover:text-text hover:bg-muted/50'
                                        }`}
                                >
                                    <div className="flex items-center justify-center gap-2">
                                        <IconComponent className="w-4 h-4" />
                                        <span>{categoryNames[category] || category} ({count})</span>
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </CardContent>
            </Card>

            {/* Список провайдеров в таблице */}
            <Card>
                <CardContent>
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-border">
                                    <th className="text-left py-3 px-4 font-semibold">Провайдер</th>
                                    <th className="text-left py-3 px-4 font-semibold">Категория</th>
                                    <th className="text-left py-3 px-4 font-semibold">Событий</th>
                                    <th className="text-left py-3 px-4 font-semibold">Статус</th>
                                    <th className="text-left py-3 px-4 font-semibold">Действия</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredProviders.map((provider: any) => {
                                    const categoryNames: { [key: string]: string } = {
                                        'sports': 'Спорт',
                                        'crypto': 'Криптовалюты',
                                        'tech': 'Технологии',
                                        'markets': 'Финансы',
                                        'other': 'Другие'
                                    };

                                    const category = provider.category || 'other';

                                    return (
                                        <tr key={provider.name} className="border-b border-border/50 hover:bg-muted/20">
                                            <td className="py-3 px-4">
                                                <div className="flex items-center gap-2">
                                                    {category === 'sports' && <Trophy className="w-4 h-4 text-success" />}
                                                    {category === 'crypto' && <Bitcoin className="w-4 h-4 text-warning" />}
                                                    {category === 'tech' && <Laptop className="w-4 h-4 text-primary" />}
                                                    {category === 'markets' && <Activity className="w-4 h-4 text-accent" />}
                                                    {category === 'other' && <Activity className="w-4 h-4 text-muted" />}
                                                    <span className="font-medium">{provider.name}</span>
                                                </div>
                                            </td>
                                            <td className="py-3 px-4">
                                                <Badge variant="outline" className="text-xs">
                                                    {categoryNames[category] || category}
                                                </Badge>
                                            </td>
                                            <td className="py-3 px-4">
                                                <span className="font-semibold">{provider.events_count}</span>
                                            </td>
                                            <td className="py-3 px-4">
                                                <Badge variant={provider.status === 'active' ? 'default' : 'secondary'}>
                                                    {provider.status === 'active' ? 'Активен' : 'Отключен'}
                                                </Badge>
                                            </td>
                                            <td className="py-3 px-4">
                                                <button
                                                    onClick={(e) => {
                                                        e.preventDefault();
                                                        e.stopPropagation();
                                                        handleTestProvider(provider.name);
                                                    }}
                                                    disabled={testingProviders.has(provider.name)}
                                                    className="btn btn-secondary text-xs px-3 py-1"
                                                >
                                                    {testingProviders.has(provider.name) ? 'Тест...' : 'Тест'}
                                                </button>
                                                {testResults[provider.name] && (
                                                    <div className="mt-2 text-xs">
                                                        {testResults[provider.name].success ? (
                                                            <div className="text-success">
                                                                ✅ {testResults[provider.name].events_found} событий
                                                            </div>
                                                        ) : (
                                                            <div className="text-error">
                                                                ❌ {testResults[provider.name].error}
                                                            </div>
                                                        )}
                                                    </div>
                                                )}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
