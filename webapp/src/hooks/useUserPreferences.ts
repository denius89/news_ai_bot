import { useState, useEffect, useCallback } from 'react';

export interface UserPreferences {
  preferred_category: string;
  preferred_style: string;
  preferred_period: string;
  min_importance: number;
  enable_smart_filtering: boolean;
  enable_gestures: boolean;
  enable_haptic_feedback: boolean;
}

const DEFAULT_PREFERENCES: UserPreferences = {
  preferred_category: 'all',
  preferred_style: 'analytical',
  preferred_period: 'today',
  min_importance: 0.3,
  enable_smart_filtering: true,
  enable_gestures: true,
  enable_haptic_feedback: true,
};

const STORAGE_KEY = 'pulseai_user_preferences';

export const useUserPreferences = (userId?: string) => {
  const [preferences, setPreferences] = useState<UserPreferences>(DEFAULT_PREFERENCES);
  const [isLoading, setIsLoading] = useState(true);

  // Загружаем предпочтения из localStorage при инициализации
  useEffect(() => {
    const loadPreferences = () => {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
          const parsed = JSON.parse(stored);
          setPreferences({ ...DEFAULT_PREFERENCES, ...parsed });
        }
      } catch (error) {
        console.warn('Failed to load preferences from localStorage:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadPreferences();
  }, []);

  // Загружаем предпочтения с сервера, если есть userId
  useEffect(() => {
    if (!userId || isLoading) return;

    const loadServerPreferences = async () => {
      try {
        const response = await fetch(`/api/users/preferences?user_id=${userId}`);
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'success') {
            const serverPrefs = data.data;
            const mergedPrefs = { ...DEFAULT_PREFERENCES, ...serverPrefs };
            setPreferences(mergedPrefs);
            
            // Сохраняем в localStorage для быстрого доступа
            localStorage.setItem(STORAGE_KEY, JSON.stringify(mergedPrefs));
          }
        }
      } catch (error) {
        console.warn('Failed to load preferences from server:', error);
      }
    };

    loadServerPreferences();
  }, [userId, isLoading]);

  // Сохраняем предпочтения в localStorage и на сервер
  const savePreferences = useCallback(async (newPreferences: Partial<UserPreferences>) => {
    const updatedPreferences = { ...preferences, ...newPreferences };
    setPreferences(updatedPreferences);

    // Сохраняем в localStorage
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedPreferences));
    } catch (error) {
      console.warn('Failed to save preferences to localStorage:', error);
    }

    // Сохраняем на сервер, если есть userId
    if (userId) {
      try {
        const response = await fetch('/api/users/preferences', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: userId,
            ...updatedPreferences,
          }),
        });

        if (!response.ok) {
          console.warn('Failed to save preferences to server:', response.statusText);
        }
      } catch (error) {
        console.warn('Failed to save preferences to server:', error);
      }
    }
  }, [preferences, userId]);

  // Сбрасываем предпочтения к значениям по умолчанию
  const resetPreferences = useCallback(async () => {
    await savePreferences(DEFAULT_PREFERENCES);
  }, [savePreferences]);

  // Получаем предпочтения для генерации дайджеста
  const getDigestPreferences = useCallback(() => {
    return {
      category: preferences.preferred_category,
      style: preferences.preferred_style,
      period: preferences.preferred_period,
      min_importance: preferences.min_importance,
      enable_smart_filtering: preferences.enable_smart_filtering,
    };
  }, [preferences]);

  // Обновляем предпочтения после генерации дайджеста
  const updateAfterDigestGeneration = useCallback(async (
    category: string,
    style: string,
    period: string
  ) => {
    await savePreferences({
      preferred_category: category,
      preferred_style: style,
      preferred_period: period,
    });
  }, [savePreferences]);

  return {
    preferences,
    isLoading,
    savePreferences,
    resetPreferences,
    getDigestPreferences,
    updateAfterDigestGeneration,
  };
};
