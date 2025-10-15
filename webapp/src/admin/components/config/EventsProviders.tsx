/**
 * Компонент для отображения провайдеров событий
 */

import { useEventsProviders, useTestEventsProvider } from '../../hooks/useEventsConfig';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Calendar, Trophy, Bitcoin, Laptop, Activity } from 'lucide-react';

export function EventsProviders() {
  const { data: eventsData, isLoading, error } = useEventsProviders();
  const testProvider = useTestEventsProvider();
  
  if (isLoading) return <div className="p-8">Загрузка провайдеров событий...</div>;
  if (error) return <div className="p-8 text-red-500">Ошибка: {error.message}</div>;
  
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-2">
        <Calendar className="w-6 h-6" />
        <h2 className="text-2xl font-bold">Events Providers</h2>
      </div>
      
      {/* Статистика по категориям */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Trophy className="w-8 h-8 text-green-500" />
              <div>
                <div className="text-2xl font-bold">{eventsData?.categories?.sports || 0}</div>
                <div className="text-sm text-muted-foreground">Sports Events</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Bitcoin className="w-8 h-8 text-orange-500" />
              <div>
                <div className="text-2xl font-bold">{eventsData?.categories?.crypto || 0}</div>
                <div className="text-sm text-muted-foreground">Crypto Events</div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <Laptop className="w-8 h-8 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">{eventsData?.categories?.tech || 0}</div>
                <div className="text-sm text-muted-foreground">Tech Events</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      {/* Список провайдеров */}
      <div className="grid gap-4">
        {eventsData?.providers?.map((provider: any) => (
          <Card key={provider.name}>
            <CardHeader>
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <Activity className="w-5 h-5" />
                  <CardTitle>{provider.name}</CardTitle>
                </div>
                <Badge variant={provider.status === 'active' ? 'default' : 'secondary'}>
                  {provider.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Category:</span>
                  <span className="text-sm font-medium">{provider.category}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-muted-foreground">Events Count:</span>
                  <span className="text-sm font-medium">{provider.events_count}</span>
                </div>
                <Button 
                  onClick={() => testProvider.mutate(provider.name)}
                  disabled={testProvider.isPending}
                  className="w-full mt-2"
                  size="sm"
                >
                  {testProvider.isPending ? 'Testing...' : 'Test Provider'}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
