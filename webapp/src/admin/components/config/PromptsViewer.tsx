/**
 * Компонент для просмотра AI промптов (read-only)
 */

import { usePrompts } from '../../hooks/usePrompts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export function PromptsViewer() {
  const { data: prompts, isLoading, error } = usePrompts();

  if (isLoading) {
    return <div className="p-8">Загрузка промптов...</div>;
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="text-red-500">Ошибка загрузки промптов: {error.message}</div>
      </div>
    );
  }

  if (!prompts) {
    return <div className="p-8">Нет данных</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">AI Prompts</h2>
        <Badge variant="secondary">View Only</Badge>
      </div>

      <div className="space-y-6">
        {/* Стили */}
        <Card>
          <CardHeader>
            <CardTitle>Стили дайджестов</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(prompts.styles).map(([key, style]) => (
                <div key={key} className="border-l-4 border-green-500 pl-4 py-2">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-lg">{style.name}</h3>
                    <Badge variant="outline" className="text-xs">{key}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{style.description}</p>
                  
                  <div className="mt-3">
                    <div className="text-xs font-semibold text-muted-foreground mb-1">Характеристики:</div>
                    <ul className="list-disc list-inside text-sm space-y-1">
                      {style.characteristics.map((char, idx) => (
                        <li key={idx}>{char}</li>
                      ))}
                    </ul>
                  </div>
                  
                  <div className="mt-3 bg-muted p-3 rounded text-sm">
                    <div className="font-semibold mb-1">Expert Persona:</div>
                    <div>{style.expert_persona}</div>
                    <div className="mt-2 font-semibold mb-1">Writing Style:</div>
                    <div className="italic">{style.writing_style}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Тона */}
        <Card>
          <CardHeader>
            <CardTitle>Тона повествования</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(prompts.tones).map(([key, tone]) => (
                <div key={key} className="border-l-4 border-blue-500 pl-4 py-2">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="font-semibold text-lg">{tone.name}</h3>
                    <Badge variant="outline" className="text-xs">{key}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mb-2">{tone.description}</p>
                  
                  <div className="mt-3">
                    <div className="text-xs font-semibold text-muted-foreground mb-1">Voice:</div>
                    <div className="text-sm italic mb-2">{tone.voice}</div>
                    
                    <div className="text-xs font-semibold text-muted-foreground mb-1">Характеристики:</div>
                    <ul className="list-disc list-inside text-sm space-y-1">
                      {tone.characteristics.map((char, idx) => (
                        <li key={idx}>{char}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Info */}
        <Card className="bg-yellow-500/10 border-yellow-500/20">
          <CardContent className="py-4">
            <div className="flex items-start gap-3">
              <div className="text-2xl">ℹ️</div>
              <div>
                <h3 className="font-semibold mb-1">Только просмотр</h3>
                <p className="text-sm text-muted-foreground">
                  Промпты находятся в файле <code className="bg-muted px-1 py-0.5 rounded">digests/prompts_v2.py</code>.
                  Для редактирования требуется прямое изменение кода. Функция редактирования через UI планируется в v2.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

