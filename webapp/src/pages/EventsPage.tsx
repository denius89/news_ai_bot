import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { MobileHeader } from '../components/ui/Header';

interface Event {
  id: string;
  title: string;
  description: string;
  category: string;
  date: string;
  time: string;
  importance: 'high' | 'medium' | 'low';
  source: string;
  impact: string;
}

const EventsPage: React.FC = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDate, setSelectedDate] = useState('today');

  const categories = [
    { id: 'all', label: 'Все', icon: '📅' },
    { id: 'crypto', label: 'Криптовалюты', icon: '₿' },
    { id: 'economics', label: 'Экономика', icon: '📊' },
    { id: 'politics', label: 'Политика', icon: '🏛️' },
    { id: 'sports', label: 'Спорт', icon: '⚽' },
  ];

  const dateFilters = [
    { id: 'today', label: 'Сегодня' },
    { id: 'tomorrow', label: 'Завтра' },
    { id: 'week', label: 'Неделя' },
    { id: 'month', label: 'Месяц' },
  ];

  // Mock data
  const mockEvents: Event[] = [
    {
      id: '1',
      title: 'Заседание ФРС США',
      description: 'Решение по процентным ставкам и денежно-кредитной политике',
      category: 'economics',
      date: '2025-01-06',
      time: '14:00',
      importance: 'high',
      source: 'Federal Reserve',
      impact: 'Высокий',
    },
    {
      id: '2',
      title: 'Запуск Ethereum 2.0 обновления',
      description: 'Крупное обновление сети Ethereum с улучшениями производительности',
      category: 'crypto',
      date: '2025-01-07',
      time: '12:00',
      importance: 'high',
      source: 'Ethereum Foundation',
      impact: 'Высокий',
    },
    {
      id: '3',
      title: 'Чемпионат мира по футболу - Финал',
      description: 'Решающий матч чемпионата мира по футболу',
      category: 'sports',
      date: '2025-01-08',
      time: '18:00',
      importance: 'medium',
      source: 'FIFA',
      impact: 'Средний',
    },
    {
      id: '4',
      title: 'Саммит G7',
      description: 'Ежегодная встреча лидеров стран G7',
      category: 'politics',
      date: '2025-01-10',
      time: '09:00',
      importance: 'high',
      source: 'G7 Secretariat',
      impact: 'Высокий',
    },
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setEvents(mockEvents);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredEvents = events.filter(event => {
    const matchesCategory = selectedCategory === 'all' || event.category === selectedCategory;
    
    // Simple date filtering logic
    const eventDate = new Date(event.date);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    let matchesDate = false;
    switch (selectedDate) {
      case 'today':
        matchesDate = eventDate.toDateString() === today.toDateString();
        break;
      case 'tomorrow':
        matchesDate = eventDate.toDateString() === tomorrow.toDateString();
        break;
      case 'week':
        const weekFromNow = new Date(today);
        weekFromNow.setDate(weekFromNow.getDate() + 7);
        matchesDate = eventDate >= today && eventDate <= weekFromNow;
        break;
      case 'month':
        const monthFromNow = new Date(today);
        monthFromNow.setMonth(monthFromNow.getMonth() + 1);
        matchesDate = eventDate >= today && eventDate <= monthFromNow;
        break;
    }
    
    return matchesCategory && matchesDate;
  });

  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'high': return 'text-error bg-error/10 border-error/20';
      case 'medium': return 'text-warning bg-warning/10 border-warning/20';
      case 'low': return 'text-success bg-success/10 border-success/20';
      default: return 'text-muted bg-muted/10 border-muted/20';
    }
  };

  const getImportanceLabel = (importance: string) => {
    switch (importance) {
      case 'high': return 'Высокая';
      case 'medium': return 'Средняя';
      case 'low': return 'Низкая';
      default: return 'Неизвестно';
    }
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
        <MobileHeader title="События" subtitle="Загрузка..." />
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
        title="События" 
        subtitle={`${filteredEvents.length} событий`}
        actions={
          <Button variant="ghost" size="sm">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </Button>
        }
      />
      
      <main className="container-main">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {/* Filters */}
          <motion.section variants={itemVariants}>
            <div className="space-y-4">
              {/* Date Filters */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Временной период</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {dateFilters.map((filter) => (
                      <Button
                        key={filter.id}
                        variant={selectedDate === filter.id ? 'primary' : 'secondary'}
                        size="sm"
                        onClick={() => setSelectedDate(filter.id)}
                      >
                        {filter.label}
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Category Filters */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Категории</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {categories.map((category) => (
                      <Button
                        key={category.id}
                        variant={selectedCategory === category.id ? 'primary' : 'secondary'}
                        size="sm"
                        onClick={() => setSelectedCategory(category.id)}
                      >
                        <span className="mr-1">{category.icon}</span>
                        {category.label}
                      </Button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </motion.section>

          {/* Events List */}
          <motion.section variants={itemVariants}>
            <div className="space-y-4">
              {filteredEvents.map((event, index) => (
                <motion.div
                  key={event.id}
                  variants={itemVariants}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="hover-lift">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg leading-tight mb-2">
                            {event.title}
                          </CardTitle>
                          <CardDescription className="mb-3">
                            {event.source} • {new Date(event.date).toLocaleDateString('ru-RU')} в {event.time}
                          </CardDescription>
                        </div>
                        <div className="flex flex-col items-end space-y-2 ml-4">
                          <div className={`text-xs px-2 py-1 rounded-full border ${getImportanceColor(event.importance)}`}>
                            {getImportanceLabel(event.importance)}
                          </div>
                          <div className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                            {categories.find(c => c.id === event.category)?.icon} {categories.find(c => c.id === event.category)?.label}
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent>
                      <p className="text-text text-sm leading-relaxed mb-4">
                        {event.description}
                      </p>
                      
                      <div className="flex items-center justify-between pt-4 border-t border-border">
                        <div className="text-sm text-muted">
                          Ожидаемое влияние: <span className="font-medium text-text">{event.impact}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Button variant="secondary" size="sm">
                            Добавить в календарь
                          </Button>
                          <Button variant="ghost" size="sm">
                            Поделиться
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Calendar View */}
          <motion.section variants={itemVariants}>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Календарный вид</CardTitle>
                <CardDescription>
                  Все события на временной шкале
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <div className="text-4xl mb-4">📅</div>
                  <h3 className="text-lg font-semibold text-text mb-2">
                    Календарь событий
                  </h3>
                  <p className="text-muted mb-4">
                    Здесь будет отображаться интерактивный календарь
                  </p>
                  <Button variant="secondary">
                    Открыть календарь
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.section>

          {/* Empty State */}
          {filteredEvents.length === 0 && (
            <motion.section variants={itemVariants} className="text-center py-20">
              <div className="text-6xl mb-4">📅</div>
              <h3 className="text-xl font-semibold text-text mb-2">
                События не найдены
              </h3>
              <p className="text-muted mb-6">
                Попробуйте изменить фильтры или выбрать другой временной период
              </p>
              <Button 
                variant="secondary" 
                onClick={() => {
                  setSelectedCategory('all');
                  setSelectedDate('today');
                }}
              >
                Сбросить фильтры
              </Button>
            </motion.section>
          )}
        </motion.div>
      </main>
    </div>
  );
};

export default EventsPage;
