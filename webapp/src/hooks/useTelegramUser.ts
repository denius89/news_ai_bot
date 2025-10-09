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
  first_name?: string;
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

        console.log('🚀 Initializing Telegram user...');
        console.log('🔍 window.Telegram:', window.Telegram);
        console.log('🔍 window.Telegram?.WebApp:', window.Telegram?.WebApp);
        console.log('🔍 window.location:', window.location);
        console.log('🔍 window.location.origin:', window.location.origin);
        console.log('🔍 navigator.userAgent:', navigator.userAgent);

        // ВРЕМЕННО ОТКЛЮЧАЕМ HTTPS ПРОВЕРКУ ДЛЯ ОТЛАДКИ
        const isHttps = window.location.protocol === 'https:';
        console.log('🔍 Protocol:', window.location.protocol, 'HTTPS:', isHttps);
        console.log('⚠️ HTTPS check disabled for debugging');
        
        // if (!isHttps) {
        //   console.log('❌ Not HTTPS - Telegram WebApp requires HTTPS');
        //   setError('Приложение должно запускаться через HTTPS (используйте Cloudflare URL)');
        //   setIsTelegramWebApp(false);
        //   return;
        // }

        // Проверяем, запущено ли приложение в Telegram WebApp
        const tgWebApp = window.Telegram?.WebApp;
        const tgUser = tgWebApp?.user || tgWebApp?.initDataUnsafe?.user;
        
        console.log('🔍 Telegram WebApp check:');
        console.log('- window.Telegram exists:', !!window.Telegram);
        console.log('- tgWebApp exists:', !!tgWebApp);
        console.log('- tgUser exists:', !!tgUser);
        console.log('- tgUser type:', typeof tgUser);
        
        // Отладочная информация
        console.log('🔍 Debug info:');
        console.log('- window.Telegram:', window.Telegram);
        console.log('- tgWebApp:', tgWebApp);
        console.log('- tgUser:', tgUser);
        console.log('- Current URL:', window.location.href);
        console.log('- User Agent:', navigator.userAgent);
        
        if (tgWebApp && tgUser) {
          console.log('🚀 Telegram WebApp detected:', tgUser);
          setIsTelegramWebApp(true);
            setTelegramUser(tgUser || null);

          // Кэш отключен - всегда получаем свежие данные от Telegram

          // Получаем user_id по telegram_id
          console.log('🔄 Fetching user data for telegram_id:', tgUser.id);
        console.log('🔍 tgUser data:', tgUser);
        console.log('🔍 tgUser.first_name:', tgUser.first_name);
        console.log('🔍 tgUser.username:', tgUser.username);
        console.log('🔍 tgUser.id:', tgUser.id);
        console.log('🔍 tgUser keys:', Object.keys(tgUser));
        console.log('🔍 tgUser full object:', JSON.stringify(tgUser, null, 2));
          
          const response = await fetch(`/api/users/by-telegram-id/${tgUser.id}`, {
            headers: {
              'X-Telegram-User-Data': JSON.stringify(tgUser)
            }
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

            console.log('✅ User data fetched successfully:', userInfo);
            
            setUserData(userInfo);
            setUserId(userInfo.user_id);
            
            // Кэш отключен - не сохраняем данные
            
          } else {
            console.error('❌ Failed to fetch user data:', data.message);
            // Более понятное сообщение об ошибке
            const errorMessage = data.message?.includes('Database') ? 
              'Проблема с подключением к серверу. Попробуйте позже.' :
              data.message || 'Ошибка аутентификации пользователя';
            setError(errorMessage);
          }

        } else {
          console.log('🌐 Not running in Telegram WebApp - using fallback');
          console.log('❌ REASON: window.Telegram?.WebApp is:', window.Telegram?.WebApp);
          console.log('❌ REASON: tgWebApp is:', tgWebApp);
          console.log('❌ REASON: tgUser is:', tgUser);
          setIsTelegramWebApp(false);
          
          // Не используем fallback - показываем ошибку
          setError('Приложение должно запускаться только через Telegram WebApp');
        }

      } catch (err) {
        console.error('❌ Error initializing Telegram user:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
        
        // Не используем fallback при ошибке - показываем ошибку
        console.log('❌ No fallback user - showing error to user');
        
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
        first_name: data.data.first_name,
        telegram_user: window.Telegram?.WebApp?.user || window.Telegram?.WebApp?.initDataUnsafe?.user
      };

      // Кэш отключен - не сохраняем данные

      return userInfo;
    }
    
    return null;
  } catch (error) {
    console.error('Error refreshing user data:', error);
    return null;
  }
};
