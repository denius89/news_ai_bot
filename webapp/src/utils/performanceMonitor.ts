// Performance Monitoring System
// Система мониторинга производительности PulseAI

import React from 'react';

interface PerformanceMetrics {
    // Core Web Vitals
    lcp?: number; // Largest Contentful Paint
    fid?: number; // First Input Delay
    cls?: number; // Cumulative Layout Shift

    // Navigation Timing
    domContentLoaded?: number;
    loadComplete?: number;

    // Custom Metrics
    componentRenderTime?: number;
    apiResponseTime?: number;
    imageLoadTime?: number;

    // Device Info
    deviceType?: 'mobile' | 'tablet' | 'desktop';
    connectionType?: string;
    memoryUsage?: number;
}

interface PerformanceConfig {
    enabled: boolean;
    sampleRate: number; // 0-1, процент записей для отправки
    endpoint?: string;
    batchSize: number;
    flushInterval: number; // ms
}

class PerformanceMonitor {
    private config: PerformanceConfig;
    private metrics: PerformanceMetrics[] = [];
    private observers: PerformanceObserver[] = [];
    private isInitialized = false;

    constructor(config: Partial<PerformanceConfig> = {}) {
        this.config = {
            enabled: true,
            sampleRate: 0.1, // 10% записей
            batchSize: 10,
            flushInterval: 30000, // 30 секунд
            ...config
        };
    }

    // Инициализация мониторинга
    init() {
        if (this.isInitialized || !this.config.enabled) return;

        console.log('[Performance] Initializing performance monitoring');

        this.setupCoreWebVitals();
        this.setupNavigationTiming();
        this.setupCustomMetrics();
        this.setupPeriodicFlush();

        this.isInitialized = true;
    }

    // Настройка Core Web Vitals
    private setupCoreWebVitals() {
        // LCP - Largest Contentful Paint
        if ('PerformanceObserver' in window) {
            try {
                const lcpObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries.length > 0 ? entries[entries.length - 1] : null;
                    if (lastEntry) {
                        this.recordMetric({ lcp: lastEntry.startTime });
                    }
                });
                lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
                this.observers.push(lcpObserver);
            } catch (error) {
                console.warn('[Performance] LCP observer not supported:', error);
            }

            // FID - First Input Delay
            try {
                const fidObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach((entry: any) => {
                        this.recordMetric({ fid: entry.processingStart - entry.startTime });
                    });
                });
                fidObserver.observe({ entryTypes: ['first-input'] });
                this.observers.push(fidObserver);
            } catch (error) {
                console.warn('[Performance] FID observer not supported:', error);
            }

            // CLS - Cumulative Layout Shift
            try {
                let clsValue = 0;
                const clsObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach((entry: any) => {
                        if (!entry.hadRecentInput) {
                            clsValue += entry.value;
                        }
                    });
                    this.recordMetric({ cls: clsValue });
                });
                clsObserver.observe({ entryTypes: ['layout-shift'] });
                this.observers.push(clsObserver);
            } catch (error) {
                console.warn('[Performance] CLS observer not supported:', error);
            }
        }
    }

    // Настройка Navigation Timing
    private setupNavigationTiming() {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

                if (navigation) {
                    this.recordMetric({
                        domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
                        loadComplete: navigation.loadEventEnd - navigation.fetchStart
                    });
                }
            }, 0);
        });
    }

    // Настройка кастомных метрик
    private setupCustomMetrics() {
        // Мониторинг API запросов
        this.interceptFetch();

        // Мониторинг изображений
        this.interceptImageLoading();
    }

    // Перехват fetch запросов
    private interceptFetch() {
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const startTime = performance.now();

            try {
                const response = await originalFetch(...args);
                const endTime = performance.now();

                this.recordMetric({
                    apiResponseTime: endTime - startTime
                });

                return response;
            } catch (error) {
                const endTime = performance.now();

                this.recordMetric({
                    apiResponseTime: endTime - startTime
                });

                throw error;
            }
        };
    }

    // Перехват загрузки изображений
    private interceptImageLoading() {
        const originalImage = window.Image;
        const self = this;

        window.Image = function (width?: number, height?: number) {
            const img = new originalImage(width, height);
            const startTime = performance.now();

            img.addEventListener('load', () => {
                const endTime = performance.now();
                self.recordMetric({
                    imageLoadTime: endTime - startTime
                });
            });

            return img;
        } as any;
    }

    // Запись метрики
    recordMetric(metric: Partial<PerformanceMetrics>) {
        if (!this.config.enabled) return;

        // Добавляем информацию об устройстве
        const enrichedMetric: PerformanceMetrics = {
            ...metric,
            deviceType: this.getDeviceType(),
            connectionType: this.getConnectionType(),
            memoryUsage: this.getMemoryUsage()
        };

        this.metrics.push(enrichedMetric);

        // Проверяем, нужно ли отправить данные
        if (this.metrics.length >= this.config.batchSize) {
            this.flush();
        }
    }

    // Определение типа устройства
    private getDeviceType(): 'mobile' | 'tablet' | 'desktop' {
        const width = window.innerWidth;
        if (width < 768) return 'mobile';
        if (width < 1024) return 'tablet';
        return 'desktop';
    }

    // Получение типа соединения
    private getConnectionType(): string {
        const connection = (navigator as any).connection || (navigator as any).mozConnection || (navigator as any).webkitConnection;
        return connection?.effectiveType || 'unknown';
    }

    // Получение использования памяти
    private getMemoryUsage(): number | undefined {
        const memory = (performance as any).memory;
        return memory ? memory.usedJSHeapSize : undefined;
    }

    // Периодическая отправка данных
    private setupPeriodicFlush() {
        setInterval(() => {
            if (this.metrics.length > 0) {
                this.flush();
            }
        }, this.config.flushInterval);
    }

    // Отправка данных
    private async flush() {
        if (this.metrics.length === 0) return;

        // Применяем sample rate
        const shouldSend = Math.random() < this.config.sampleRate;
        if (!shouldSend) {
            this.metrics = [];
            return;
        }

        const metricsToSend = [...this.metrics];
        this.metrics = [];

        try {
            if (this.config.endpoint) {
                await fetch(this.config.endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        timestamp: Date.now(),
                        url: window.location.href,
                        userAgent: navigator.userAgent,
                        metrics: metricsToSend
                    })
                });
            }

            // Локальное логирование для отладки
            console.log('[Performance] Metrics sent:', metricsToSend);
        } catch (error) {
            console.error('[Performance] Failed to send metrics:', error);
            // Возвращаем метрики в очередь при ошибке
            this.metrics.unshift(...metricsToSend);
        }
    }

    // Ручная отправка метрик
    async sendMetrics() {
        await this.flush();
    }

    // Получение текущих метрик
    getMetrics(): PerformanceMetrics[] {
        return [...this.metrics];
    }

    // Очистка метрик
    clearMetrics() {
        this.metrics = [];
    }

    // Остановка мониторинга
    destroy() {
        this.observers.forEach(observer => observer.disconnect());
        this.observers = [];
        this.metrics = [];
        this.isInitialized = false;
    }
}

// Создаем глобальный экземпляр
export const performanceMonitor = new PerformanceMonitor({
    enabled: process.env.NODE_ENV === 'production',
    sampleRate: 0.1,
    batchSize: 5,
    flushInterval: 30000
});

// Хук для React компонентов
export const usePerformanceMonitor = () => {
    const startTime = React.useRef<number>(0);

    const startMeasurement = React.useCallback(() => {
        startTime.current = performance.now();
    }, []);

    const endMeasurement = React.useCallback(() => {
        if (startTime.current > 0) {
            const renderTime = performance.now() - startTime.current;
            performanceMonitor.recordMetric({
                componentRenderTime: renderTime
            });
            startTime.current = 0;
        }
    }, []);

    return { startMeasurement, endMeasurement };
};

export default PerformanceMonitor;
