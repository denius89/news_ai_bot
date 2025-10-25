import React, { createContext, ReactNode, useContext, useEffect, useState } from 'react';

export interface TelegramUser {
    id: number;
    first_name: string;
    last_name?: string;
    username?: string;
    language_code?: string;
    is_premium?: boolean;
    photo_url?: string;
}

export interface UserData {
    user_id: string;
    telegram_id: number;
    username?: string;
    locale: string;
    first_name?: string;
    telegram_user?: TelegramUser;
}

interface AuthContextType {
    user: UserData | null;
    loading: boolean;
    error: string | null;
    isAuthenticated: boolean;
    authHeaders: Record<string, string>;
    login: () => Promise<void>;
    logout: () => void;
    refreshAuth: () => Promise<void>;
    setAuthHeaders: (headers: Record<string, string>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [user, setUser] = useState<UserData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [authHeaders, setAuthHeaders] = useState<Record<string, string>>({});

    const isAuthenticated = Boolean(user);

    // Retry логика для получения initData (оптимизировано для скорости)
    const getInitDataWithRetry = async (maxAttempts = 2): Promise<string> => {
        for (let i = 0; i < maxAttempts; i++) {
            const initData = window.Telegram?.WebApp?.initData;
            if (initData) return initData;

            if (i < maxAttempts - 1) {
                await new Promise(resolve => setTimeout(resolve, 100)); // Уменьшено с 500ms до 100ms
            }
        }
        throw new Error('Failed to get initData after retries');
    };

    // Безопасная сериализация Telegram пользователя с Base64 кодированием
    const serializeTelegramUser = (tgUser: TelegramUser): string => {
        try {
            // НЕ нормализуем Unicode - сохраняем оригинальные данные
            // Но кодируем в Base64 для безопасной передачи через HTTP headers
            const userJson = JSON.stringify(tgUser);

            // Кодируем UTF-8 строку в Base64 для совместимости с HTTP headers (ISO-8859-1)
            // btoa() требует Latin-1, поэтому сначала encodeURIComponent → unescape
            const base64 = btoa(unescape(encodeURIComponent(userJson)));

            return base64;
        } catch (e) {
            console.error('Error encoding tgUser to Base64:', e);
            // Fallback: минимальные данные в Base64
            const fallbackJson = JSON.stringify({
                id: tgUser.id,
                first_name: tgUser.first_name || '',
                username: tgUser.username || ''
            });
            return btoa(unescape(encodeURIComponent(fallbackJson)));
        }
    };

    const login = async () => {
        try {
            setLoading(true);
            setError(null);

            // Проверяем Telegram WebApp
            const tgWebApp = window.Telegram?.WebApp;
            const tgUser = tgWebApp?.user || tgWebApp?.initDataUnsafe?.user;

            // Исключение для админ панели в DEV режиме
            const isAdminPanel = window.location.pathname.startsWith('/admin');
            const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            const isCloudflareTunnel = window.location.hostname.includes('trycloudflare.com');

            if (!tgWebApp || !tgUser) {
                if (isAdminPanel && (isLocalhost || isCloudflareTunnel)) {
                    console.log('🔓 DEV mode: bypassing Telegram auth for admin panel');
                    // Создаём fake user для админ панели в DEV режиме
                    const fakeUser: TelegramUser = {
                        id: 999999999,
                        first_name: 'Dev Admin',
                        username: 'dev_admin',
                        language_code: 'en'
                    };

                    // Создаём fake auth headers
                    const headers = {
                        'X-Telegram-Init-Data': '',
                        'X-Telegram-User-Data': serializeTelegramUser(fakeUser)
                    };
                    setAuthHeaders(headers);

                    // Создаём fake user data
                    const fakeUserData: UserData = {
                        user_id: 'dev-admin-999999999',
                        telegram_id: 999999999,
                        username: 'dev_admin',
                        locale: 'en',
                        first_name: 'Dev Admin',
                        telegram_user: fakeUser
                    };

                    setUser(fakeUserData);
                    setLoading(false);
                    return;
                }

                throw new Error('Приложение должно запускаться только через Telegram WebApp');
            }


            // Получаем initData с retry логикой
            let initData = '';
            try {
                initData = await getInitDataWithRetry();
            } catch (e) {
                console.warn('Failed to get initData, using fallback authentication');
            }

            // Обновляем заголовки аутентификации
            const headers = {
                'X-Telegram-Init-Data': initData,
                'X-Telegram-User-Data': serializeTelegramUser(tgUser)
            };
            console.log('🔐 Auth headers:', {
                hasInitData: !!initData,
                initDataLength: initData?.length || 0,
                hasUserData: !!headers['X-Telegram-User-Data']
            });
            setAuthHeaders(headers);

            // Получаем данные пользователя из API
            const response = await fetch(`/api/users/by-telegram-id/${tgUser.id}`, {
                headers
            });

            const data = await response.json();

            if (data.status === 'success') {
                const userInfo: UserData = {
                    user_id: data.data.user_id,
                    telegram_id: data.data.telegram_id,
                    username: data.data.username,
                    locale: data.data.locale,
                    first_name: data.data.first_name,
                    telegram_user: tgUser
                };

                setUser(userInfo);

                // Сохраняем в localStorage для быстрого восстановления
                localStorage.setItem('pulseai_auth', JSON.stringify({
                    user: userInfo,
                    telegramUser: tgUser,
                    headers
                }));
            } else {
                throw new Error(data.message || 'Ошибка аутентификации пользователя');
            }

        } catch (err) {
            console.error('Login error:', err);
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    const logout = () => {
        setUser(null);
        setAuthHeaders({});
        setError(null);
        localStorage.removeItem('pulseai_auth');
    };

    const refreshAuth = async () => {
        // Очищаем текущие данные и повторяем аутентификацию
        setUser(null);
        setAuthHeaders({});
        await login();
    };

    // Инициализация при загрузке
    useEffect(() => {
        const initializeAuth = async () => {
            try {
                // Пытаемся восстановить из localStorage
                const cachedAuth = localStorage.getItem('pulseai_auth');
                if (cachedAuth) {
                    const { user: cachedUser, telegramUser: cachedTgUser, headers: cachedHeaders } = JSON.parse(cachedAuth);

                    // Проверяем, что Telegram WebApp все еще доступен
                    const currentTgUser = window.Telegram?.WebApp?.user || window.Telegram?.WebApp?.initDataUnsafe?.user;

                    if (currentTgUser && currentTgUser.id === cachedTgUser.id) {
                        setUser(cachedUser);
                        setAuthHeaders(cachedHeaders);
                        setLoading(false);
                        return;
                    }
                }

                // Если нет кэша или данные устарели, выполняем полную аутентификацию
                await login();
            } catch (err) {
                console.error('Auth initialization error:', err);
                setError(err instanceof Error ? err.message : 'Unknown error');
                setLoading(false);
            }
        };

        initializeAuth();
    }, []);

    const value: AuthContextType = {
        user,
        loading,
        error,
        isAuthenticated,
        authHeaders,
        login,
        logout,
        refreshAuth,
        setAuthHeaders
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
            {/* Debug info */}
            {process.env.NODE_ENV === 'development' && (
                <div
                    data-testid="auth-debug"
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        background: 'black',
                        color: 'white',
                        padding: '10px',
                        fontSize: '12px',
                        zIndex: 9999,
                        maxWidth: '300px'
                    }}
                >
                    <div>Auth Headers: {JSON.stringify(authHeaders)}</div>
                    <div>Is Authenticated: {isAuthenticated ? 'Yes' : 'No'}</div>
                    <div>User ID: {user?.user_id || 'None'}</div>
                    <div>Loading: {loading ? 'Yes' : 'No'}</div>
                    <div>Error: {error || 'None'}</div>
                </div>
            )}
        </AuthContext.Provider>
    );
};
