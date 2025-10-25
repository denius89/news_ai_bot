import React, { useCallback, useEffect, useRef, useState } from 'react';

interface OptimizedImageProps {
    src: string;
    alt: string;
    width?: number;
    height?: number;
    className?: string;
    placeholder?: string;
    fallback?: string;
    lazy?: boolean;
    priority?: boolean;
    quality?: number;
    sizes?: string;
    onLoad?: () => void;
    onError?: () => void;
    onClick?: () => void;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = React.memo(({
    src,
    alt,
    width,
    height,
    className = '',
    placeholder,
    fallback = '/placeholder-image.png',
    lazy = true,
    priority = false,
    quality = 80,
    sizes,
    onLoad,
    onError,
    onClick
}) => {
    const [isLoaded, setIsLoaded] = useState(false);
    const [isInView, setIsInView] = useState(priority || !lazy);
    const [hasError, setHasError] = useState(false);
    const [currentSrc, setCurrentSrc] = useState<string>('');

    const imgRef = useRef<HTMLImageElement>(null);
    const observerRef = useRef<IntersectionObserver | null>(null);

    // Оптимизация URL изображения
    const optimizeImageUrl = useCallback((url: string): string => {
        if (!url) return fallback;

        // Если это уже оптимизированный URL (содержит параметры), возвращаем как есть
        if (url.includes('?') || url.includes('&')) {
            return url;
        }

        const params = new URLSearchParams();
        if (width) params.append('w', width.toString());
        if (height) params.append('h', height.toString());
        if (quality) params.append('q', quality.toString());
        if (sizes) params.append('sizes', sizes);

        // Добавляем формат WebP для лучшего сжатия
        params.append('fm', 'webp');

        const queryString = params.toString();
        return queryString ? `${url}?${queryString}` : url;
    }, [width, height, quality, sizes, fallback]);

    // Intersection Observer для ленивой загрузки
    useEffect(() => {
        if (!lazy || priority || isInView) return;

        if (!imgRef.current) return;

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
                rootMargin: '50px', // Загружаем за 50px до появления в viewport
                threshold: 0.1
            }
        );

        observerRef.current.observe(imgRef.current);

        return () => {
            observerRef.current?.disconnect();
        };
    }, [lazy, priority, isInView]);

    // Обновляем src когда изображение должно загружаться
    useEffect(() => {
        if (isInView && !currentSrc) {
            setCurrentSrc(optimizeImageUrl(src));
        }
    }, [isInView, src, optimizeImageUrl, currentSrc]);

    const handleLoad = useCallback(() => {
        setIsLoaded(true);
        setHasError(false);
        onLoad?.();
    }, [onLoad]);

    const handleError = useCallback(() => {
        setHasError(true);
        setIsLoaded(false);
        setCurrentSrc(fallback);
        onError?.();
    }, [fallback, onError]);

    const handleClick = useCallback(() => {
        onClick?.();
    }, [onClick]);

    // Плейсхолдер пока изображение не загружено
    const renderPlaceholder = () => {
        if (placeholder) {
            return (
                <div
                    className={`bg-muted animate-pulse ${className}`}
                    style={{ width, height }}
                >
                    <img
                        src={placeholder}
                        alt=""
                        className="w-full h-full object-cover opacity-50"
                    />
                </div>
            );
        }

        return (
            <div
                className={`bg-muted animate-pulse flex items-center justify-center ${className}`}
                style={{ width, height }}
            >
                <div className="w-8 h-8 bg-muted-foreground/20 rounded" />
            </div>
        );
    };

    return (
        <div className="relative overflow-hidden">
            {!isInView ? (
                renderPlaceholder()
            ) : (
                <img
                    ref={imgRef}
                    src={currentSrc || optimizeImageUrl(src)}
                    alt={alt}
                    width={width}
                    height={height}
                    className={`transition-opacity duration-300 ${isLoaded ? 'opacity-100' : 'opacity-0'
                        } ${className}`}
                    onLoad={handleLoad}
                    onError={handleError}
                    onClick={handleClick}
                    loading={lazy && !priority ? 'lazy' : 'eager'}
                    decoding="async"
                    style={{
                        width: width ? `${width}px` : undefined,
                        height: height ? `${height}px` : undefined,
                    }}
                />
            )}

            {/* Показываем плейсхолдер пока изображение загружается */}
            {isInView && !isLoaded && !hasError && (
                <div className="absolute inset-0">
                    {renderPlaceholder()}
                </div>
            )}

            {/* Индикатор ошибки */}
            {hasError && (
                <div
                    className={`bg-muted flex items-center justify-center ${className}`}
                    style={{ width, height }}
                >
                    <div className="text-center text-muted-foreground">
                        <div className="w-8 h-8 mx-auto mb-2 bg-muted-foreground/20 rounded" />
                        <span className="text-xs">Ошибка загрузки</span>
                    </div>
                </div>
            )}
        </div>
    );
});

OptimizedImage.displayName = 'OptimizedImage';
