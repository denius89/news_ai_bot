/**
 * Telegram Bot Admin Page
 */

import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { Activity, Bot, Clock, Settings, Users } from 'lucide-react';
import { useEffect, useState } from 'react';

interface RateLimit {
    limit: number;
    window: number;
    description: string;
}

interface Metrics {
    total_handler_calls: number;
    total_handler_errors: number;
    active_users: number;
    average_execution_time_ms: number;
    top_commands: Record<string, number>;
}

interface FeatureDetails {
    enabled: boolean;
    name: string;
    description: string;
    details: string;
}

interface BotStatus {
    bot_running: boolean;
    metrics: Metrics;
    rate_limits: Record<string, RateLimit>;
    features: Record<string, boolean>;
    features_details: Record<string, FeatureDetails>;
    timestamp: string;
}

export function AdminTelegramBot() {
    const [botStatus, setBotStatus] = useState<BotStatus | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchBotStatus();
    }, []);

    const fetchBotStatus = async () => {
        try {
            setLoading(true);
            const response = await fetch('/admin/telegram/api/status');
            if (!response.ok) {
                throw new Error('Failed to fetch bot status');
            }
            const data = await response.json();
            setBotStatus(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    const reloadConfig = async () => {
        try {
            const response = await fetch('/admin/telegram/reload-config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                throw new Error('Failed to reload config');
            }

            // Refresh status
            await fetchBotStatus();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        }
    };

    const updateRateLimit = async (limitName: string, limit: number, window: number) => {
        try {
            const response = await fetch('/admin/telegram/rate-limits/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    rate_limits: {
                        [limitName]: { limit, window }
                    }
                })
            });

            if (!response.ok) {
                throw new Error('Failed to update rate limit');
            }

            // Reload config to apply changes
            await reloadConfig();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        }
    };

    const toggleFeature = async (featureName: string, enabled: boolean) => {
        try {
            const response = await fetch('/admin/telegram/features/toggle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    feature: featureName,
                    enabled: enabled
                })
            });

            if (!response.ok) {
                throw new Error('Failed to toggle feature');
            }

            // Reload config to apply changes
            await reloadConfig();
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center">
                    <Bot className="h-8 w-8 animate-spin mx-auto mb-4" />
                    <p>Загрузка статуса бота...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-center text-red-500">
                    <Bot className="h-8 w-8 mx-auto mb-4" />
                    <p>Ошибка: {error}</p>
                    <Button onClick={fetchBotStatus} className="mt-4">
                        Попробовать снова
                    </Button>
                </div>
            </div>
        );
    }

    if (!botStatus) {
        return (
            <div className="text-center">
                <p>Нет данных о статусе бота</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-3">
                    <Bot className="h-8 w-8" />
                    Telegram Bot Admin
                </h1>
                <p className="text-muted-foreground mt-2">
                    Управление настройками и мониторинг Telegram-бота
                </p>
            </div>

            {/* Status Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Статус бота</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">
                            <Badge variant={botStatus.bot_running ? "default" : "destructive"}>
                                {botStatus.bot_running ? "Работает" : "Остановлен"}
                            </Badge>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Всего запросов</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{botStatus.metrics.total_handler_calls}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Ошибки</CardTitle>
                        <Activity className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold text-red-500">{botStatus.metrics.total_handler_errors}</div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Активные пользователи</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{botStatus.metrics.active_users}</div>
                    </CardContent>
                </Card>
            </div>

            {/* Tabs */}
            <Tabs defaultValue="rate-limits" className="space-y-4">
                <TabsList>
                    <TabsTrigger value="rate-limits">Rate Limits</TabsTrigger>
                    <TabsTrigger value="features">Функции</TabsTrigger>
                </TabsList>

                <TabsContent value="rate-limits" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Clock className="h-5 w-5" />
                                Rate Limits
                            </CardTitle>
                            <CardDescription>
                                Настройка лимитов для команд бота
                                <br />
                                <span className="text-xs text-muted-foreground">
                                    💡 Рекомендуется 60 сек для нормальной работы
                                </span>
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            {Object.entries(botStatus.rate_limits).map(([name, config]) => (
                                <div key={name} className="flex items-center justify-between p-4 border rounded-lg">
                                    <div>
                                        <h3 className="font-medium">{config.description}</h3>
                                        <p className="text-sm text-muted-foreground">{name}</p>
                                    </div>
                                    <div className="flex items-center gap-4">
                                        <div className="text-right">
                                            <p className="text-sm">Лимит: <strong>{config.limit}</strong></p>
                                            <p className="text-sm">Окно: <strong>{config.window} сек</strong></p>
                                        </div>
                                        <div className="flex gap-2">
                                            <Button
                                                size="sm"
                                                variant={config.window === 30 ? "primary" : "outline"}
                                                onClick={() => updateRateLimit(name, config.limit, 30)}
                                            >
                                                30 сек
                                            </Button>
                                            <Button
                                                size="sm"
                                                variant={config.window === 60 ? "primary" : "outline"}
                                                onClick={() => updateRateLimit(name, config.limit, 60)}
                                            >
                                                1 мин
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </CardContent>
                    </Card>
                </TabsContent>

                <TabsContent value="features" className="space-y-4">
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Settings className="h-5 w-5" />
                                Функции бота
                            </CardTitle>
                            <CardDescription>
                                Управление функциями бота. Включение/выключение различных возможностей.
                            </CardDescription>
                        </CardHeader>
                        <CardContent>
                            <div className="space-y-4">
                                {Object.entries(botStatus.features_details).map(([key, feature]) => (
                                    <div key={key} className="p-4 border rounded-lg space-y-3">
                                        <div className="flex items-center justify-between">
                                            <div className="flex-1">
                                                <h3 className="font-medium text-lg">{feature.name}</h3>
                                                <p className="text-sm text-muted-foreground mt-1">
                                                    {feature.description}
                                                </p>
                                                <p className="text-xs text-muted-foreground mt-2">
                                                    {feature.details}
                                                </p>
                                            </div>
                                            <div className="flex items-center gap-3 ml-4">
                                                <Badge variant={feature.enabled ? "default" : "secondary"}>
                                                    {feature.enabled ? "Включено" : "Отключено"}
                                                </Badge>
                                                <Button
                                                    size="sm"
                                                    variant={feature.enabled ? "outline" : "primary"}
                                                    onClick={() => toggleFeature(key, !feature.enabled)}
                                                >
                                                    {feature.enabled ? "Отключить" : "Включить"}
                                                </Button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>

            {/* Refresh Button */}
            <div className="flex justify-end">
                <Button onClick={fetchBotStatus} variant="outline">
                    Обновить данные
                </Button>
            </div>
        </div>
    );
}
