/**
 * AdminLogViewer component
 * Reusable log viewer with search, filter, and auto-scroll
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { useEffect, useRef, useState } from 'react';

interface LogEntry {
    text: string;
    timestamp?: string;
}

interface AdminLogViewerProps {
    logs: LogEntry[];
    title?: string;
    searchable?: boolean;
    filterable?: boolean;
    autoScroll?: boolean;
    maxHeight?: string;
    onRefresh?: () => void;
    isLoading?: boolean;
}

const parseLogLevel = (text: string): string => {
    if (text.includes('ERROR') || text.includes('❌')) return 'ERROR';
    if (text.includes('WARNING') || text.includes('⚠️')) return 'WARNING';
    if (text.includes('✅') || text.includes('SUCCESS')) return 'SUCCESS';
    return 'INFO';
};

const getLogLevelColor = (level: string): string => {
    switch (level) {
        case 'ERROR': return 'text-error bg-error/10';
        case 'WARNING': return 'text-warning bg-warning/10';
        case 'SUCCESS': return 'text-success bg-success/10';
        default: return 'text-text';
    }
};

export function AdminLogViewer({
    logs,
    title = 'Logs',
    searchable = true,
    filterable = true,
    autoScroll: autoScrollProp = true,
    maxHeight = '600px',
    onRefresh,
    isLoading = false,
}: AdminLogViewerProps) {
    const [searchTerm, setSearchTerm] = useState('');
    const [logLevel, setLogLevel] = useState('all');
    const [autoScroll, setAutoScroll] = useState(autoScrollProp);
    const logsEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll effect
    useEffect(() => {
        if (autoScroll && logsEndRef.current) {
            logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs, autoScroll]);

    // Filter logs
    const filteredLogs = logs.filter((log) => {
        // Search filter
        if (searchTerm && !log.text.toLowerCase().includes(searchTerm.toLowerCase())) {
            return false;
        }

        // Level filter
        if (logLevel !== 'all') {
            const level = parseLogLevel(log.text);
            return level === logLevel;
        }

        return true;
    });

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <CardTitle>{title} ({filteredLogs.length} / {logs.length})</CardTitle>
                    {isLoading && (
                        <span className="text-sm text-muted">Loading...</span>
                    )}
                </div>
            </CardHeader>
            <CardContent>
                {/* Controls */}
                {(searchable || filterable) && (
                    <div className="flex gap-2 mb-3">
                        {searchable && (
                            <input
                                type="text"
                                placeholder="🔍 Search logs..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="input flex-1 text-sm"
                            />
                        )}
                        {filterable && (
                            <select
                                value={logLevel}
                                onChange={(e) => setLogLevel(e.target.value)}
                                className="input text-sm"
                            >
                                <option value="all">All Levels</option>
                                <option value="INFO">ℹ️ INFO</option>
                                <option value="WARNING">⚠️ WARNING</option>
                                <option value="ERROR">❌ ERROR</option>
                                <option value="SUCCESS">✅ SUCCESS</option>
                            </select>
                        )}
                        <button
                            onClick={() => setAutoScroll(!autoScroll)}
                            className={`btn btn-sm ${autoScroll ? 'btn-primary' : 'btn-secondary'}`}
                        >
                            {autoScroll ? '✅ Auto' : '⬇️ Auto'}
                        </button>
                        {onRefresh && (
                            <button
                                onClick={onRefresh}
                                className="btn btn-sm btn-secondary"
                                disabled={isLoading}
                            >
                                🔄 Refresh
                            </button>
                        )}
                    </div>
                )}

                {/* Logs Display */}
                <div
                    className="bg-muted/50 rounded-lg p-4 font-mono text-xs overflow-y-auto"
                    style={{ maxHeight }}
                >
                    {filteredLogs.length > 0 ? (
                        <>
                            {filteredLogs.map((log, index) => {
                                const level = parseLogLevel(log.text);
                                const colorClass = getLogLevelColor(level);

                                return (
                                    <div key={index} className={`py-1 rounded px-2 mb-1 ${colorClass}`}>
                                        {log.text}
                                    </div>
                                );
                            })}
                            <div ref={logsEndRef} />
                        </>
                    ) : (
                        <div className="text-center text-muted py-4">
                            No logs match your filters
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
