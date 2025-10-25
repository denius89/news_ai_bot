import { useEffect, useMemo } from 'react';

interface PreloadResource {
    href: string;
    as: 'image' | 'style' | 'script' | 'font' | 'fetch';
    type?: string;
    crossorigin?: 'anonymous' | 'use-credentials';
}

/**
 * Хук для предзагрузки критических ресурсов
 */
export const usePreloadResources = (resources: PreloadResource[]) => {
    useEffect(() => {
        resources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource.href;
            link.as = resource.as;

            if (resource.type) {
                link.type = resource.type;
            }

            if (resource.crossorigin) {
                link.crossOrigin = resource.crossorigin;
            }

            document.head.appendChild(link);
        });

        return () => {
            resources.forEach(resource => {
                const existingLink = document.querySelector(`link[href="${resource.href}"]`);
                if (existingLink) {
                    existingLink.remove();
                }
            });
        };
    }, [resources]);
};

/**
 * Хук для предзагрузки изображений
 */
export const usePreloadImages = (imageUrls: string[]) => {
    useEffect(() => {
        imageUrls.forEach(url => {
            if (url && url.startsWith('http')) {
                const img = new Image();
                img.src = url;
            }
        });
    }, [imageUrls]);
};

/**
 * Хук для предзагрузки шрифтов
 */
export const usePreloadFonts = (fontUrls: string[]) => {
    const resources = useMemo(() =>
        fontUrls.map(url => ({
            href: url,
            as: 'font' as const,
            type: 'font/woff2',
            crossorigin: 'anonymous' as const
        })), [fontUrls]
    );

    usePreloadResources(resources);
};

/**
 * Хук для предзагрузки критических изображений приложения
 */
export const useCriticalImagePreload = () => {
    const criticalImages = useMemo(() => [
        // Добавьте здесь URL критических изображений
        // Например, логотип, фоновые изображения и т.д.
    ], []);

    usePreloadImages(criticalImages);
};
