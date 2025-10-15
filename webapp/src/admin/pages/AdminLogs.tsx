/**
 * Страница просмотра логов
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { useLogs, useLogFiles } from '../hooks/useLogs';
import { RefreshCw, Download } from 'lucide-react';

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
          <h1 className="text-3xl font-bold">System Logs</h1>
          <p className="text-muted-foreground mt-1">
            Real-time log viewer (auto-refreshes every 5s)
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => refetch()}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-4 py-2 bg-muted hover:bg-muted/80 rounded-lg transition-colors"
          >
            <Download className="h-4 w-4" />
            Download
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="flex gap-4 items-center">
        <div>
          <label className="text-sm text-muted-foreground mb-2 block">Log File</label>
          <select
            value={selectedFile}
            onChange={(e) => setSelectedFile(e.target.value)}
            className="px-4 py-2 bg-card border rounded-lg"
          >
            {logFiles?.files.map((file) => (
              <option key={file.name} value={file.name}>
                {file.name} ({(file.size / 1024).toFixed(2)} KB)
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="text-sm text-muted-foreground mb-2 block">Lines</label>
          <select
            value={linesCount}
            onChange={(e) => setLinesCount(Number(e.target.value))}
            className="px-4 py-2 bg-card border rounded-lg"
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
              {selectedFile} ({logs?.returned_lines || 0} / {logs?.total_lines || 0} lines)
            </CardTitle>
            {isLoading && (
              <span className="text-sm text-muted-foreground flex items-center gap-2">
                <RefreshCw className="h-3 w-3 animate-spin" />
                Loading...
              </span>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="bg-muted/50 rounded-lg p-4 font-mono text-sm max-h-[600px] overflow-y-auto">
            {logs?.logs.map((log, index) => (
              <div
                key={index}
                className={`py-1 ${
                  log.text.includes('ERROR') || log.text.includes('❌')
                    ? 'text-red-500'
                    : log.text.includes('WARNING') || log.text.includes('⚠️')
                    ? 'text-yellow-500'
                    : log.text.includes('✅') || log.text.includes('SUCCESS')
                    ? 'text-green-500'
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


