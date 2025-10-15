/**
 * Компонент для настройки AI параметров
 */

import { useState, useEffect } from 'react';
import { useAllConfig, useUpdateConfig } from '../../hooks/useConfig';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export function AISettings() {
  const { data: config, isLoading, error } = useAllConfig();
  const updateConfig = useUpdateConfig();

  const [modelSummary, setModelSummary] = useState('');
  const [modelScoring, setModelScoring] = useState('');
  const [maxTokens, setMaxTokens] = useState(800);
  const [minImportance, setMinImportance] = useState(0.6);
  const [minCredibility, setMinCredibility] = useState(0.7);

  // Загрузка значений из БД
  useEffect(() => {
    if (config?.ai) {
      setModelSummary(config.ai.model_summary?.value || 'gpt-4o-mini');
      setModelScoring(config.ai.model_scoring?.value || 'gpt-4o-mini');
      setMaxTokens(Number(config.ai.max_tokens?.value) || 800);
      setMinImportance(Number(config.ai.min_importance?.value) || 0.6);
      setMinCredibility(Number(config.ai.min_credibility?.value) || 0.7);
    }
  }, [config]);

  const handleSave = async () => {
    try {
      await updateConfig.mutateAsync({ category: 'ai', key: 'model_summary', value: modelSummary });
      await updateConfig.mutateAsync({ category: 'ai', key: 'model_scoring', value: modelScoring });
      await updateConfig.mutateAsync({ category: 'ai', key: 'max_tokens', value: maxTokens });
      await updateConfig.mutateAsync({ category: 'ai', key: 'min_importance', value: minImportance });
      await updateConfig.mutateAsync({ category: 'ai', key: 'min_credibility', value: minCredibility });
      
      alert('Настройки сохранены успешно!');
    } catch (err: any) {
      alert(`Ошибка сохранения: ${err.message}`);
    }
  };

  if (isLoading) {
    return <div className="p-8">Загрузка настроек...</div>;
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="text-red-500">Ошибка загрузки настроек: {error.message}</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">AI Settings</h2>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Модели AI</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Model for Summarization
            </label>
            <select
              className="w-full px-3 py-2 border rounded"
              value={modelSummary}
              onChange={(e) => setModelSummary(e.target.value)}
            >
              <option value="gpt-4o-mini">gpt-4o-mini</option>
              <option value="gpt-4o">gpt-4o</option>
              <option value="gpt-4-turbo">gpt-4-turbo</option>
              <option value="claude-3-sonnet">claude-3-sonnet</option>
              <option value="claude-3-opus">claude-3-opus</option>
            </select>
            <p className="text-xs text-muted-foreground mt-1">
              {config?.ai?.model_summary?.description}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Model for Scoring
            </label>
            <select
              className="w-full px-3 py-2 border rounded"
              value={modelScoring}
              onChange={(e) => setModelScoring(e.target.value)}
            >
              <option value="gpt-4o-mini">gpt-4o-mini</option>
              <option value="gpt-4o">gpt-4o</option>
              <option value="gpt-4-turbo">gpt-4-turbo</option>
              <option value="claude-3-sonnet">claude-3-sonnet</option>
              <option value="claude-3-opus">claude-3-opus</option>
            </select>
            <p className="text-xs text-muted-foreground mt-1">
              {config?.ai?.model_scoring?.description}
            </p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Параметры генерации</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div>
            <label className="block text-sm font-medium mb-2">
              Max Tokens: {maxTokens}
            </label>
            <input
              type="range"
              min="100"
              max="4000"
              step="100"
              value={maxTokens}
              onChange={(e) => setMaxTokens(Number(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground mt-1">
              {config?.ai?.max_tokens?.description}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Min Importance: {minImportance.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={minImportance}
              onChange={(e) => setMinImportance(Number(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground mt-1">
              {config?.ai?.min_importance?.description}
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Min Credibility: {minCredibility.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={minCredibility}
              onChange={(e) => setMinCredibility(Number(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-muted-foreground mt-1">
              {config?.ai?.min_credibility?.description}
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button 
          onClick={handleSave}
          disabled={updateConfig.isPending}
          className="px-6"
        >
          {updateConfig.isPending ? 'Сохранение...' : 'Сохранить настройки'}
        </Button>
      </div>
    </div>
  );
}

