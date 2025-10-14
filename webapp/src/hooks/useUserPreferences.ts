import { useState, useEffect, useCallback } from 'react';

export interface CategoryPreference {
  [categoryId: string]: string[] | null; // null = all subcategories, [] = disabled, [sub1, sub2] = specific
}

export interface CategoryStructure {
  [categoryId: string]: {
    name: string;
    emoji?: string;
    subcategories: {
      [subcategoryId: string]: {
        name: string;
        icon?: string;
        sources?: Array<{ name: string; url: string }>;
      };
    };
  };
}

interface UseUserPreferencesReturn {
  preferences: CategoryPreference;
  categoriesStructure: CategoryStructure;
  loading: boolean;
  error: string | null;
  updatePreferences: (preferences: CategoryPreference) => Promise<boolean>;
  refreshPreferences: () => Promise<void>;
}

/**
 * Hook для управления предпочтениями категорий пользователя
 * 
 * Функциональность:
 * - Быстрая загрузка предпочтений и категорий
 * - Мгновенное обновление UI
 * - Debounced сохранение изменений (300ms)
 * - Работает только в Telegram WebApp (userId всегда доступен)
 */
export const useUserPreferences = (
  userId: string,
  authHeaders: Record<string, string>
): UseUserPreferencesReturn => {
  const [preferences, setPreferences] = useState<CategoryPreference>({});
  const [categoriesStructure, setCategoriesStructure] = useState<CategoryStructure>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Debounce timer для сохранения
  const [saveTimer, setSaveTimer] = useState<NodeJS.Timeout | null>(null);

  // Загрузка предпочтений и категорий
  const loadPreferences = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Параллельная загрузка для максимальной скорости
      const [categoriesRes, preferencesRes] = await Promise.all([
        fetch('/api/categories'),
        fetch('/api/user/category-preferences', {
          headers: authHeaders
        })
      ]);

      if (!categoriesRes.ok || !preferencesRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const categoriesData = await categoriesRes.json();
      const preferencesData = await preferencesRes.json();

      const newPreferences = preferencesData.data?.preferences || {};
      const newCategoriesStructure = categoriesData.data || {};

      // Обновляем состояние
      setPreferences(newPreferences);
      setCategoriesStructure(newCategoriesStructure);

      console.log('✅ Preferences loaded successfully');

    } catch (err) {
      console.error('❌ Error loading preferences:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      
      // Устанавливаем пустые значения при ошибке
      setPreferences({});
      setCategoriesStructure({});
    } finally {
      setLoading(false);
    }
  }, [userId, authHeaders]);

  // Обновление предпочтений с debounce
  const updatePreferences = useCallback(async (newPreferences: CategoryPreference): Promise<boolean> => {
    try {
      // Мгновенное обновление UI
      setPreferences(newPreferences);

      // Очищаем предыдущий таймер
      if (saveTimer) {
        clearTimeout(saveTimer);
      }

      // Устанавливаем новый таймер с минимальной задержкой
      const timer = setTimeout(async () => {
        try {
          console.log('💾 Saving preferences to server...');
          
          const response = await fetch('/api/user/category-preferences', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...authHeaders
            },
            body: JSON.stringify({
              preferences: newPreferences
            })
          });

          if (!response.ok) {
            throw new Error('Failed to save preferences');
          }

          console.log('✅ Preferences saved successfully');
          return true;
        } catch (err) {
          console.error('❌ Error saving preferences:', err);
          setError(err instanceof Error ? err.message : 'Failed to save preferences');
          return false;
        }
      }, 300); // 300ms debounce

      setSaveTimer(timer);
      return true;

    } catch (err) {
      console.error('❌ Error updating preferences:', err);
      setError(err instanceof Error ? err.message : 'Failed to update preferences');
      return false;
    }
  }, [authHeaders, saveTimer]);

  // Принудительное обновление
  const refreshPreferences = useCallback(async () => {
    await loadPreferences();
  }, [loadPreferences]);

  // Автоматическая загрузка при изменении userId
  useEffect(() => {
    if (userId) {
      loadPreferences();
    }
  }, [userId, loadPreferences]);

  // Очистка таймера при размонтировании
  useEffect(() => {
    return () => {
      if (saveTimer) {
        clearTimeout(saveTimer);
      }
    };
  }, [saveTimer]);

  return {
    preferences,
    categoriesStructure,
    loading,
    error,
    updatePreferences,
    refreshPreferences
  };
};
