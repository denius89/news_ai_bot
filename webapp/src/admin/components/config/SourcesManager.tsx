/**
 * Компонент для управления источниками новостей
 */

import { useState } from 'react';
import { useSources, useTestSource } from '../../hooks/useSources';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/Tabs';
import { Newspaper, Calendar } from 'lucide-react';
import { EventsProviders } from './EventsProviders';

export function SourcesManager() {
  const { data: sources, isLoading, error } = useSources();
  const testSource = useTestSource();
  const [testUrl, setTestUrl] = useState('');
  const [testResult, setTestResult] = useState<any>(null);
  const [activeSubTab, setActiveSubTab] = useState<'news' | 'events'>('news');

  if (isLoading) {
    return <div className="p-8">Загрузка источников...</div>;
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="text-red-500">Ошибка загрузки источников: {error.message}</div>
      </div>
    );
  }

  if (!sources) {
    return <div className="p-8">Нет данных</div>;
  }

  const handleTestSource = async () => {
    if (!testUrl) return;
    
    try {
      const result = await testSource.mutateAsync({ url: testUrl });
      setTestResult(result);
    } catch (err: any) {
      setTestResult({ success: false, error: err.message });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Sources Management</h2>
      </div>
      
      {/* Подвкладки с Lucide Icons */}
      <Tabs value={activeSubTab} defaultValue="news" onValueChange={(v) => setActiveSubTab(v as 'news' | 'events')}>
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="news" className="flex items-center gap-2">
            <Newspaper className="w-4 h-4" />
            News Sources
          </TabsTrigger>
          <TabsTrigger value="events" className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            Events Providers
          </TabsTrigger>
        </TabsList>
        
        <TabsContent value="news">
          <div className="space-y-6 mt-6">

      {/* Статистика */}
      <Card>
        <CardHeader>
          <CardTitle>Статистика источников</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <div className="text-3xl font-bold text-green-600">{sources.statistics.categories}</div>
              <div className="text-sm text-muted-foreground">Категорий</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-blue-600">{sources.statistics.subcategories}</div>
              <div className="text-sm text-muted-foreground">Подкатегорий</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-purple-600">{sources.statistics.sources}</div>
              <div className="text-sm text-muted-foreground">Источников</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-orange-600">{sources.statistics.avg_sources_per_subcategory}</div>
              <div className="text-sm text-muted-foreground">Среднее / подкатегория</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Тест парсера */}
      <Card>
        <CardHeader>
          <CardTitle>Тест RSS парсера</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex gap-2">
              <input
                type="url"
                placeholder="https://example.com/feed"
                className="flex-1 px-3 py-2 border rounded"
                value={testUrl}
                onChange={(e) => setTestUrl(e.target.value)}
              />
              <Button 
                onClick={handleTestSource}
                disabled={!testUrl || testSource.isPending}
              >
                {testSource.isPending ? 'Тестирование...' : 'Тест'}
              </Button>
            </div>

            {testResult && (
              <div className={`p-4 rounded border ${testResult.success ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
                {testResult.success ? (
                  <div>
                    <div className="font-semibold mb-2">✅ Парсер работает!</div>
                    <div className="text-sm">Найдено новостей: {testResult.items_count}</div>
                    {testResult.sample && testResult.sample.length > 0 && (
                      <div className="mt-3">
                        <div className="text-xs font-semibold mb-2">Примеры:</div>
                        <div className="space-y-2">
                          {testResult.sample.map((item: any, idx: number) => (
                            <div key={idx} className="text-xs bg-background p-2 rounded">
                              <div className="font-semibold">{item.title}</div>
                              <div className="text-muted-foreground mt-1">{item.published_at}</div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div>
                    <div className="font-semibold mb-1">❌ Ошибка</div>
                    <div className="text-sm">{testResult.error}</div>
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Структура источников */}
      <Card>
        <CardHeader>
          <CardTitle>Структура источников</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(sources.structure).map(([category, subcategories]) => (
              <div key={category} className="border rounded p-4">
                <h3 className="text-lg font-semibold capitalize mb-3">{category}</h3>
                <div className="space-y-3">
                  {Object.entries(subcategories).map(([subcat, data]) => (
                    <div key={subcat} className="pl-4 border-l-2 border-muted">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium">{subcat}</span>
                        <Badge variant="outline" className="text-xs">
                          {data.sources.length} источников
                        </Badge>
                      </div>
                      <div className="space-y-1">
                        {data.sources.map((source, idx) => (
                          <div key={idx} className="text-sm text-muted-foreground flex items-center gap-2">
                            <span>•</span>
                            <span className="font-medium">{source.name}</span>
                            <span className="text-xs">({source.url})</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
          </div>
        </TabsContent>
        
        <TabsContent value="events">
          <div className="mt-6">
            <EventsProviders />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

