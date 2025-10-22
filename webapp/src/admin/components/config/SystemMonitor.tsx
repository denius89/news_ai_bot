/**
 * Компонент для мониторинга системы
 */

import { Badge } from '@/components/ui/Badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Progress } from '@/components/ui/Progress';
import { useSystemStatus } from '../../hooks/useSystemStatus';

export function SystemMonitor() {
    const { data: status, isLoading, error } = useSystemStatus();

    if (isLoading) {
        return <div className="p-8">Загрузка статуса системы...</div>;
    }

    if (error) {
        return (
            <div className="p-8">
                <div className="text-error">Ошибка загрузки статуса: {error.message}</div>
            </div>
        );
    }

    if (!status) {
        return <div className="p-8">Нет данных</div>;
    }

    const getStatusBadge = (serviceStatus: string) => {
        if (serviceStatus === 'ok') {
            return <Badge variant="success">Работает</Badge>;
        }
        return <Badge variant="error">Недоступен</Badge>;
    };

    const getResourceColor = (percent: number) => {
        if (percent < 60) return 'bg-success';
        if (percent < 80) return 'bg-warning';
        return 'bg-error';
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Мониторинг системы</h2>
                <div className="text-sm text-muted">
                    Обновлено: {new Date(status.timestamp).toLocaleTimeString('ru-RU')}
                </div>
            </div>

            {/* Сервисы */}
            <Card>
                <CardHeader>
                    <CardTitle>Статус сервисов</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between p-3 border rounded">
                            <div className="flex items-center gap-3">
                                <div className="text-2xl">🌐</div>
                                <div>
                                    <div className="font-semibold">Flask WebApp</div>
                                    <div className="text-sm text-muted">
                                        PID файл: {status.services.flask.pid_file}
                                    </div>
                                </div>
                            </div>
                            {getStatusBadge(status.services.flask.status)}
                        </div>

                        <div className="flex items-center justify-between p-3 border rounded">
                            <div className="flex items-center gap-3">
                                <div className="text-2xl">🤖</div>
                                <div>
                                    <div className="font-semibold">Telegram Bot</div>
                                    <div className="text-sm text-muted">
                                        PID файл: {status.services.bot.pid_file}
                                    </div>
                                </div>
                            </div>
                            {getStatusBadge(status.services.bot.status)}
                        </div>

                        <div className="flex items-center justify-between p-3 border rounded">
                            <div className="flex items-center gap-3">
                                <div className="text-2xl">💾</div>
                                <div>
                                    <div className="font-semibold">PostgreSQL Database</div>
                                    <div className="text-sm text-muted">
                                        Supabase / PostgreSQL
                                    </div>
                                </div>
                            </div>
                            {getStatusBadge(status.services.database.status)}
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Ресурсы */}
            <Card>
                <CardHeader>
                    <CardTitle>Системные ресурсы</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-6">
                        {/* CPU */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <div className="text-sm font-semibold">Загрузка CPU</div>
                                <div className="text-sm font-mono">{status.resources.cpu_percent}%</div>
                            </div>
                            <Progress
                                value={status.resources.cpu_percent}
                                className={getResourceColor(status.resources.cpu_percent)}
                            />
                        </div>

                        {/* Memory */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <div className="text-sm font-semibold">Использование памяти</div>
                                <div className="text-sm font-mono">
                                    {status.resources.memory_used_mb.toFixed(0)} MB /
                                    {' '}{(status.resources.memory_used_mb + status.resources.memory_available_mb).toFixed(0)} MB
                                    {' '}({status.resources.memory_percent}%)
                                </div>
                            </div>
                            <Progress
                                value={status.resources.memory_percent}
                                className={getResourceColor(status.resources.memory_percent)}
                            />
                        </div>

                        {/* Disk */}
                        <div>
                            <div className="flex items-center justify-between mb-2">
                                <div className="text-sm font-semibold">Использование диска</div>
                                <div className="text-sm font-mono">
                                    {status.resources.disk_free_gb} GB free ({status.resources.disk_percent}% used)
                                </div>
                            </div>
                            <Progress
                                value={status.resources.disk_percent}
                                className={getResourceColor(status.resources.disk_percent)}
                            />
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Uptime */}
            <Card>
                <CardHeader>
                    <CardTitle>Информация о системе</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <div className="text-sm text-muted mb-1">Время работы</div>
                            <div className="text-2xl font-mono">{status.uptime}</div>
                        </div>
                        <div>
                            <div className="text-sm text-muted mb-1">Время работы (секунды)</div>
                            <div className="text-2xl font-mono">{status.uptime_seconds.toLocaleString()}</div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
