/**
 * RSS Parser Metrics component
 * Performance, sources status, and AI optimization metrics
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { useState } from 'react';
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { useRSSLiveMetrics, useRSSParserMetrics } from '../../hooks/useMetrics';

export function RSSParserMetrics() {
    const [hours, setHours] = useState(24);
    const { data: rssMetrics, isLoading: rssLoading } = useRSSParserMetrics(hours);
    const { data: liveMetrics, isLoading: liveLoading } = useRSSLiveMetrics();

    if (rssLoading || liveLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-muted">Загрузка метрик RSS парсера...</div>
            </div>
        );
    }

    const hasData = (rssMetrics?.performance?.total_processed ?? 0) > 0;

    return (
        <div className="space-y-6">
            {/* No Data Warning */}
            {!hasData && (
                <Card className="bg-gradient-to-br from-warning/10 to-warning/10 border-warning/20">
                    <CardContent className="py-6">
                        <div className="text-center">
                            <div className="text-4xl mb-4">📡</div>
                            <h3 className="text-lg font-semibold mb-2">RSS Parser не активен</h3>
                            <p className="text-sm text-muted">
                                Запустите RSS парсер для получения метрик
                            </p>
                            <code className="text-xs bg-muted px-2 py-1 rounded mt-2 inline-block">
                                python tools/news/fetch_and_train.py
                            </code>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Live Status */}
            {liveMetrics && (
                <div className="grid gap-4 md:grid-cols-4">
                    <Card className={liveMetrics.status === 'active' ? 'border-success/50 bg-success/5' : ''}>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm">Статус</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className={`text-2xl font-bold ${liveMetrics.status === 'active' ? 'text-success' : 'text-muted'}`}>
                                {liveMetrics.status === 'active' ? '🟢 Активен' : '⚪ Ожидание'}
                            </div>
                            <p className="text-xs text-muted mt-1">
                                {liveMetrics.current_sources_processing} источников обрабатывается
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm">Новости за час</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {liveMetrics.news_last_hour}
                            </div>
                            <p className="text-xs text-muted mt-1">
                                обработано
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm">AI запросы</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold">
                                {rssMetrics?.ai_optimization?.total_ai_requests || 0}
                            </div>
                            <p className="text-xs text-muted mt-1">
                                период {hours}ч
                            </p>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader className="pb-2">
                            <CardTitle className="text-sm">Экономия</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="text-2xl font-bold text-success">
                                ${rssMetrics?.ai_optimization?.estimated_cost_savings_usd?.toFixed(4) || '0.0000'}
                            </div>
                            <p className="text-xs text-muted mt-1">
                                оценка экономии
                            </p>
                        </CardContent>
                    </Card>
                </div>
            )}

            {/* Time Period Selector */}
            <div className="flex gap-2">
                {[6, 12, 24, 72].map((h) => (
                    <button
                        key={h}
                        onClick={() => setHours(h)}
                        className={`px-4 py-2 rounded-lg transition-colors ${hours === h
                            ? 'bg-primary text-white'
                            : 'bg-surface-alt hover:bg-muted text-text'
                            }`}
                    >
                        {h}h
                    </button>
                ))}
            </div>

            {/* Performance Metrics */}
            {rssMetrics && (
                <div className="grid gap-6 md:grid-cols-2">
                    {/* Sources Status */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Производительность источников</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {rssMetrics.sources_status.slice(0, 10).map((source) => (
                                    <div key={source.source} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                                        <div className="flex-1">
                                            <div className="font-medium text-sm truncate">{source.source}</div>
                                            <div className="text-xs text-muted">
                                                {source.items_processed} элементов • {source.success_rate}% успеха
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <div className={`w-2 h-2 rounded-full ${source.status === 'healthy' ? 'bg-success' :
                                                source.status === 'degraded' ? 'bg-warning' : 'bg-error'
                                                }`} />
                                            <div className="text-xs font-mono">
                                                {source.avg_importance.toFixed(2)}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    {/* AI Optimization */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Оптимизация AI</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <div className="text-sm text-muted">Локальные предсказания</div>
                                        <div className="text-2xl font-bold text-success">
                                            {rssMetrics.ai_optimization.local_prediction_rate}%
                                        </div>
                                    </div>
                                    <div>
                                        <div className="text-sm text-muted">Экономия токенов</div>
                                        <div className="text-2xl font-bold">
                                            {Math.round(rssMetrics.ai_optimization.estimated_tokens_saved / 1000)}K
                                        </div>
                                    </div>
                                </div>

                                <div className="pt-4 border-t">
                                    <div className="text-sm text-muted mb-2">Распределение запросов</div>
                                    <ResponsiveContainer width="100%" height={150}>
                                        <BarChart data={[
                                            { name: 'OpenAI', value: rssMetrics.ai_optimization.total_ai_requests, fill: '#DC2626' },
                                            { name: 'Локальная ML', value: rssMetrics.ai_optimization.estimated_saved_requests, fill: '#16A34A' }
                                        ]}>
                                            <XAxis dataKey="name" />
                                            <YAxis />
                                            <Tooltip />
                                            <Bar dataKey="value" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    {/* Cache Performance */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Производительность кэша</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <div className="text-sm text-muted">Hit Rate</div>
                                    <div className="text-3xl font-bold text-primary">
                                        {rssMetrics.cache_stats.hit_rate.toFixed(1)}%
                                    </div>
                                </div>
                                <div>
                                    <div className="text-sm text-muted">Размер кэша</div>
                                    <div className="text-3xl font-bold">
                                        {rssMetrics.cache_stats.size_mb.toFixed(1)} MB
                                    </div>
                                </div>
                            </div>
                            <div className="mt-4 text-xs text-muted">
                                {rssMetrics.cache_stats.total_requests} всего запросов
                            </div>
                        </CardContent>
                    </Card>

                    {/* Error Summary */}
                    <Card>
                        <CardHeader>
                            <CardTitle>Ошибки</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-3">
                                {rssMetrics.errors.map((error, index) => (
                                    <div key={index} className="flex items-center justify-between p-2 rounded bg-muted/30">
                                        <div className="text-sm font-medium">{error.error_type}</div>
                                        <div className="text-xs text-muted">
                                            {error.count} случаев
                                        </div>
                                    </div>
                                ))}
                                {rssMetrics.errors.length === 0 && (
                                    <div className="text-center py-4 text-muted">
                                        🎉 Ошибок нет
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                </div>
            )}
        </div>
    );
}
