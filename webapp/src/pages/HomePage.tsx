import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Header } from '../components/ui/Header';

const HomePage: React.FC = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        ease: 'easeOut',
      },
    },
  };

  const stats = [
    { label: 'Новостей сегодня', value: '1,247', trend: '+12%' },
    { label: 'Активных источников', value: '89', trend: '+3' },
    { label: 'Категорий', value: '12', trend: 'стабильно' },
    { label: 'AI дайджестов', value: '156', trend: '+8' },
  ];

  const quickActions = [
    {
      title: '📰 Новости',
      description: 'Последние новости по всем категориям',
      href: '/news',
      icon: '📰',
    },
    {
      title: '🤖 AI Дайджест',
      description: 'Персональный дайджест от ИИ',
      href: '/digest',
      icon: '🤖',
    },
    {
      title: '📅 События',
      description: 'Календарь важных событий',
      href: '/events',
      icon: '📅',
    },
    {
      title: '⚙️ Настройки',
      description: 'Управление подписками и уведомлениями',
      href: '/settings',
      icon: '⚙️',
    },
  ];

  return (
    <div className="min-h-screen bg-bg">
      <Header 
        title="PulseAI" 
        subtitle="Ваш персональный AI-помощник для новостей"
      />
      
      <main className="container-main">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-8"
        >
          {/* Welcome Section */}
          <motion.section variants={itemVariants}>
            <Card className="text-center py-8">
              <CardContent>
                <div className="text-6xl mb-4">🚀</div>
                <h1 className="text-3xl font-bold text-text mb-2">
                  Добро пожаловать в PulseAI
                </h1>
                <p className="text-muted text-lg mb-6 max-w-2xl mx-auto">
                  Получайте персональные новости и аналитику, созданную с помощью 
                  искусственного интеллекта специально для вас
                </p>
                <Button size="lg" className="btn-primary">
                  Начать работу
                </Button>
              </CardContent>
            </Card>
          </motion.section>

          {/* Stats Section */}
          <motion.section variants={itemVariants}>
            <h2 className="text-2xl font-semibold text-text mb-6">Статистика</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  variants={itemVariants}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="text-center">
                    <CardContent className="pt-6">
                      <div className="text-2xl font-bold text-text">{stat.value}</div>
                      <div className="text-sm text-muted">{stat.label}</div>
                      <div className="text-xs text-success mt-1">{stat.trend}</div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Quick Actions */}
          <motion.section variants={itemVariants}>
            <h2 className="text-2xl font-semibold text-text mb-6">Быстрые действия</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {quickActions.map((action, index) => (
                <motion.div
                  key={action.title}
                  variants={itemVariants}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="h-full">
                    <CardHeader>
                      <div className="flex items-center space-x-3">
                        <div className="text-2xl">{action.icon}</div>
                        <div>
                          <CardTitle className="text-lg">{action.title}</CardTitle>
                          <CardDescription>{action.description}</CardDescription>
                        </div>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <Button 
                        variant="secondary" 
                        className="w-full"
                        onClick={() => window.location.href = action.href}
                      >
                        Открыть
                      </Button>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Recent Activity */}
          <motion.section variants={itemVariants}>
            <Card>
              <CardHeader>
                <CardTitle>Последняя активность</CardTitle>
                <CardDescription>
                  Ваши недавние действия в системе
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3 p-3 bg-surface-alt rounded-lg">
                    <div className="w-2 h-2 bg-primary rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-text">
                        Получен новый дайджест по криптовалютам
                      </p>
                      <p className="text-xs text-muted">2 минуты назад</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 p-3 bg-surface-alt rounded-lg">
                    <div className="w-2 h-2 bg-success rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-text">
                        Добавлен новый источник новостей
                      </p>
                      <p className="text-xs text-muted">1 час назад</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 p-3 bg-surface-alt rounded-lg">
                    <div className="w-2 h-2 bg-warning rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-text">
                        Обновлены настройки уведомлений
                      </p>
                      <p className="text-xs text-muted">3 часа назад</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.section>
        </motion.div>
      </main>
    </div>
  );
};

export default HomePage;
