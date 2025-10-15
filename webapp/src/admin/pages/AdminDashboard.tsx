/**
 * Главная панель админа - Dashboard
 */

import { Users, FileText, Brain, TrendingUp } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { StatCard } from '../components/StatCard';
import { useAdminStats } from '../hooks/useAdminStats';

export function AdminDashboard() {
  const { data: stats, isLoading, error } = useAdminStats(30000); // Auto-refresh каждые 30 сек

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading statistics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-destructive">Failed to load statistics: {error.message}</div>
      </div>
    );
  }

  const statCards = [
    {
      icon: Users,
      label: 'Total Users',
      value: stats?.total_users || 0,
      color: 'text-blue-500'
    },
    {
      icon: FileText,
      label: 'News Today',
      value: stats?.news_today || 0,
      color: 'text-green-500'
    },
    {
      icon: Brain,
      label: 'Digests Today',
      value: stats?.digests_today || 0,
      color: 'text-purple-500'
    },
    {
      icon: TrendingUp,
      label: 'Avg Importance',
      value: stats?.avg_importance?.toFixed(2) || '0.00',
      color: 'text-orange-500'
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          System overview and statistics
        </p>
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
            <CardTitle>AI Quality (7 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Average Importance</span>
                  <span className="text-sm font-medium">{stats?.avg_importance?.toFixed(2) || '0.00'}</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-600 transition-all"
                    style={{ width: `${(stats?.avg_importance || 0) * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Average Credibility</span>
                  <span className="text-sm font-medium">{stats?.avg_credibility?.toFixed(2) || '0.00'}</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-cyan-600 transition-all"
                    style={{ width: `${(stats?.avg_credibility || 0) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">API Status</span>
                <span className="flex items-center gap-2 text-sm">
                  <span className="h-2 w-2 rounded-full bg-green-500"></span>
                  Online
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Database</span>
                <span className="flex items-center gap-2 text-sm">
                  <span className="h-2 w-2 rounded-full bg-green-500"></span>
                  Connected
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Last Update</span>
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


