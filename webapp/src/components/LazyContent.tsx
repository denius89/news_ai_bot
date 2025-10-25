import React, { ReactNode, useEffect, useRef, useState } from 'react';

interface LazyContentProps {
    children: ReactNode;
    fallback?: ReactNode;
    rootMargin?: string;
    threshold?: number;
    className?: string;
    onVisible?: () => void;
}

export const LazyContent: React.FC<LazyContentProps> = React.memo(({
    children,
    fallback,
    rootMargin = '50px',
    threshold = 0.1,
    className = '',
    onVisible
}) => {
    const [isVisible, setIsVisible] = useState(false);
    const [hasBeenVisible, setHasBeenVisible] = useState(false);
    const ref = useRef<HTMLDivElement>(null);
    const observerRef = useRef<IntersectionObserver | null>(null);

    useEffect(() => {
        if (!ref.current) return;

        observerRef.current = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting && !hasBeenVisible) {
                        setIsVisible(true);
                        setHasBeenVisible(true);
                        onVisible?.();
                        observerRef.current?.disconnect();
                    }
                });
            },
            {
                rootMargin,
                threshold
            }
        );

        observerRef.current.observe(ref.current);

        return () => {
            observerRef.current?.disconnect();
        };
    }, [rootMargin, threshold, hasBeenVisible, onVisible]);

    return (
        <div ref={ref} className={className}>
            {isVisible ? (
                <div className="transition-opacity duration-300">
                    {children}
                </div>
            ) : (
                fallback || (
                    <div className="animate-pulse">
                        <div className="h-4 bg-muted rounded w-3/4 mb-2" />
                        <div className="h-4 bg-muted rounded w-1/2" />
                    </div>
                )
            )}
        </div>
    );
});

LazyContent.displayName = 'LazyContent';

// Компонент для ленивой загрузки списков
interface LazyListProps<T> {
    items: T[];
    renderItem: (item: T, index: number) => ReactNode;
    itemHeight?: number;
    containerHeight?: number;
    overscan?: number;
    className?: string;
}

export const LazyList = <T,>({
    items,
    renderItem,
    itemHeight = 200,
    containerHeight = 400,
    overscan = 5,
    className = ''
}: LazyListProps<T>) => {
    const [visibleRange, setVisibleRange] = useState({ start: 0, end: overscan });
    const containerRef = useRef<HTMLDivElement>(null);

    const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
        const scrollTop = e.currentTarget.scrollTop;

        const start = Math.floor(scrollTop / itemHeight);
        const end = Math.min(start + Math.ceil(containerHeight / itemHeight) + overscan, items.length);

        setVisibleRange({ start, end });
    };

    const visibleItems = items.slice(visibleRange.start, visibleRange.end);
    const totalHeight = items.length * itemHeight;
    const offsetY = visibleRange.start * itemHeight;

    return (
        <div
            ref={containerRef}
            className={`overflow-auto ${className}`}
            style={{ height: containerHeight }}
            onScroll={handleScroll}
        >
            <div style={{ height: totalHeight, position: 'relative' }}>
                <div style={{ transform: `translateY(${offsetY}px)` }}>
                    {visibleItems.map((item, index) => (
                        <div
                            key={visibleRange.start + index}
                            style={{ height: itemHeight }}
                        >
                            {renderItem(item, visibleRange.start + index)}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

// Компонент для ленивой загрузки изображений в галерее
interface LazyImageGalleryProps {
    images: string[];
    thumbnailSize?: number;
    className?: string;
    onImageClick?: (src: string, index: number) => void;
}

export const LazyImageGallery: React.FC<LazyImageGalleryProps> = React.memo(({
    images,
    thumbnailSize = 150,
    className = '',
    onImageClick
}) => {
    const handleImageLoad = () => {
        // Image loaded callback
    };

    return (
        <div className={`grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 ${className}`}>
            {images.map((src, index) => (
                <LazyContent
                    key={index}
                    fallback={
                        <div
                            className="bg-muted animate-pulse rounded-lg"
                            style={{ width: thumbnailSize, height: thumbnailSize }}
                        />
                    }
                >
                    <img
                        src={src}
                        alt={`Gallery image ${index + 1}`}
                        className="w-full h-full object-cover rounded-lg cursor-pointer hover:opacity-80 transition-opacity"
                        style={{ width: thumbnailSize, height: thumbnailSize }}
                        onClick={() => onImageClick?.(src, index)}
                        onLoad={() => handleImageLoad()}
                    />
                </LazyContent>
            ))}
        </div>
    );
});

LazyImageGallery.displayName = 'LazyImageGallery';
