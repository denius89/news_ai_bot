import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  TrendingUp, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Filter, 
  Brain, 
  RefreshCw,
  Activity
} from 'lucide-react';

interface AnalyticsData {
  total_generations: number;
  successful_generations: number;
  success_rate: number;
  avg_generation_time_ms: number;
  category_stats: Record<string, number>;
  style_stats: Record<string, number>;
  period_days: number;
  user_id?: string;
}

interface AnalyticsPageProps {
  userId?: string;
}

export const AnalyticsPage: React.FC<AnalyticsPageProps> = ({ userId }) => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);

  const loadAnalytics = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const url = userId 
        ? `/api/analytics/digest-stats?user_id=${userId}&days=${days}`
        : `/api/analytics/digest-stats?days=${days}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.status === 'success') {
        setAnalytics(data.data);
      } else {
        setError(data.message || 'Ошибка загрузки аналитики');
      }
    } catch (err) {
      setError('Не удалось загрузить аналитику');
      console.error('Analytics loading error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAnalytics();
  }, [userId, days]);

  const formatTime = (ms: number) => {
    if (ms < 1000) return `${Math.round(ms)}мс`;
    return `${(ms / 1000).toFixed(1)}с`;
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'all': return <Filter className="w-4 h-4" />;
      case 'crypto': return <TrendingUp className="w-4 h-4" />;
      case 'sports': return <Activity className="w-4 h-4" />;
      case 'markets': return <BarChart3 className="w-4 h-4" />;
      case 'tech': return <Brain className="w-4 h-4" />;
      case 'world': return <Filter className="w-4 h-4" />;
      default: return <Filter className="w-4 h-4" />;
    }
  };

  const getStyleIcon = (style: string) => {
    switch (style) {
      case 'analytical': return <Brain className="w-4 h-4" />;
      case 'business': return <TrendingUp className="w-4 h-4" />;
      case 'meme': return <Activity className="w-4 h-4" />;
      default: return <Brain className="w-4 h-4" />;
    }
  };

  const getCategoryName = (category: string) => {
    const names: Record<string, string> = {
      all: 'Все категории',
      crypto: 'Криптовалюты',
      sports: 'Спорт',
      markets: 'Рынки',
      tech: 'Технологии',
      world: 'Мир'
    };
    return names[category] || category;
  };

  const getStyleName = (style: string) => {
    const names: Record<string, string> = {
      analytical: 'Аналитический',
      business: 'Бизнес',
      meme: 'Мемный'
    };
    return names[style] || style;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center"
        >
          <RefreshCw className="w-8 h-8 animate-spin text-emerald-500 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Загружаем аналитику...</p>
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center max-w-md mx-auto p-6"
        >
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Ошибка загрузки
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
          <button
            onClick={loadAnalytics}
            className="px-4 py-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
          >
            Попробовать снова
          </button>
        </motion.div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center"
        >
          <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600 dark:text-gray-400">Нет данных для отображения</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto p-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-emerald-500" />
              Аналитика дайджестов
            </h1>
            
            <div className="flex items-center gap-2">
              <select
                value={days}
                onChange={(e) => setDays(Number(e.target.value))}
                className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-sm"
              >
                <option value={7}>7 дней</option>
                <option value={30}>30 дней</option>
                <option value={90}>90 дней</option>
              </select>
              
              <button
                onClick={loadAnalytics}
                className="p-2 bg-emerald-500 text-white rounded-lg hover:bg-emerald-600 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
              </button>
            </div>
          </div>
          
          <p className="text-gray-600 dark:text-gray-400">
            Статистика за последние {days} дней
          </p>
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <BarChart3 className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Всего генераций</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {analytics.total_generations}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Успешных</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {analytics.successful_generations}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg">
                <TrendingUp className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Успешность</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatPercentage(analytics.success_rate)}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                <Clock className="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Среднее время</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {formatTime(analytics.avg_generation_time_ms)}
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Category Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Filter className="w-5 h-5 text-emerald-500" />
              Популярные категории
            </h3>
            
            <div className="space-y-3">
              {Object.entries(analytics.category_stats)
                .sort(([,a], [,b]) => b - a)
                .map(([category, count]) => (
                  <div key={category} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-1 bg-gray-100 dark:bg-gray-700 rounded">
                        {getCategoryIcon(category)}
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {getCategoryName(category)}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
                          style={{
                            width: `${(count / Math.max(...Object.values(analytics.category_stats))) * 100}%`
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 dark:text-gray-400 w-8 text-right">
                        {count}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </motion.div>

          {/* Style Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-sm border border-gray-200 dark:border-gray-700"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Brain className="w-5 h-5 text-emerald-500" />
              Популярные стили
            </h3>
            
            <div className="space-y-3">
              {Object.entries(analytics.style_stats)
                .sort(([,a], [,b]) => b - a)
                .map(([style, count]) => (
                  <div key={style} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="p-1 bg-gray-100 dark:bg-gray-700 rounded">
                        {getStyleIcon(style)}
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white">
                        {getStyleName(style)}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
                          style={{
                            width: `${(count / Math.max(...Object.values(analytics.style_stats))) * 100}%`
                          }}
                        />
                      </div>
                      <span className="text-sm text-gray-600 dark:text-gray-400 w-8 text-right">
                        {count}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};
