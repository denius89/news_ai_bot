/**
 * Компонент управления новостями для таба
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { useState } from 'react';
import {
    useNewsFetchConfig,
    useNewsFetchLogs,
    useNewsFetchStatus,
    useStartNewsFetch,
    useStopNewsFetch
} from '../hooks/useNewsFetch';
import type { NewsFetchSettings } from '../types/admin';
import { formatTime } from '../utils/formatters';
import { Toggle } from './ui/Toggle';

export function AdminNewsControl() {
    const [settings, setSettings] = useState<Partial<NewsFetchSettings>>({
        max_concurrent: 10,
        min_importance: 0.1,
        per_subcategory: 50,
        force_train: false,
        skip_train: false,
        categories: [],
        subcategories: [],
    });

    const { data: status, isLoading: statusLoading } = useNewsFetchStatus();
    const { data: config, isLoading: configLoading } = useNewsFetchConfig();
    const { data: logs, isLoading: logsLoading } = useNewsFetchLogs(50);

    const startMutation = useStartNewsFetch();
    const stopMutation = useStopNewsFetch();

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
            {/* 1️⃣ Статус загрузки новостей */}
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${status?.running ? 'bg-success' : 'bg-muted'}`} />
                        Статус загрузки новостей
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
                                {status?.last_run ? formatTime(status.last_run) : 'Никогда'}
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
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <label className="block text-sm font-medium mb-2">
                                Максимум одновременных запросов
                            </label>
                            <input
                                type="number"
                                min="1"
                                max="50"
                                value={settings.max_concurrent}
                                onChange={(e) => setSettings({ ...settings, max_concurrent: parseInt(e.target.value) })}
                                className="input w-full"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">
                                Минимальная важность
                            </label>
                            <input
                                type="number"
                                min="0"
                                max="1"
                                step="0.1"
                                value={settings.min_importance}
                                onChange={(e) => setSettings({ ...settings, min_importance: parseFloat(e.target.value) })}
                                className="input w-full"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium mb-2">
                                Новостей на подкатегорию
                            </label>
                            <input
                                type="number"
                                min="1"
                                max="200"
                                value={settings.per_subcategory}
                                onChange={(e) => setSettings({ ...settings, per_subcategory: parseInt(e.target.value) })}
                                className="input w-full"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-6">
                        <Toggle
                            checked={settings.force_train || false}
                            onChange={(checked) => setSettings({ ...settings, force_train: checked })}
                            label="Принудительное обучение"
                        />
                        <Toggle
                            checked={settings.skip_train || false}
                            onChange={(checked) => setSettings({ ...settings, skip_train: checked })}
                            label="Пропустить обучение"
                        />
                    </div>
                </CardContent>
            </Card>

            {/* 3️⃣ Категории и подкатегории */}
            <Card>
                <CardHeader>
                    <CardTitle>Категории и подкатегории</CardTitle>
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

                    {/* Подкатегории */}
                    {settings.categories && settings.categories.length > 0 && config?.settings?.category_structure && (
                        <div className="space-y-4">
                            <h4 className="text-sm font-medium text-muted">Подкатегории категории {settings.categories.join(', ')}</h4>
                            {settings.categories.map((cat) => {
                                const subcategories = config.settings.category_structure[cat] || [];
                                if (subcategories.length === 0) return null;

                                return (
                                    <div key={cat} className="space-y-2">
                                        <div className="flex items-center gap-2">
                                            <h5 className="text-sm font-medium text-muted">{cat}</h5>
                                            <div className="flex-1 h-px bg-border"></div>
                                        </div>
                                        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                                            {subcategories.map((sub) => (
                                                <button
                                                    key={`${cat}:${sub}`}
                                                    type="button"
                                                    onClick={() => {
                                                        const set = new Set(settings.subcategories || []);
                                                        if (set.has(sub)) set.delete(sub); else set.add(sub);
                                                        setSettings({ ...settings, subcategories: Array.from(set) });
                                                    }}
                                                    className={`btn w-full ${(settings.subcategories || []).includes(sub) ? 'btn-primary' : 'btn-secondary'}`}
                                                >
                                                    {sub}
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
