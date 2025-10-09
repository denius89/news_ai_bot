import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { MobileHeader } from '../components/ui/Header';

interface Category {
  id: string;
  name: string;
  icon: string;
  enabled: boolean;
  subcategories: {
    id: string;
    name: string;
    enabled: boolean;
  }[];
}

interface NotificationSettings {
  push: boolean;
  email: boolean;
  digest: boolean;
  events: boolean;
  frequency: 'instant' | 'hourly' | 'daily' | 'weekly';
}

interface SettingsPageProps {
  theme: 'light' | 'dark';
  onThemeToggle: () => void;
}

const SettingsPage: React.FC<SettingsPageProps> = ({ theme }) => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [notifications, setNotifications] = useState<NotificationSettings>({
    push: true,
    email: false,
    digest: true,
    events: true,
    frequency: 'daily',
  });
  const [loading, setLoading] = useState(true);
  const [userInfo, setUserInfo] = useState({
    name: '',
    email: '',
    timezone: 'Europe/Moscow',
  });

  const mockCategories: Category[] = [
    {
      id: 'crypto',
      name: 'Криптовалюты',
      icon: '₿',
      enabled: true,
      subcategories: [
        { id: 'bitcoin', name: 'Bitcoin', enabled: true },
        { id: 'ethereum', name: 'Ethereum', enabled: true },
        { id: 'altcoins', name: 'Альткоины', enabled: false },
        { id: 'defi', name: 'DeFi', enabled: true },
      ],
    },
    {
      id: 'tech',
      name: 'Технологии',
      icon: '🤖',
      enabled: true,
      subcategories: [
        { id: 'ai', name: 'ИИ', enabled: true },
        { id: 'blockchain', name: 'Блокчейн', enabled: false },
        { id: 'startups', name: 'Стартапы', enabled: true },
      ],
    },
    {
      id: 'sports',
      name: 'Спорт',
      icon: '⚽',
      enabled: false,
      subcategories: [
        { id: 'football', name: 'Футбол', enabled: false },
        { id: 'basketball', name: 'Баскетбол', enabled: false },
        { id: 'tennis', name: 'Теннис', enabled: false },
      ],
    },
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setCategories(mockCategories);
      setLoading(false);
    }, 1000);
  }, []);

  const toggleCategory = (categoryId: string) => {
    setCategories(prev => prev.map(cat => 
      cat.id === categoryId 
        ? { ...cat, enabled: !cat.enabled }
        : cat
    ));
  };

  const toggleSubcategory = (categoryId: string, subcategoryId: string) => {
    setCategories(prev => prev.map(cat => 
      cat.id === categoryId 
        ? {
            ...cat,
            subcategories: cat.subcategories.map(sub => 
              sub.id === subcategoryId 
                ? { ...sub, enabled: !sub.enabled }
                : sub
            )
          }
        : cat
    ));
  };

  const updateNotificationSettings = (key: keyof NotificationSettings, value: any) => {
    setNotifications(prev => ({ ...prev, [key]: value }));
  };

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

  if (loading) {
    return (
      <div className="min-h-screen bg-bg">
        <MobileHeader title="Настройки" subtitle="Загрузка..." />
        <main className="container-main">
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-4 bg-surface-alt rounded w-3/4"></div>
                  <div className="h-3 bg-surface-alt rounded w-1/2"></div>
                </CardHeader>
                <CardContent>
                  <div className="h-3 bg-surface-alt rounded w-full mb-2"></div>
                  <div className="h-3 bg-surface-alt rounded w-2/3"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg">
      <MobileHeader 
        title="Настройки" 
        subtitle="Персонализация и уведомления"
      />
      
      <main className="container-main">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {/* User Profile */}
          <motion.section variants={itemVariants}>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Профиль пользователя</CardTitle>
                <CardDescription>
                  Основная информация о вашем аккаунте
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium text-text mb-2 block">
                    Имя
                  </label>
                  <Input
                    value={userInfo.name}
                    onChange={(e) => setUserInfo(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Введите ваше имя"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-text mb-2 block">
                    Email
                  </label>
                  <Input
                    type="email"
                    value={userInfo.email}
                    onChange={(e) => setUserInfo(prev => ({ ...prev, email: e.target.value }))}
                    placeholder="Введите ваш email"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-text mb-2 block">
                    Часовой пояс
                  </label>
                  <select 
                    className="input w-full"
                    value={userInfo.timezone}
                    onChange={(e) => setUserInfo(prev => ({ ...prev, timezone: e.target.value }))}
                  >
                    <option value="Europe/Moscow">Москва (UTC+3)</option>
                    <option value="Europe/London">Лондон (UTC+0)</option>
                    <option value="America/New_York">Нью-Йорк (UTC-5)</option>
                    <option value="Asia/Tokyo">Токио (UTC+9)</option>
                  </select>
                </div>
                <Button variant="primary" className="w-full">
                  Сохранить изменения
                </Button>
              </CardContent>
            </Card>
          </motion.section>

          {/* Categories */}
          <motion.section variants={itemVariants}>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Категории новостей</CardTitle>
                <CardDescription>
                  Выберите интересующие вас категории и подкатегории
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {categories.map((category) => (
                    <div key={category.id} className="border border-border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">{category.icon}</span>
                          <div>
                            <h4 className="font-medium text-text">{category.name}</h4>
                            <p className="text-sm text-muted-strong">
                              {category.subcategories.filter(sub => sub.enabled).length} из {category.subcategories.length} подкатегорий
                            </p>
                          </div>
                        </div>
                        <Button
                          variant={category.enabled ? 'primary' : 'secondary'}
                          size="sm"
                          onClick={() => toggleCategory(category.id)}
                        >
                          {category.enabled ? 'Включено' : 'Выключено'}
                        </Button>
                      </div>
                      
                      {category.enabled && (
                        <div className="space-y-2">
                          {category.subcategories.map((subcategory) => (
                            <div key={subcategory.id} className="flex items-center justify-between py-2 px-3 bg-surface-alt rounded-lg">
                              <span className="text-sm text-text">{subcategory.name}</span>
                              <Button
                                variant={subcategory.enabled ? 'primary' : 'secondary'}
                                size="sm"
                                onClick={() => toggleSubcategory(category.id, subcategory.id)}
                              >
                                {subcategory.enabled ? 'Вкл' : 'Выкл'}
                              </Button>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.section>

          {/* Notifications */}
          <motion.section variants={itemVariants}>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Уведомления</CardTitle>
                <CardDescription>
                  Настройте получение уведомлений
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-text">Push-уведомления</h4>
                      <p className="text-sm text-muted-strong">Получать уведомления в браузере</p>
                    </div>
                    <Button
                      variant={notifications.push ? 'primary' : 'secondary'}
                      size="sm"
                      onClick={() => updateNotificationSettings('push', !notifications.push)}
                    >
                      {notifications.push ? 'Включено' : 'Выключено'}
                    </Button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-text">Email-уведомления</h4>
                      <p className="text-sm text-muted-strong">Получать дайджесты на email</p>
                    </div>
                    <Button
                      variant={notifications.email ? 'primary' : 'secondary'}
                      size="sm"
                      onClick={() => updateNotificationSettings('email', !notifications.email)}
                    >
                      {notifications.email ? 'Включено' : 'Выключено'}
                    </Button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-text">AI-дайджесты</h4>
                      <p className="text-sm text-muted-strong">Персональные дайджесты от ИИ</p>
                    </div>
                    <Button
                      variant={notifications.digest ? 'primary' : 'secondary'}
                      size="sm"
                      onClick={() => updateNotificationSettings('digest', !notifications.digest)}
                    >
                      {notifications.digest ? 'Включено' : 'Выключено'}
                    </Button>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-text">Важные события</h4>
                      <p className="text-sm text-muted-strong">Уведомления о важных событиях</p>
                    </div>
                    <Button
                      variant={notifications.events ? 'primary' : 'secondary'}
                      size="sm"
                      onClick={() => updateNotificationSettings('events', !notifications.events)}
                    >
                      {notifications.events ? 'Включено' : 'Выключено'}
                    </Button>
                  </div>
                </div>
                
                <div>
                  <label className="text-sm font-medium text-text mb-2 block">
                    Частота уведомлений
                  </label>
                  <select 
                    className="input w-full"
                    value={notifications.frequency}
                    onChange={(e) => updateNotificationSettings('frequency', e.target.value)}
                  >
                    <option value="instant">Мгновенно</option>
                    <option value="hourly">Каждый час</option>
                    <option value="daily">Ежедневно</option>
                    <option value="weekly">Еженедельно</option>
                  </select>
                </div>
              </CardContent>
            </Card>
          </motion.section>

          {/* Export/Import */}
          <motion.section variants={itemVariants}>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Экспорт и импорт</CardTitle>
                <CardDescription>
                  Управление настройками и данными
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Button variant="secondary" className="w-full">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    Экспорт настроек
                  </Button>
                  <Button variant="secondary" className="w-full">
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
                    </svg>
                    Импорт настроек
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.section>

          {/* Danger Zone */}
          <motion.section variants={itemVariants}>
            <Card className="border-error/20">
              <CardHeader>
                <CardTitle className="text-lg text-error">Опасная зона</CardTitle>
                <CardDescription>
                  Необратимые действия с вашим аккаунтом
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <Button variant="secondary" className="w-full text-error border-error/20 hover:bg-error/10">
                  Сбросить все настройки
                </Button>
                <Button variant="secondary" className="w-full text-error border-error/20 hover:bg-error/10">
                  Удалить аккаунт
                </Button>
              </CardContent>
            </Card>
          </motion.section>
        </motion.div>
      </main>
    </div>
  );
};

export default SettingsPage;
