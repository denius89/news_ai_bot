// API Configuration
// Конфигурация API для PulseAI

// API Configuration
// Конфигурация API для PulseAI

const getApiBaseUrl = () => {
    // В development используем proxy
    if ((import.meta as any).env?.DEV) {
        return '';
    }

    // В production используем полный URL
    if ((import.meta as any).env?.VITE_API_BASE_URL) {
        return (import.meta as any).env.VITE_API_BASE_URL;
    }

    // Fallback для production
    return window.location.origin.replace('/webapp', '');
};

export const API_BASE_URL = getApiBaseUrl();

export const apiUrl = (path: string) => {
    const baseUrl = API_BASE_URL;
    const cleanPath = path.startsWith('/') ? path : `/${path}`;

    if (baseUrl) {
        return `${baseUrl}${cleanPath}`;
    }

    return cleanPath;
};

// Утилиты для API запросов
export const apiRequest = async (path: string, options: RequestInit = {}) => {
    const url = apiUrl(path);

    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    });

    if (response.status === 401) {
        throw new Error('Authentication required');
    }

    return response;
};

export default {
    API_BASE_URL,
    apiUrl,
    apiRequest
};
