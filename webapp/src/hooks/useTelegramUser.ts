import { useState, useEffect } from 'react';

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
  telegram_user?: TelegramUser;
}

export interface UseTelegramUserReturn {
  userId: string | null;
  telegramUser: TelegramUser | null;
  userData: UserData | null;
  loading: boolean;
  error: string | null;
  isTelegramWebApp: boolean;
  isAuthenticated: boolean;
}

/**
 * Hook для автоматического получения user_id из Telegram WebApp
 * 
 * Функциональность:
 * - Автоматически определяет Telegram WebApp
 * - Получает telegram_id из window.Telegram.WebApp.user.id
 * - Находит user_id в базе данных по telegram_id
 * - Предоставляет fallback для разработки
 * - Кэширует результат в localStorage
 * 
 * @returns Объект с данными пользователя и состоянием загрузки
 */
export const useTelegramUser = (): UseTelegramUserReturn => {
  const [userId, setUserId] = useState<string | null>(null);
  const [telegramUser, setTelegramUser] = useState<TelegramUser | null>(null);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isTelegramWebApp, setIsTelegramWebApp] = useState(false);

  useEffect(() => {
    const initializeUser = async () => {
      try {
        setLoading(true);
        setError(null);

        // Проверяем, запущено ли приложение в Telegram WebApp
        const tgWebApp = window.Telegram?.WebApp;
        const tgUser = tgWebApp?.user || tgWebApp?.initDataUnsafe?.user;
        
        if (tgWebApp && tgUser) {
          console.log('🚀 Telegram WebApp detected:', tgUser);
          setIsTelegramWebApp(true);
            setTelegramUser(tgUser || null);

          // Проверяем кэш в localStorage
          const cacheKey = `telegram_user_${tgUser.id}`;
          const cachedData = localStorage.getItem(cacheKey);
          
          if (cachedData) {
            try {
              const parsedCache = JSON.parse(cachedData);
              // Проверяем, что кэш не старше 1 часа
              if (Date.now() - parsedCache.timestamp < 3600000) {
                console.log('✅ Using cached user data:', parsedCache.data);
                setUserData(parsedCache.data);
                setUserId(parsedCache.data.user_id);
                setLoading(false);
                return;
              }
            } catch (e) {
              console.warn('⚠️ Invalid cache data, fetching fresh data');
            }
          }

          // Получаем user_id по telegram_id
          console.log('🔄 Fetching user data for telegram_id:', tgUser.id);
          
          const response = await fetch(`/api/users/by-telegram-id/${tgUser.id}`);
          const data = await response.json();

          if (data.status === 'success') {
            const userInfo: UserData = {
              user_id: data.data.user_id,
              telegram_id: data.data.telegram_id,
              username: data.data.username,
              locale: data.data.locale,
              telegram_user: tgUser
            };

            console.log('✅ User data fetched successfully:', userInfo);
            
            setUserData(userInfo);
            setUserId(userInfo.user_id);
            
            // Кэшируем данные
            localStorage.setItem(cacheKey, JSON.stringify({
              data: userInfo,
              timestamp: Date.now()
            }));
            
          } else {
            console.error('❌ Failed to fetch user data:', data.message);
            setError(data.message || 'Failed to authenticate user');
          }

        } else {
          console.log('🌐 Not running in Telegram WebApp - using fallback');
          setIsTelegramWebApp(false);
          
          // Fallback для разработки - используем тестового пользователя
          const fallbackUser: UserData = {
            user_id: 'f7d38911-4e62-4012-a9bf-2aaa03483497', // Тестовый пользователь
            telegram_id: 123,
            username: 'demo_user',
            locale: 'ru',
            telegram_user: {
              id: 123,
              first_name: 'Demo',
              username: 'demo_user',
              language_code: 'ru'
            }
          };

          console.log('🔄 Using fallback user data:', fallbackUser);
          setUserData(fallbackUser);
          setUserId(fallbackUser.user_id);
          setTelegramUser(fallbackUser.telegram_user || null);
        }

      } catch (err) {
        console.error('❌ Error initializing Telegram user:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        
        // Fallback при ошибке
        const fallbackUser: UserData = {
          user_id: 'f7d38911-4e62-4012-a9bf-2aaa03483497',
          telegram_id: 123,
          username: 'demo_user',
          locale: 'ru',
          telegram_user: {
            id: 123,
            first_name: 'Demo',
            username: 'demo_user',
            language_code: 'ru'
          }
        };
        
        setUserData(fallbackUser);
        setUserId(fallbackUser.user_id);
        setTelegramUser(fallbackUser.telegram_user || null);
        
      } finally {
        setLoading(false);
      }
    };

    initializeUser();
  }, []);

  const isAuthenticated = Boolean(userId && userData);

  return {
    userId,
    telegramUser,
    userData,
    loading,
    error,
    isTelegramWebApp,
    isAuthenticated
  };
};

/**
 * Утилита для очистки кэша пользователя
 */
export const clearTelegramUserCache = (telegramId?: number) => {
  if (telegramId) {
    localStorage.removeItem(`telegram_user_${telegramId}`);
  } else {
    // Очищаем весь кэш пользователей
    Object.keys(localStorage).forEach(key => {
      if (key.startsWith('telegram_user_')) {
        localStorage.removeItem(key);
      }
    });
  }
};

/**
 * Утилита для принудительного обновления данных пользователя
 */
export const refreshTelegramUser = async (telegramId: number): Promise<UserData | null> => {
  try {
    const response = await fetch(`/api/users/by-telegram-id/${telegramId}`);
    const data = await response.json();

    if (data.status === 'success') {
      const userInfo: UserData = {
        user_id: data.data.user_id,
        telegram_id: data.data.telegram_id,
        username: data.data.username,
        locale: data.data.locale,
        telegram_user: window.Telegram?.WebApp?.user || window.Telegram?.WebApp?.initDataUnsafe?.user
      };

      // Обновляем кэш
      const cacheKey = `telegram_user_${telegramId}`;
      localStorage.setItem(cacheKey, JSON.stringify({
        data: userInfo,
        timestamp: Date.now()
      }));

      return userInfo;
    }
    
    return null;
  } catch (error) {
    console.error('Error refreshing user data:', error);
    return null;
  }
};
