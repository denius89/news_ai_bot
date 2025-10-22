/**
 * Компонент управления событиями для таба
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { useState } from 'react';
import {
    useEventsFetchConfig,
    useEventsFetchLogs,
    useEventsFetchStatus,
    useStartEventsFetch,
    useStopEventsFetch
} from '../hooks/useEventsFetch';
import type { EventsFetchSettings } from '../types/admin';
import { Toggle } from './ui/Toggle';

export function AdminEventsControl() {
    const [settings, setSettings] = useState<Partial<EventsFetchSettings>>({
        days_ahead: 7,
        dry_run: false,
        categories: [],
        providers: [],
    });

    const { data: status, isLoading: statusLoading } = useEventsFetchStatus();
    const { data: config, isLoading: configLoading } = useEventsFetchConfig();
    const { data: logs, isLoading: logsLoading } = useEventsFetchLogs(50);

    const startMutation = useStartEventsFetch();
    const stopMutation = useStopEventsFetch();

    const handleStart = () => {
        startMutation.mutate(settings);
    };

    if (statusLoading || configLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-muted">Загрузка...</div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* 1️⃣ Статус загрузки событий */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${status?.running ? 'bg-success' : 'bg-muted'}`} />
                        Статус загрузки событий
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <div className="text-sm text-muted">Статус</div>
                            <div className="font-semibold">
                                {status?.running ? 'Запущено' : 'Остановлено'}
                            </div>
                        </div>
                        <div>
                            <div className="text-sm text-muted">Последний запуск</div>
                            <div className="font-semibold">
                                {status?.last_run ? new Date(status.last_run).toLocaleString() : 'Никогда'}
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* 2️⃣ Глобальные параметры */}
            <Card>
                <CardHeader>
                    <CardTitle>Глобальные параметры</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div className="flex items-center gap-4">
                            <div className="w-48">
                                <label className="block text-sm font-medium mb-2">
                                    Дней вперед
                                </label>
                                <input
                                    type="number"
                                    min="1"
                                    max="30"
                                    value={settings.days_ahead}
                                    onChange={(e) => setSettings({ ...settings, days_ahead: parseInt(e.target.value) })}
                                    className="input w-full"
                                />
                            </div>
                        </div>
                        <div>
                            <Toggle
                                checked={settings.dry_run || false}
                                onChange={(checked) => setSettings({ ...settings, dry_run: checked })}
                                label="Тестовый режим (без сохранения)"
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* 3️⃣ Категории и провайдеры */}
            <Card>
                <CardHeader>
                    <CardTitle>Категории и провайдеры</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Категории */}
                    {Array.isArray(config?.settings?.available_categories) && (
                        <div className="space-y-3">
                            <h4 className="text-sm font-medium text-muted">Категории</h4>
                            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                                {config.settings.available_categories.map((category: string) => (
                                    <button
                                        key={category}
                                        type="button"
                                        onClick={() => {
                                            const set = new Set(settings.categories || []);
                                            if (set.has(category)) set.delete(category); else set.add(category);
                                            setSettings({ ...settings, categories: Array.from(set) });
                                        }}
                                        className={`btn w-full ${(settings.categories || []).includes(category) ? 'btn-primary' : 'btn-secondary'}`}
                                    >
                                        {category}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Разделитель */}
                    <div className="border-t border-border"></div>

                    {/* Провайдеры */}
                    {settings.categories && settings.categories.length > 0 && config?.settings?.available_providers && (
                        <div className="space-y-4">
                            <h4 className="text-sm font-medium text-muted">Провайдеры категории {settings.categories.join(', ')}</h4>
                            {settings.categories.map((cat) => {
                                const providers = (config.settings.available_providers[cat] || []).map((p) => p.name);
                                if (providers.length === 0) return null;

                                return (
                                    <div key={cat} className="space-y-2">
                                        <div className="flex items-center gap-2">
                                            <h5 className="text-sm font-medium text-muted">{cat}</h5>
                                            <div className="flex-1 h-px bg-border"></div>
                                        </div>
                                        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                                            {providers.map((provider) => (
                                                <button
                                                    key={provider}
                                                    type="button"
                                                    onClick={() => {
                                                        const set = new Set(settings.providers || []);
                                                        if (set.has(provider)) set.delete(provider); else set.add(provider);
                                                        setSettings({ ...settings, providers: Array.from(set) });
                                                    }}
                                                    className={`btn w-full ${(settings.providers || []).includes(provider) ? 'btn-primary' : 'btn-secondary'}`}
                                                >
                                                    {provider}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Управление */}
            <Card>
                <CardHeader>
                    <CardTitle>Управление</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex gap-2 flex-wrap">
                        <button
                            onClick={handleStart}
                            disabled={startMutation.isPending || status?.running}
                            className="btn btn-primary flex-1"
                        >
                            {startMutation.isPending ? 'Запуск...' : 'Запустить'}
                        </button>
                        <button
                            onClick={() => stopMutation.mutate()}
                            disabled={stopMutation.isPending || !status?.running}
                            className="btn btn-secondary flex-1"
                        >
                            {stopMutation.isPending ? 'Остановка...' : 'Остановить'}
                        </button>
                    </div>
                </CardContent>
            </Card>

            {/* Логи */}
            <Card>
                <CardHeader>
                    <CardTitle>Логи</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="bg-muted/10 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm">
                        {logsLoading ? (
                            <div className="text-muted">Загрузка логов...</div>
                        ) : logs ? (
                            <div className="text-text">Логи загружены</div>
                        ) : (
                            <div className="text-muted">Нет логов</div>
                        )}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
