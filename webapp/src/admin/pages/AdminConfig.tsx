/**
 * Страница управления конфигурацией с табами
 */

import { Card, CardContent } from '@/components/ui/Card';
import { Bot, FileText, Newspaper, Settings } from 'lucide-react';
import { useState } from 'react';
import { AISettings } from '../components/config/AISettings';
import { PromptsViewer } from '../components/config/PromptsViewer';
import { SourcesManager } from '../components/config/SourcesManager';
import { SystemSettings } from '../components/config/SystemSettings';

type TabValue = 'ai' | 'prompts' | 'sources' | 'system';

export function AdminConfig() {
    const [activeTab, setActiveTab] = useState<TabValue>('ai');

    const tabs = [
        { value: 'ai' as TabValue, label: 'Настройки AI', icon: Bot },
        { value: 'prompts' as TabValue, label: 'Промпты', icon: FileText },
        { value: 'sources' as TabValue, label: 'Источники', icon: Newspaper },
        { value: 'system' as TabValue, label: 'Система', icon: Settings },
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
            default:
                return <AISettings />;
        }
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold">Конфигурация системы</h1>
                <p className="text-muted mt-1">
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
                                className={`flex-1 px-4 py-3 text-sm font-medium transition-colors ${activeTab === tab.value
                                    ? 'border-b-2 border-primary text-primary bg-primary/5'
                                    : 'text-muted hover:text-text hover:bg-muted/50'
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
