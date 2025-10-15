/**
 * Страница управления конфигурацией с табами
 */

import { useState } from 'react';
import { Card, CardContent } from '@/components/ui/Card';
import { AISettings } from '../components/config/AISettings';
import { PromptsViewer } from '../components/config/PromptsViewer';
import { SourcesManager } from '../components/config/SourcesManager';
import { SystemSettings } from '../components/config/SystemSettings';
import { SystemMonitor } from '../components/config/SystemMonitor';
import { Bot, FileText, Newspaper, Settings, Activity } from 'lucide-react';

type TabValue = 'ai' | 'prompts' | 'sources' | 'system' | 'monitor';

export function AdminConfig() {
  const [activeTab, setActiveTab] = useState<TabValue>('ai');

  const tabs = [
    { value: 'ai' as TabValue, label: 'AI Settings', icon: Bot },
    { value: 'prompts' as TabValue, label: 'Prompts', icon: FileText },
    { value: 'sources' as TabValue, label: 'Sources', icon: Newspaper },
    { value: 'system' as TabValue, label: 'System', icon: Settings },
    { value: 'monitor' as TabValue, label: 'Monitor', icon: Activity },
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'ai':
        return <AISettings />;
      case 'prompts':
        return <PromptsViewer />;
      case 'sources':
        return <SourcesManager />;
      case 'system':
        return <SystemSettings />;
      case 'monitor':
        return <SystemMonitor />;
      default:
        return <AISettings />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">System Configuration</h1>
        <p className="text-muted-foreground mt-1">
          Управление AI моделями, промптами, источниками и системными настройками
        </p>
      </div>

      {/* Tabs */}
      <Card>
        <CardContent className="p-0">
          <div className="flex border-b">
            {tabs.map((tab) => (
              <button
                key={tab.value}
                onClick={() => setActiveTab(tab.value)}
                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${
                  activeTab === tab.value
                    ? 'border-b-2 border-green-500 text-green-600 bg-green-500/5'
                    : 'text-muted-foreground hover:text-foreground hover:bg-muted/50'
                }`}
              >
                <div className="flex items-center justify-center gap-2">
                  <tab.icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Content */}
      <div>{renderContent()}</div>
    </div>
  );
}
