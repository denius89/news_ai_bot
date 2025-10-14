import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

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

  // Безопасная сериализация Telegram пользователя
  // Функция для нормализации Unicode символов
  const normalizeUnicodeText = (text: string): string => {
    if (!text) return text;
    
    // Нормализуем Unicode символы (NFD -> NFC)
    return text
      .normalize('NFD')  // Разбиваем составные символы
      .replace(/[\u0300-\u036f]/g, '')  // Убираем диакритические знаки
      .replace(/[^\x00-\x7F]/g, (char) => {
        // Заменяем не-ASCII символы на ASCII аналоги
        const replacements: Record<string, string> = {
          '𝕀': 'I', '𝕧': 'v', '𝕒': 'a', '𝕟': 'n',
          '𝔸': 'A', '𝔹': 'B', 'ℂ': 'C', '𝔻': 'D',
          '𝔼': 'E', '𝔽': 'F', '𝔾': 'G', 'ℍ': 'H',
          '𝕁': 'J', '𝕂': 'K', '𝕃': 'L',
          '𝕄': 'M', 'ℕ': 'N', '𝕆': 'O', 'ℙ': 'P',
          'ℚ': 'Q', 'ℝ': 'R', '𝕊': 'S', '𝕋': 'T',
          '𝕌': 'U', '𝕍': 'V', '𝕎': 'W', '𝕏': 'X',
          '𝕐': 'Y', 'ℤ': 'Z'
        };
        return replacements[char] || char;
      });
  };

  const serializeTelegramUser = (tgUser: TelegramUser): string => {
    try {
      // Создаем нормализованную копию пользователя
      const normalizedUser = {
        ...tgUser,
        first_name: normalizeUnicodeText(tgUser.first_name || ''),
        last_name: normalizeUnicodeText(tgUser.last_name || ''),
        username: normalizeUnicodeText(tgUser.username || '')
      };
      
      return JSON.stringify(normalizedUser);
    } catch (e) {
      console.error('Error stringifying tgUser:', e);
      return JSON.stringify({
        id: tgUser.id,
        first_name: normalizeUnicodeText(tgUser.first_name || ''),
        username: normalizeUnicodeText(tgUser.username || '')
      });
    }
  };

  const login = async () => {
    try {
      setLoading(true);
      setError(null);

      // Проверяем Telegram WebApp
      const tgWebApp = window.Telegram?.WebApp;
      const tgUser = tgWebApp?.user || tgWebApp?.initDataUnsafe?.user;
      
      if (!tgWebApp || !tgUser) {
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
    refreshAuth
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
