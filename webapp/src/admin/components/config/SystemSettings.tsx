/**
 * Компонент для системных настроек
 */

import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { useEffect, useState } from 'react';
import { useAllConfig, useUpdateConfig } from '../../hooks/useConfig';

export function SystemSettings() {
    const { data: config, isLoading, error } = useAllConfig();
    const updateConfig = useUpdateConfig();

    const [newsFetchInterval, setNewsFetchInterval] = useState(30);
    const [maxDigestItems, setMaxDigestItems] = useState(10);
    const [notificationHour, setNotificationHour] = useState(9);
    const [apiRateLimit, setApiRateLimit] = useState(100);

    // Загрузка значений из БД
    useEffect(() => {
        if (config?.system) {
            setNewsFetchInterval(Number(config.system.news_fetch_interval?.value) || 30);
            setMaxDigestItems(Number(config.system.max_digest_items?.value) || 10);
            setNotificationHour(Number(config.system.notification_hour?.value) || 9);
            setApiRateLimit(Number(config.system.api_rate_limit?.value) || 100);
        }
    }, [config]);

    const handleSave = async () => {
        try {
            await updateConfig.mutateAsync({ category: 'system', key: 'news_fetch_interval', value: newsFetchInterval });
            await updateConfig.mutateAsync({ category: 'system', key: 'max_digest_items', value: maxDigestItems });
            await updateConfig.mutateAsync({ category: 'system', key: 'notification_hour', value: notificationHour });
            await updateConfig.mutateAsync({ category: 'system', key: 'api_rate_limit', value: apiRateLimit });

            alert('Системные настройки сохранены успешно!');
        } catch (err: any) {
            alert(`Ошибка сохранения: ${err.message}`);
        }
    };

    if (isLoading) {
        return <div className="p-8">Загрузка настроек...</div>;
    }

    if (error) {
        return (
            <div className="p-8">
                <div className="text-error">Ошибка загрузки настроек: {error.message}</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Системные настройки</h2>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Настройки новостей</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">
                                News Fetch Interval (минуты)
                            </label>
                            <input
                                type="number"
                                min="5"
                                max="120"
                                step="5"
                                value={newsFetchInterval}
                                onChange={(e) => setNewsFetchInterval(Number(e.target.value))}
                                className="input w-full"
                            />
                            <p className="text-xs text-muted mt-1">
                                {config?.system?.news_fetch_interval?.description}
                            </p>
                        </div>

                        <div>
                            <label className="block text-sm font-medium mb-2">
                                Max Digest Items
                            </label>
                            <input
                                type="number"
                                min="5"
                                max="50"
                                step="5"
                                value={maxDigestItems}
                                onChange={(e) => setMaxDigestItems(Number(e.target.value))}
                                className="input w-full"
                            />
                            <p className="text-xs text-muted mt-1">
                                {config?.system?.max_digest_items?.description}
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Настройки уведомлений</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">
                                Notification Hour (0-23)
                            </label>
                            <input
                                type="number"
                                min="0"
                                max="23"
                                value={notificationHour}
                                onChange={(e) => setNotificationHour(Number(e.target.value))}
                                className="input w-full"
                            />
                            <p className="text-xs text-muted mt-1">
                                {config?.system?.notification_hour?.description}
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Настройки API</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">
                                API Rate Limit (запросов в минуту)
                            </label>
                            <input
                                type="number"
                                min="10"
                                max="1000"
                                step="10"
                                value={apiRateLimit}
                                onChange={(e) => setApiRateLimit(Number(e.target.value))}
                                className="input w-full"
                            />
                            <p className="text-xs text-muted mt-1">
                                {config?.system?.api_rate_limit?.description}
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>

            <div className="flex justify-end">
                <Button
                    onClick={handleSave}
                    disabled={updateConfig.isPending}
                    className="px-6"
                >
                    {updateConfig.isPending ? 'Сохранение...' : 'Сохранить настройки'}
                </Button>
            </div>
        </div>
    );
}
