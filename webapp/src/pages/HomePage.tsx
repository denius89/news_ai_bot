import React, { useState, useEffect, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Header } from '../components/ui/Header';
import { Rocket, Bot, Calendar, Settings, BarChart3, Newspaper, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTelegramUser } from '../hooks/useTelegramUser';
import { shouldReduceMotion, logDevicePerformanceInfo } from '../utils/performance';

interface HomePageProps {
  theme: 'light' | 'dark';
  onThemeToggle: () => void;
  onNavigate?: (page: string) => void;
}

interface DashboardStats {
  news_today: {
    count: number;
    change: number;
  };
  active_users: {
    count: number;
    change: number;
  };
  events_week: {
    count: number;
    change: number;
  };
  ai_digests: {
    count: number;
    change: number;
  };
}

const HomePage: React.FC<HomePageProps> = ({ theme, onThemeToggle, onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [statsLoading, setStatsLoading] = useState(true);
  
  // Гибридный подход: useTelegramUser для UI, useAuth для API
  const { telegramUser } = useTelegramUser();
  const { authHeaders } = useAuth();

  useEffect(() => {
    // Логируем информацию о производительности устройства
    logDevicePerformanceInfo();
    
    fetchDashboardStats();
    
    // Обновляем данные каждые 5 минут (вместо 30 секунд) для экономии батареи
    const interval = setInterval(fetchDashboardStats, 300000);
    
    return () => clearInterval(interval);
  }, []);

  // Функция для персонализированного приветствия
  const getPersonalizedGreeting = () => {
    if (!telegramUser?.first_name) {
      return "Добро пожаловать в PulseAI";
    }
    
    const timeOfDay = new Date().getHours();
    
    let greeting = "";
    if (timeOfDay < 12) {
      greeting = "Доброе утро";
    } else if (timeOfDay < 18) {
      greeting = "Добрый день";
    } else {
      greeting = "Добрый вечер";
    }
    
    return `${greeting}, ${telegramUser.first_name}!`;
  };

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch('/api/dashboard/stats', {
        headers: authHeaders
      });
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setStats(data.data);
        }
      }
    } catch (error) {
      console.error('Ошибка загрузки статистики:', error);
    } finally {
      setStatsLoading(false);
    }
  };

  // Определяем, нужно ли отключить анимации для экономии батареи
  const reduceMotion = useMemo(() => shouldReduceMotion(), []);

  const containerVariants = useMemo(() => {
    if (reduceMotion) {
      return {
        hidden: { opacity: 1 },
        visible: { opacity: 1 },
      };
    }
    return {
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          duration: 0.3,
          // Убрали staggerChildren для экономии ресурсов
        },
      },
    };
  }, [reduceMotion]);

  const itemVariants = useMemo(() => {
    if (reduceMotion) {
      return {
        hidden: { opacity: 1 },
        visible: { opacity: 1 },
      };
    }
    return {
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          duration: 0.3,
          ease: 'easeOut' as const,
        },
      },
    };
  }, [reduceMotion]);

  const formatChange = (change: number): string => {
    if (change > 0) {
      return `+${change}%`;
    } else if (change < 0) {
      return `${change}%`;
    } else {
      return 'стабильно';
    }
  };

  const getChangeColor = (change: number): string => {
    if (change > 0) return 'text-green-600 dark:text-green-400';
    if (change < 0) return 'text-red-600 dark:text-red-400';
    return 'text-muted-strong';
  };

  const statsData = stats ? [
    { label: 'Новостей сегодня', value: stats.news_today.count.toLocaleString(), trend: formatChange(stats.news_today.change), color: getChangeColor(stats.news_today.change) },
    { label: 'Активных пользователей', value: stats.active_users.count.toString(), trend: formatChange(stats.active_users.change), color: getChangeColor(stats.active_users.change) },
    { label: 'Событий на неделю', value: stats.events_week.count.toString(), trend: formatChange(stats.events_week.change), color: getChangeColor(stats.events_week.change) },
    { label: 'AI дайджестов', value: stats.ai_digests.count.toString(), trend: formatChange(stats.ai_digests.change), color: getChangeColor(stats.ai_digests.change) },
  ] : [
    { label: 'Новостей сегодня', value: '...', trend: '...', color: 'text-muted-strong' },
    { label: 'Активных пользователей', value: '...', trend: '...', color: 'text-muted-strong' },
    { label: 'Событий на неделю', value: '...', trend: '...', color: 'text-muted-strong' },
    { label: 'AI дайджестов', value: '...', trend: '...', color: 'text-muted-strong' },
  ];

  const quickActions = [
    {
      title: 'Новости',
      description: 'Последние новости по всем категориям',
      page: 'news',
      icon: <Newspaper className="w-6 h-6 text-primary" />,
    },
    {
      title: 'AI Дайджест',
      description: 'Ваш AI-дайджест — без лишнего шума',
      page: 'digest',
      icon: <Bot className="w-6 h-6 text-primary" />,
    },
    {
      title: 'События',
      description: 'Не пропустите то, что действительно важно',
      page: 'events',
      icon: <Calendar className="w-6 h-6 text-primary" />,
    },
    {
      title: 'Настройки',
      description: 'Настройте PulseAI под себя',
      page: 'settings',
      icon: <Settings className="w-6 h-6 text-primary" />,
    },
  ];

  return (
    <div className="min-h-screen bg-bg">
      <Header 
        title="PulseAI" 
        subtitle="Ваш персональный AI-помощник для новостей"
        theme={theme}
        onThemeToggle={onThemeToggle}
      />
      
      <main className="container-main pb-28 md:pb-32">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-8"
        >
          {/* Welcome Section */}
          <motion.section variants={itemVariants}>
            <Card className="text-center py-8 bg-gradient-to-br from-primary/5 to-accent/5 border-primary/20">
              <CardContent>
                <div className="flex justify-center mb-4">
                  <Rocket className="w-16 h-16 text-primary" />
                </div>
                <h1 className="text-3xl font-bold text-text mb-2">
                  {getPersonalizedGreeting()}
                </h1>
                <p className="text-muted-strong text-lg mb-6 max-w-2xl mx-auto">
                  {telegramUser ? 
                    "Ваш AI уже анализирует новости и готовит персональные дайджесты" : 
                    "Добро пожаловать в PulseAI — новости, которые работают на вас"
                  }
                </p>
                <Button 
                  size="lg" 
                  className="btn-primary hover:scale-105 transition-transform duration-200"
                  onClick={() => onNavigate?.('news')}
                >
                  {telegramUser ? "Поехали!" : "Начать с PulseAI"}
                </Button>
              </CardContent>
            </Card>
          </motion.section>

          {/* Stats Section */}
          <motion.section variants={itemVariants}>
            <h2 className="text-2xl font-semibold text-text mb-6 flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-primary" />
              Статистика
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-5 auto-rows-[1fr]">
              {statsData.map((stat) => (
                <motion.div
                  key={stat.label}
                  variants={itemVariants}
                  className={`h-full flex flex-col justify-between items-center text-center 
                              bg-white dark:bg-surface-alt rounded-2xl 
                              shadow-[0_1px_6px_rgba(0,0,0,0.04)] 
                              py-5 px-4 transition-all duration-300 ${!reduceMotion ? 'hover:scale-[1.01]' : ''}
                              ${stat.label.length > 25 ? "min-h-[140px]" : "min-h-[120px]"}`}
                >
                  <div className="text-2xl font-semibold text-text dark:text-white">{stat.value}</div>
                  <p className="text-sm text-muted-strong leading-tight text-balance">
                    {stat.label}
                  </p>
                  {stat.trend && (
                    <p className={`text-xs font-medium mt-1 ${stat.color}`}>{stat.trend}</p>
                  )}
                </motion.div>
              ))}
            </div>
            {statsLoading && (
              <div className="text-center text-muted-strong mt-4">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto mb-2"></div>
                Загрузка данных...
              </div>
            )}
          </motion.section>

          {/* Quick Actions */}
          <motion.section variants={itemVariants}>
            <h2 className="text-2xl font-semibold text-text mb-6 flex items-center gap-2">
              <Sparkles className="w-6 h-6 text-primary" />
              Быстрые действия
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {quickActions.map((action) => (
                <motion.div
                  key={action.title}
                  variants={itemVariants}
                >
                  <Card className={`h-full hover:shadow-lg ${!reduceMotion ? 'hover:scale-[1.01]' : ''} transition-all duration-300 cursor-pointer group`}
                        onClick={() => onNavigate?.(action.page)}>
                    <CardHeader>
                      <div className="flex items-center space-x-3">
                        <div className="group-hover:scale-110 transition-transform duration-200">{action.icon}</div>
                        <div>
                          <CardTitle className="text-lg group-hover:text-primary transition-colors">{action.title}</CardTitle>
                          <CardDescription className="text-muted-strong">{action.description}</CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <Button 
                        variant="outline" 
                        className="w-full hover:bg-primary/10 hover:text-primary hover:border-primary transition-all duration-200"
                        onClick={() => onNavigate?.(action.page)}
                      >
                        {action.title === 'AI Дайджест' ? 'Смотреть дайджест' : 
                         action.title === 'События' ? 'Смотреть календарь' : 
                         action.title === 'Настройки' ? 'Открыть настройки' : 'Открыть'}
                      </Button>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.section>
          
          {/* Дополнительный отступ для мобильных устройств */}
          <div className="h-10 md:h-16" />
        </motion.div>
      </main>
    </div>
  );
};

export default HomePage;
