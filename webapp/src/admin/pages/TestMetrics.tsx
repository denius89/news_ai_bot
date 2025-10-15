/**
 * Тестовая страница для проверки API метрик
 */

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';

export function TestMetrics() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Fetching metrics from /admin/api/metrics/ai...');
        const response = await fetch('/admin/api/metrics/ai');
        console.log('Response status:', response.status);
        const json = await response.json();
        console.log('Response data:', json);
        setData(json);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching metrics:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="text-red-500">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Test Metrics API</h1>
      
      <Card>
        <CardHeader>
          <CardTitle>API Response</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="bg-muted p-4 rounded text-xs overflow-auto">
            {JSON.stringify(data, null, 2)}
          </pre>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Parsed Data</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div>Total Items: <strong>{data?.total_items ?? 'N/A'}</strong></div>
            <div>Avg Importance: <strong>{data?.avg_importance ?? 'N/A'}</strong></div>
            <div>Avg Credibility: <strong>{data?.avg_credibility ?? 'N/A'}</strong></div>
            <div>Days Analyzed: <strong>{data?.days_analyzed ?? 'N/A'}</strong></div>
            <div>
              Importance Distribution: <strong>{data?.importance_distribution?.length ?? 0} items</strong>
            </div>
            <div>
              Credibility Distribution: <strong>{data?.credibility_distribution?.length ?? 0} items</strong>
            </div>
          </div>
        </CardContent>
      </Card>

      {data?.total_items === 0 && (
        <Card className="bg-yellow-500/10 border-yellow-500/20">
          <CardContent className="py-6">
            <div className="text-center">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-lg font-semibold mb-2">Нет данных для анализа</h3>
              <p className="text-sm text-muted-foreground">
                API работает, но в БД нет дайджестов за последние 7 дней
              </p>
              <code className="text-xs bg-muted px-2 py-1 rounded mt-2 inline-block">
                python tools/fetch_and_store_news.py
              </code>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
