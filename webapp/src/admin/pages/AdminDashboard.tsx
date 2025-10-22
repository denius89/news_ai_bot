/**
 * Главная панель админа - Dashboard
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Brain, FileText, TrendingUp, Users } from 'lucide-react';
import { StatCard } from '../components/StatCard';
import { useAdminStats } from '../hooks/useAdminStats';

export function AdminDashboard() {
    const { data: stats, isLoading, error } = useAdminStats(30000); // Auto-refresh каждые 30 сек

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-muted">Загрузка статистики...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="text-error">Не удалось загрузить статистику: {error.message}</div>
            </div>
        );
    }

    const statCards = [
        {
            icon: Users,
            label: 'Всего пользователей',
            value: stats?.total_users || 0,
            iconColor: 'primary' as const,
        },
        {
            icon: FileText,
            label: 'Новостей сегодня',
            value: stats?.news_today || 0,
            iconColor: 'accent' as const,
        },
        {
            icon: Brain,
            label: 'Дайджестов сегодня',
            value: stats?.digests_today || 0,
            iconColor: 'purple' as const,
        },
        {
            icon: TrendingUp,
            label: 'Средняя важность',
            value: stats?.avg_importance?.toFixed(2) || '0.00',
            iconColor: 'warning' as const,
        },
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Панель</h1>
                <p className="text-muted mt-1">Обзор системы и ключевые метрики</p>
            </div>

            {/* Stats Grid */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                {statCards.map((stat, i) => (
                    <StatCard
                        key={stat.label}
                        {...stat}
                        delay={i * 0.1}
                    />
                ))}
            </div>

            {/* AI Quality Metrics */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card>
                    <CardHeader>
                        <CardTitle>Качество AI (7 дней)</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div>
                                <div className="flex justify-between mb-2">
                                    <span className="text-sm text-muted">Средняя важность</span>
                                    <span className="text-sm font-medium">{stats?.avg_importance?.toFixed(2) || '0.00'}</span>
                                </div>
                                <div className="h-2 bg-muted rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-primary to-accent transition-all"
                                        style={{ width: `${(stats?.avg_importance || 0) * 100}%` }}
                                    />
                                </div>
                            </div>

                            <div>
                                <div className="flex justify-between mb-2">
                                    <span className="text-sm text-muted">Средняя достоверность</span>
                                    <span className="text-sm font-medium">{stats?.avg_credibility?.toFixed(2) || '0.00'}</span>
                                </div>
                                <div className="h-2 bg-muted rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-gradient-to-r from-primary to-primary-700 transition-all"
                                        style={{ width: `${(stats?.avg_credibility || 0) * 100}%` }}
                                    />
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle>Статус системы</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-muted">Статус API</span>
                                <span className="flex items-center gap-2 text-sm">
                                    <span className="h-2 w-2 rounded-full bg-success"></span>
                                    Онлайн
                                </span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-muted">База данных</span>
                                <span className="flex items-center gap-2 text-sm">
                                    <span className="h-2 w-2 rounded-full bg-success"></span>
                                    Подключена
                                </span>
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-muted">Последнее обновление</span>
                                <span className="text-sm">
                                    {new Date().toLocaleTimeString()}
                                </span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
