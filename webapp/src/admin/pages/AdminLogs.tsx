/**
 * Страница просмотра логов
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Download, RefreshCw } from 'lucide-react';
import { useState } from 'react';
import { useLogFiles, useLogs } from '../hooks/useLogs';

export function AdminLogs() {
    const [selectedFile, setSelectedFile] = useState('app.log');
    const [linesCount, setLinesCount] = useState(100);
    const { data: logs, isLoading, refetch } = useLogs(selectedFile, linesCount, 5000);
    const { data: logFiles } = useLogFiles();

    const handleDownload = () => {
        if (!logs) return;

        const content = logs.logs.map(log => log.text).join('\n');
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${selectedFile}_${new Date().toISOString()}.log`;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold">Системные логи</h1>
                    <p className="text-muted mt-1">
                        Просмотр логов в реальном времени (обновление каждые 5 сек)
                    </p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => refetch()}
                        className="btn btn-primary flex items-center gap-2"
                    >
                        <RefreshCw className="h-4 w-4" />
                        Обновить
                    </button>
                    <button
                        onClick={handleDownload}
                        className="btn btn-secondary flex items-center gap-2"
                    >
                        <Download className="h-4 w-4" />
                        Скачать
                    </button>
                </div>
            </div>

            {/* Controls */}
            <div className="flex gap-4 items-center">
                <div>
                    <label className="text-sm text-muted mb-2 block">Файл логов</label>
                    <select
                        value={selectedFile}
                        onChange={(e) => setSelectedFile(e.target.value)}
                        className="input"
                    >
                        {logFiles?.files.map((file) => (
                            <option key={file.name} value={file.name}>
                                {file.name} ({(file.size / 1024).toFixed(2)} KB)
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="text-sm text-muted mb-2 block">Строк</label>
                    <select
                        value={linesCount}
                        onChange={(e) => setLinesCount(Number(e.target.value))}
                        className="input"
                    >
                        <option value={50}>50</option>
                        <option value={100}>100</option>
                        <option value={200}>200</option>
                        <option value={500}>500</option>
                    </select>
                </div>
            </div>

            {/* Logs Display */}
            <Card>
                <CardHeader>
                    <div className="flex items-center justify-between">
                        <CardTitle>
                            {selectedFile} ({logs?.returned_lines || 0} / {logs?.total_lines || 0} строк)
                        </CardTitle>
                        {isLoading && (
                            <span className="text-sm text-muted flex items-center gap-2">
                                <RefreshCw className="h-3 w-3 animate-spin" />
                                Загрузка...
                            </span>
                        )}
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="bg-muted/50 rounded-lg p-4 font-mono text-sm max-h-[600px] overflow-y-auto">
                        {logs?.logs.map((log, index) => (
                            <div
                                key={index}
                                className={`py-1 ${log.text.includes('ERROR') || log.text.includes('❌')
                                    ? 'text-error'
                                    : log.text.includes('WARNING') || log.text.includes('⚠️')
                                        ? 'text-warning'
                                        : log.text.includes('✅') || log.text.includes('SUCCESS')
                                            ? 'text-success'
                                            : 'text-foreground'
                                    }`}
                            >
                                {log.text}
                            </div>
                        ))}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
