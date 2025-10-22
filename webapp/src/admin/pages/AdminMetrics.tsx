/**
 * Страница метрик - AI, пользователи и RSS Parser
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Activity, Brain, Rss } from 'lucide-react';
import { useState } from 'react';
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { SystemMonitor } from '../components/config/SystemMonitor';
import { RSSParserMetrics } from '../components/metrics/RSSParserMetrics';
import { useAIMetrics, useUserMetrics } from '../hooks/useMetrics';
import { CHART_COLORS_ARRAY } from '../utils/colors';

const COLORS = CHART_COLORS_ARRAY;

type TabValue = 'ai' | 'rss' | 'system';

export function AdminMetrics() {
    const [activeTab, setActiveTab] = useState<TabValue>('ai');
    const [days, setDays] = useState(7);
    const { data: aiMetrics, isLoading: aiLoading } = useAIMetrics(days);
    const { data: userMetrics, isLoading: userLoading } = useUserMetrics();

    const tabs = [
        { value: 'ai' as TabValue, label: 'AI и пользователи', icon: Brain },
        { value: 'rss' as TabValue, label: 'RSS Парсер', icon: Rss },
        { value: 'system' as TabValue, label: 'Мониторинг системы', icon: Activity },
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Метрики и аналитика</h1>
                <p className="text-muted mt-1">
                    Производительность AI, активность пользователей и мониторинг RSS парсера
                </p>
            </div>

            {/* Tabs */}
            <Card>
                <CardContent className="p-0">
                    <div className="flex border-b">
                        {tabs.map((tab) => (
                            <button
                                key={tab.value}
                                onClick={() => setActiveTab(tab.value)}
                                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${activeTab === tab.value
                                    ? 'border-b-2 border-primary text-primary bg-primary/5'
                                    : 'text-muted hover:text-text hover:bg-muted/50'
                                    }`}
                            >
                                <div className="flex items-center justify-center gap-2">
                                    <tab.icon className="w-4 h-4" />
                                    <span>{tab.label}</span>
                                </div>
                            </button>
                        ))}
                    </div>
                </CardContent>
            </Card>

            {/* Content */}
            {activeTab === 'ai' ? (
                <AIAndUserMetrics
                    days={days}
                    setDays={setDays}
                    aiMetrics={aiMetrics}
                    userMetrics={userMetrics}
                    isLoading={aiLoading || userLoading}
                />
            ) : activeTab === 'rss' ? (
                <RSSParserMetrics />
            ) : (
                <SystemMonitor />
            )}
        </div>
    );
}

// AI & User Metrics Component
function AIAndUserMetrics({ days, setDays, aiMetrics, userMetrics, isLoading }: any) {
    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-muted">Загрузка метрик...</div>
            </div>
        );
    }

    // Проверка на наличие данных
    const hasData = (aiMetrics?.total_items ?? 0) > 0 || (userMetrics?.total_users ?? 0) > 0;

    return (
        <div className="space-y-6">

            {/* No Data Warning */}
            {!hasData && (
                <Card className="bg-gradient-to-br from-warning/10 to-warning/5 border-warning/20">
                    <CardContent className="py-6">
                        <div className="text-center">
                            <div className="text-4xl mb-4">📊</div>
                            <h3 className="text-lg font-semibold mb-2">Нет данных для анализа</h3>
                            <p className="text-sm text-muted">
                                Запустите парсеры новостей и генерацию дайджестов для получения метрик
                            </p>
                            <code className="text-xs bg-muted px-2 py-1 rounded mt-2 inline-block">
                                python tools/fetch_and_store_news.py
                            </code>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Days Selector */}
            <div className="flex gap-2">
                {[7, 14, 30].map((d) => (
                    <button
                        key={d}
                        onClick={() => setDays(d)}
                        className={`px-4 py-2 rounded-lg transition-colors ${days === d
                            ? 'bg-primary text-white'
                            : 'bg-surface-alt hover:bg-muted text-text'
                            }`}
                    >
                        {d} дней
                    </button>
                ))}
            </div>

            {/* AI Metrics Summary */}
            <div className="grid gap-4 md:grid-cols-3">
                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm">Средняя важность</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">
                            {aiMetrics?.avg_importance?.toFixed(2) || '0.00'}
                        </div>
                        <p className="text-xs text-muted mt-1">
                            {aiMetrics?.total_items || 0} элементов проанализировано
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm">Средняя достоверность</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">
                            {aiMetrics?.avg_credibility?.toFixed(2) || '0.00'}
                        </div>
                        <p className="text-xs text-muted mt-1">
                            За последние {days} дней
                        </p>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="text-sm">Всего пользователей</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold">
                            {userMetrics?.total_users || 0}
                        </div>
                        <p className="text-xs text-muted mt-1">
                            {userMetrics?.total_subscriptions || 0} подписок
                        </p>
                    </CardContent>
                </Card>
            </div>

            {/* Charts */}
            <div className="grid gap-4 md:grid-cols-2">
                {/* Importance Distribution */}
                <Card>
                    <CardHeader>
                        <CardTitle>Распределение важности</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={aiMetrics?.importance_distribution || []}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="range" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="count" fill="#00A6C8" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* Credibility Distribution */}
                <Card>
                    <CardHeader>
                        <CardTitle>Распределение достоверности</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={aiMetrics?.credibility_distribution || []}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="range" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="count" fill="#7CFAD8" />
                            </BarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* Category Distribution */}
                <Card className="md:col-span-2">
                    <CardHeader>
                        <CardTitle>Подписки по категориям</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={(userMetrics?.category_distribution || []) as any}
                                    dataKey="count"
                                    nameKey="category"
                                    cx="50%"
                                    cy="50%"
                                    outerRadius={100}
                                    label
                                >
                                    {(userMetrics?.category_distribution || []).map((_item: any, index: number) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
