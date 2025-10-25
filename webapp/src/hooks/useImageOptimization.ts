import { useCallback, useEffect, useRef, useState } from 'react';

interface UseImageOptimizationOptions {
    width?: number;
    height?: number;
    quality?: number;
    format?: 'webp' | 'jpeg' | 'png' | 'auto';
    lazy?: boolean;
    priority?: boolean;
}

interface UseImageOptimizationReturn {
    src: string;
    isLoaded: boolean;
    hasError: boolean;
    isInView: boolean;
    ref: React.RefObject<HTMLImageElement>;
    handleLoad: () => void;
    handleError: () => void;
}

export const useImageOptimization = (
    originalSrc: string,
    options: UseImageOptimizationOptions = {}
): UseImageOptimizationReturn => {
    const {
        width,
        height,
        quality = 80,
        format = 'webp',
        lazy = true,
        priority = false
    } = options;

    const [isLoaded, setIsLoaded] = useState(false);
    const [hasError, setHasError] = useState(false);
    const [isInView, setIsInView] = useState(priority || !lazy);

    const ref = useRef<HTMLImageElement>(null);
    const observerRef = useRef<IntersectionObserver | null>(null);

    // Оптимизация URL изображения
    const optimizeUrl = useCallback((url: string): string => {
        if (!url) return '';

        // Если это уже оптимизированный URL, возвращаем как есть
        if (url.includes('?') || url.includes('&')) {
            return url;
        }

        const params = new URLSearchParams();
        if (width) params.append('w', width.toString());
        if (height) params.append('h', height.toString());
        if (quality) params.append('q', quality.toString());
        if (format !== 'auto') params.append('fm', format);

        const queryString = params.toString();
        return queryString ? `${url}?${queryString}` : url;
    }, [width, height, quality, format]);

    // Intersection Observer для ленивой загрузки
    useEffect(() => {
        if (!lazy || priority || isInView) return;

        if (!ref.current) return;

        observerRef.current = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        setIsInView(true);
                        observerRef.current?.disconnect();
                    }
                });
            },
            {
                rootMargin: '50px',
                threshold: 0.1
            }
        );

        observerRef.current.observe(ref.current);

        return () => {
            observerRef.current?.disconnect();
        };
    }, [lazy, priority, isInView]);

    const handleLoad = useCallback(() => {
        setIsLoaded(true);
        setHasError(false);
    }, []);

    const handleError = useCallback(() => {
        setHasError(true);
        setIsLoaded(false);
    }, []);

    return {
        src: optimizeUrl(originalSrc),
        isLoaded,
        hasError,
        isInView,
        ref,
        handleLoad,
        handleError
    };
};

// Хук для предзагрузки изображений
export const useImagePreloader = () => {
    const [preloadedImages, setPreloadedImages] = useState<Set<string>>(new Set());
    const [isPreloading, setIsPreloading] = useState(false);

    const preloadImage = useCallback((src: string): Promise<void> => {
        return new Promise((resolve, reject) => {
            if (preloadedImages.has(src)) {
                resolve();
                return;
            }

            const img = new Image();
            img.onload = () => {
                setPreloadedImages(prev => new Set([...prev, src]));
                resolve();
            };
            img.onerror = reject;
            img.src = src;
        });
    }, [preloadedImages]);

    const preloadImages = useCallback(async (srcs: string[]): Promise<void> => {
        setIsPreloading(true);
        try {
            await Promise.all(srcs.map(src => preloadImage(src)));
        } finally {
            setIsPreloading(false);
        }
    }, [preloadImage]);

    return {
        preloadedImages,
        isPreloading,
        preloadImage,
        preloadImages
    };
};

// Хук для мониторинга производительности изображений
export const useImagePerformance = () => {
    const [metrics, setMetrics] = useState<{
        loadTime: number;
        decodedTime: number;
        naturalWidth: number;
        naturalHeight: number;
    } | null>(null);

    const measureImagePerformance = useCallback((img: HTMLImageElement) => {
        const startTime = performance.now();

        const handleLoad = () => {
            const loadTime = performance.now() - startTime;

            setMetrics({
                loadTime,
                decodedTime: (img as any).decodedBodySize || 0,
                naturalWidth: img.naturalWidth,
                naturalHeight: img.naturalHeight
            });
        };

        img.addEventListener('load', handleLoad, { once: true });

        return () => {
            img.removeEventListener('load', handleLoad);
        };
    }, []);

    return {
        metrics,
        measureImagePerformance
    };
};
