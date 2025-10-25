// Performance Metrics Display Component
// Компонент для отображения метрик производительности (только для разработки)

import React, { useEffect, useState } from 'react';
import { performanceMonitor } from '../utils/performanceMonitor';

interface PerformanceDisplayProps {
    enabled?: boolean;
}

export const PerformanceDisplay: React.FC<PerformanceDisplayProps> = ({
    enabled = process.env.NODE_ENV === 'development'
}) => {
    const [metrics, setMetrics] = useState<any[]>([]);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        if (!enabled) return;

        const interval = setInterval(() => {
            const currentMetrics = performanceMonitor.getMetrics();
            setMetrics(currentMetrics);
        }, 1000);

        return () => clearInterval(interval);
    }, [enabled]);

    if (!enabled) return null;

    const latestMetrics = metrics[metrics.length - 1] || {};

    return (
        <>
            {/* Toggle Button */}
            <button
                onClick={() => setIsVisible(!isVisible)}
                className="fixed bottom-20 right-4 z-50 bg-black/80 text-white text-xs px-2 py-1 rounded"
                style={{ fontSize: '10px' }}
            >
                Perf {isVisible ? '▼' : '▲'}
            </button>

            {/* Metrics Panel */}
            {isVisible && (
                <div className="fixed bottom-24 right-4 z-50 bg-black/90 text-white text-xs p-3 rounded-lg max-w-xs">
                    <div className="font-bold mb-2">Performance Metrics</div>

                    <div className="space-y-1">
                        {latestMetrics.lcp && (
                            <div>LCP: {latestMetrics.lcp.toFixed(2)}ms</div>
                        )}
                        {latestMetrics.fid && (
                            <div>FID: {latestMetrics.fid.toFixed(2)}ms</div>
                        )}
                        {latestMetrics.cls && (
                            <div>CLS: {latestMetrics.cls.toFixed(4)}</div>
                        )}
                        {latestMetrics.domContentLoaded && (
                            <div>DOM Ready: {latestMetrics.domContentLoaded.toFixed(2)}ms</div>
                        )}
                        {latestMetrics.loadComplete && (
                            <div>Load Complete: {latestMetrics.loadComplete.toFixed(2)}ms</div>
                        )}
                        {latestMetrics.apiResponseTime && (
                            <div>API: {latestMetrics.apiResponseTime.toFixed(2)}ms</div>
                        )}
                        {latestMetrics.imageLoadTime && (
                            <div>Image: {latestMetrics.imageLoadTime.toFixed(2)}ms</div>
                        )}
                        {latestMetrics.componentRenderTime && (
                            <div>Render: {latestMetrics.componentRenderTime.toFixed(2)}ms</div>
                        )}
                    </div>

                    <div className="mt-2 pt-2 border-t border-gray-600">
                        <div>Device: {latestMetrics.deviceType}</div>
                        <div>Connection: {latestMetrics.connectionType}</div>
                        {latestMetrics.memoryUsage && (
                            <div>Memory: {(latestMetrics.memoryUsage / 1024 / 1024).toFixed(1)}MB</div>
                        )}
                    </div>

                    <div className="mt-2 pt-2 border-t border-gray-600">
                        <div>Metrics Count: {metrics.length}</div>
                        <button
                            onClick={() => performanceMonitor.sendMetrics()}
                            className="bg-blue-600 text-white px-2 py-1 rounded text-xs mt-1"
                        >
                            Send Metrics
                        </button>
                        <button
                            onClick={() => performanceMonitor.clearMetrics()}
                            className="bg-red-600 text-white px-2 py-1 rounded text-xs mt-1 ml-1"
                        >
                            Clear
                        </button>
                    </div>
                </div>
            )}
        </>
    );
};

export default PerformanceDisplay;
