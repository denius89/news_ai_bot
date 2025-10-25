// Service Worker Registration
// Регистрация Service Worker для кеширования

export const registerServiceWorker = async () => {
    if ('serviceWorker' in navigator) {
        try {
            const registration = await navigator.serviceWorker.register('/webapp/sw.js', {
                scope: '/webapp/'
            });

            console.log('[SW] Service Worker registered successfully:', registration);

            // Обработка обновлений
            registration.addEventListener('updatefound', () => {
                const newWorker = registration.installing;
                if (newWorker) {
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // Новый Service Worker установлен, можно обновить страницу
                            console.log('[SW] New Service Worker available');
                            // Можно показать уведомление пользователю
                        }
                    });
                }
            });

            return registration;
        } catch (error) {
            console.error('[SW] Service Worker registration failed:', error);
            return null;
        }
    } else {
        console.log('[SW] Service Worker not supported');
        return null;
    }
};

// Проверка статуса Service Worker
export const getServiceWorkerStatus = () => {
    if ('serviceWorker' in navigator) {
        return {
            supported: true,
            controller: navigator.serviceWorker.controller,
            ready: navigator.serviceWorker.ready
        };
    }
    return { supported: false };
};

// Принудительное обновление Service Worker
export const updateServiceWorker = async () => {
    if ('serviceWorker' in navigator) {
        try {
            const registration = await navigator.serviceWorker.getRegistration();
            if (registration) {
                await registration.update();
                console.log('[SW] Service Worker updated');
                return true;
            }
        } catch (error) {
            console.error('[SW] Failed to update Service Worker:', error);
        }
    }
    return false;
};

// Очистка кеша
export const clearServiceWorkerCache = async () => {
    if ('caches' in window) {
        try {
            const cacheNames = await caches.keys();
            await Promise.all(
                cacheNames.map(cacheName => caches.delete(cacheName))
            );
            console.log('[SW] All caches cleared');
            return true;
        } catch (error) {
            console.error('[SW] Failed to clear caches:', error);
        }
    }
    return false;
};

// Получение информации о кеше
export const getCacheInfo = async () => {
    if ('caches' in window) {
        try {
            const cacheNames = await caches.keys();
            const cacheInfo = await Promise.all(
                cacheNames.map(async (cacheName) => {
                    const cache = await caches.open(cacheName);
                    const keys = await cache.keys();
                    return {
                        name: cacheName,
                        size: keys.length,
                        urls: keys.map(request => request.url)
                    };
                })
            );
            return cacheInfo;
        } catch (error) {
            console.error('[SW] Failed to get cache info:', error);
        }
    }
    return [];
};
