/**
 * Страница метрик - AI и пользователи
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { useAIMetrics, useUserMetrics } from '../hooks/useMetrics';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export function AdminMetrics() {
  const [days, setDays] = useState(7);
  const { data: aiMetrics, isLoading: aiLoading } = useAIMetrics(days);
  const { data: userMetrics, isLoading: userLoading } = useUserMetrics();

  if (aiLoading || userLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-muted-foreground">Loading metrics...</div>
      </div>
    );
  }

  // Проверка на наличие данных
  const hasData = (aiMetrics?.total_items ?? 0) > 0 || (userMetrics?.total_users ?? 0) > 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Metrics & Analytics</h1>
        <p className="text-muted-foreground mt-1">
          AI performance and user engagement
        </p>
      </div>
      
      {/* No Data Warning */}
      {!hasData && (
        <Card className="bg-gradient-to-br from-yellow-500/10 to-orange-500/10 border-yellow-500/20">
          <CardContent className="py-6">
            <div className="text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-semibold mb-2">Нет данных для анализа</h3>
              <p className="text-sm text-muted-foreground">
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
            className={`px-4 py-2 rounded-lg transition-colors ${
              days === d
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted hover:bg-muted/80'
            }`}
          >
            {d} days
          </button>
        ))}
      </div>

      {/* AI Metrics Summary */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Avg Importance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {aiMetrics?.avg_importance?.toFixed(2) || '0.00'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {aiMetrics?.total_items || 0} items analyzed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Avg Credibility</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {aiMetrics?.avg_credibility?.toFixed(2) || '0.00'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Last {days} days
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Total Users</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold">
              {userMetrics?.total_users || 0}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {userMetrics?.total_subscriptions || 0} subscriptions
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Importance Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Importance Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={aiMetrics?.importance_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#22c55e" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Credibility Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Credibility Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={aiMetrics?.credibility_distribution || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="range" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Category Distribution */}
        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle>Subscriptions by Category</CardTitle>
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
                  {(userMetrics?.category_distribution || []).map((_item, index) => (
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

