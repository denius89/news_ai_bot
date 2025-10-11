import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Bell, BellOff, Check, X } from 'lucide-react';

interface NotificationPreferences {
  categories: string[];
  min_importance: number;
  delivery_method: string;
  notification_frequency: string;
  max_notifications_per_day: number;
}

const CATEGORIES = [
  { id: 'crypto', name: 'Криптовалюты', emoji: '🪙' },
  { id: 'markets', name: 'Финансовые рынки', emoji: '📈' },
  { id: 'sports', name: 'Спорт', emoji: '🏀' },
  { id: 'tech', name: 'Технологии', emoji: '💻' },
  { id: 'world', name: 'Мировые события', emoji: '🌍' },
];

const FREQUENCIES = [
  { id: 'realtime', name: 'В реальном времени' },
  { id: 'hourly', name: 'Каждый час' },
  { id: 'daily', name: 'Ежедневно' },
  { id: 'weekly', name: 'Еженедельно' },
];

const DELIVERY_METHODS = [
  { id: 'bot', name: 'Telegram бот' },
  { id: 'webapp', name: 'WebApp' },
  { id: 'all', name: 'Все каналы' },
];

export const NotificationSettings: React.FC = () => {
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    categories: [],
    min_importance: 0.6,
    delivery_method: 'bot',
    notification_frequency: 'daily',
    max_notifications_per_day: 3,
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    try {
      setLoading(true);
      
      const response = await fetch('/api/user/preferences', {
        headers: {
          'X-Telegram-User-Id': window.Telegram?.WebApp?.initDataUnsafe?.user?.id?.toString() || '',
        },
      });
      
      const data = await response.json();
      
      if (data.success && data.data) {
        setPreferences(data.data);
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
      showMessage('error', 'Ошибка загрузки настроек');
    } finally {
      setLoading(false);
    }
  };

  const savePreferences = async () => {
    try {
      setSaving(true);
      
      const response = await fetch('/api/user/preferences', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Telegram-User-Id': window.Telegram?.WebApp?.initDataUnsafe?.user?.id?.toString() || '',
        },
        body: JSON.stringify(preferences),
      });
      
      const data = await response.json();
      
      if (data.success) {
        showMessage('success', 'Настройки сохранены');
      } else {
        showMessage('error', 'Ошибка сохранения настроек');
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      showMessage('error', 'Ошибка сохранения настроек');
    } finally {
      setSaving(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  const toggleCategory = (categoryId: string) => {
    setPreferences(prev => ({
      ...prev,
      categories: prev.categories.includes(categoryId)
        ? prev.categories.filter(c => c !== categoryId)
        : [...prev.categories, categoryId],
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  return (
    <main className="pb-32 pt-4 px-4 max-w-md mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <Bell className="w-6 h-6 text-emerald-500" />
          Уведомления
        </h1>
        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Настройте уведомления о важных событиях
        </p>
      </div>

      {/* Message */}
      {message && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          className={`mb-4 p-3 rounded-xl flex items-center gap-2 ${
            message.type === 'success'
              ? 'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-300'
              : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300'
          }`}
        >
          {message.type === 'success' ? (
            <Check className="w-5 h-5" />
          ) : (
            <X className="w-5 h-5" />
          )}
          <span className="text-sm font-medium">{message.text}</span>
        </motion.div>
      )}

      {/* Categories */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Категории событий
        </h2>
        <div className="space-y-2">
          {CATEGORIES.map(category => (
            <motion.button
              key={category.id}
              whileTap={{ scale: 0.98 }}
              onClick={() => toggleCategory(category.id)}
              className={`w-full p-3 rounded-xl flex items-center justify-between transition-all ${
                preferences.categories.includes(category.id)
                  ? 'bg-emerald-50 dark:bg-emerald-900/20 border-2 border-emerald-500'
                  : 'bg-gray-50 dark:bg-gray-800 border-2 border-transparent'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl">{category.emoji}</span>
                <span className="font-medium text-gray-900 dark:text-white">
                  {category.name}
                </span>
              </div>
              {preferences.categories.includes(category.id) && (
                <Check className="w-5 h-5 text-emerald-500" />
              )}
            </motion.button>
          ))}
        </div>
        {preferences.categories.length === 0 && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Выберите хотя бы одну категорию для получения уведомлений
          </p>
        )}
      </div>

      {/* Importance */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Минимальная важность
        </h2>
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-xl">
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={preferences.min_importance}
            onChange={(e) =>
              setPreferences(prev => ({ ...prev, min_importance: parseFloat(e.target.value) }))
            }
            className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
          />
          <div className="flex justify-between mt-2 text-sm text-gray-600 dark:text-gray-400">
            <span>Все события</span>
            <span className="font-semibold text-emerald-600 dark:text-emerald-400">
              {Math.round(preferences.min_importance * 100)}%
            </span>
            <span>Только важные</span>
          </div>
        </div>
      </div>

      {/* Frequency */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Частота уведомлений
        </h2>
        <div className="space-y-2">
          {FREQUENCIES.map(freq => (
            <motion.button
              key={freq.id}
              whileTap={{ scale: 0.98 }}
              onClick={() =>
                setPreferences(prev => ({ ...prev, notification_frequency: freq.id }))
              }
              className={`w-full p-3 rounded-xl flex items-center justify-between transition-all ${
                preferences.notification_frequency === freq.id
                  ? 'bg-emerald-50 dark:bg-emerald-900/20 border-2 border-emerald-500'
                  : 'bg-gray-50 dark:bg-gray-800 border-2 border-transparent'
              }`}
            >
              <span className="font-medium text-gray-900 dark:text-white">{freq.name}</span>
              {preferences.notification_frequency === freq.id && (
                <Check className="w-5 h-5 text-emerald-500" />
              )}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Delivery Method */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Способ доставки
        </h2>
        <div className="space-y-2">
          {DELIVERY_METHODS.map(method => (
            <motion.button
              key={method.id}
              whileTap={{ scale: 0.98 }}
              onClick={() =>
                setPreferences(prev => ({ ...prev, delivery_method: method.id }))
              }
              className={`w-full p-3 rounded-xl flex items-center justify-between transition-all ${
                preferences.delivery_method === method.id
                  ? 'bg-emerald-50 dark:bg-emerald-900/20 border-2 border-emerald-500'
                  : 'bg-gray-50 dark:bg-gray-800 border-2 border-transparent'
              }`}
            >
              <span className="font-medium text-gray-900 dark:text-white">{method.name}</span>
              {preferences.delivery_method === method.id && (
                <Check className="w-5 h-5 text-emerald-500" />
              )}
            </motion.button>
          ))}
        </div>
      </div>

      {/* Max per day */}
      <div className="mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Максимум уведомлений в день
        </h2>
        <div className="bg-gray-50 dark:bg-gray-800 p-4 rounded-xl">
          <input
            type="range"
            min="1"
            max="10"
            step="1"
            value={preferences.max_notifications_per_day}
            onChange={(e) =>
              setPreferences(prev => ({
                ...prev,
                max_notifications_per_day: parseInt(e.target.value),
              }))
            }
            className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
          />
          <div className="flex justify-center mt-2">
            <span className="text-2xl font-bold text-emerald-600 dark:text-emerald-400">
              {preferences.max_notifications_per_day}
            </span>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <motion.button
        whileTap={{ scale: 0.98 }}
        onClick={savePreferences}
        disabled={saving || preferences.categories.length === 0}
        className={`w-full py-4 rounded-xl font-semibold text-white transition-all ${
          saving || preferences.categories.length === 0
            ? 'bg-gray-300 dark:bg-gray-700 cursor-not-allowed'
            : 'bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 shadow-lg'
        }`}
      >
        {saving ? 'Сохранение...' : 'Сохранить настройки'}
      </motion.button>
    </main>
  );
};

