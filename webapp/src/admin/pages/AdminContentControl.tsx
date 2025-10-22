/**
 * Объединённая страница управления контентом (Новости + События)
 */

import { Card, CardContent } from '@/components/ui/Card';
import { Brain, Calendar } from 'lucide-react';
import { useState } from 'react';
import { AdminEventsControl } from '../components/AdminEventsControl';
import { AdminNewsControl } from '../components/AdminNewsControl';

type TabValue = 'news' | 'events';

export function AdminContentControl() {
    const [activeTab, setActiveTab] = useState<TabValue>('news');

    const tabs = [
        { value: 'news' as TabValue, label: 'Новости', icon: Brain },
        { value: 'events' as TabValue, label: 'События', icon: Calendar },
    ];

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-text">Управление контентом</h1>
                <p className="text-muted mt-2">
                    Загрузка и обработка новостей и событий
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
            {activeTab === 'news' ? <AdminNewsControl /> : <AdminEventsControl />}
        </div>
    );
}
