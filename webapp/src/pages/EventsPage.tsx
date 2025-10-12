import React, { useState, useEffect, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { MobileHeader } from '../components/ui/Header';
import { MiniCalendarWidget } from '../components/events/MiniCalendarWidget';
import { useCalendarExport, useShareEvent } from '../hooks/useEventActions';
import { 
  CalendarDays, 
  Calendar, 
  CalendarPlus,
  CalendarRange,
  Bitcoin,
  Trophy,
  Cpu,
  Globe2,
  LineChart,
  Share2,
  ExternalLink,
  X,
  Clock,
  MapPin,
  Building,
  ChevronUp
} from 'lucide-react';

interface Event {
  id: string;
  title: string;
  description: string;
  category: string;
  date: string;
  time: string;
  importance: number;
  source: string;
  impact?: string;
  starts_at?: string;
  ends_at?: string;
  location?: string;
  link?: string;
}

interface EventsPageProps {
  theme: 'light' | 'dark';
  onThemeToggle: () => void;
}

// Event Detail Modal
interface EventDetailModalProps {
  event: Event | null;
  isOpen: boolean;
  onClose: () => void;
}

const EventDetailModal: React.FC<EventDetailModalProps> = ({ event, isOpen, onClose }) => {
  const { exportEvent } = useCalendarExport();
  const { shareEvent } = useShareEvent();

  if (!event) return null;

  const handleExport = () => {
    exportEvent(event);
  };

  const handleShare = async () => {
    await shareEvent(event);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
            onClick={onClose}
          />
          
          {/* Modal */}
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            className="fixed inset-x-0 bottom-0 md:inset-x-auto md:top-1/2 md:left-1/2 md:bottom-auto md:-translate-x-1/2 md:-translate-y-1/2 z-50 md:rounded-3xl bg-surface border border-border shadow-2xl max-h-[85vh] overflow-hidden md:max-w-2xl w-full"
          >
            {/* Header */}
            <div className="flex items-start justify-between p-6 border-b border-border">
              <div className="flex-1">
                <div className="flex gap-2 mb-3">
                  <div className="flex items-center gap-1 text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                    {(() => {
                      const icons: Record<string, React.ComponentType<any>> = {
                        all: CalendarRange,
                        crypto: Bitcoin,
                        sports: Trophy,
                        tech: Cpu,
                        world: Globe2,
                        markets: LineChart
                      };
                      const IconComponent = icons[event.category] || CalendarRange;
                      return <IconComponent className="w-3 h-3" />;
                    })()}
                    <span>{event.category}</span>
                  </div>
                  <div className={`text-xs px-2 py-1 rounded-full border ${
                    event.importance >= 0.8 ? 'text-red-600 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' :
                    event.importance >= 0.6 ? 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800' :
                    'text-green-600 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                  }`}>
                    {event.importance >= 0.8 ? 'Высокая' : event.importance >= 0.6 ? 'Средняя' : 'Низкая'} важность
                  </div>
                  <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 bg-muted/10 px-2 py-1 rounded-full">
                    <Clock className="w-3 h-3" />
                    {event.date} в {event.time}
                  </div>
                </div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">{event.title}</h2>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-surface-alt rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="prose prose-sm max-w-none">
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed">{event.description}</p>
              </div>
              
              {/* Metadata */}
              <div className="mt-6 space-y-3">
                {event.location && (
                  <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                    <MapPin className="w-4 h-4" />
                    <span>{event.location}</span>
                  </div>
                )}
                <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                  <Building className="w-4 h-4" />
                  <span>Источник: {event.source}</span>
                </div>
                {event.impact && (
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Ожидаемое влияние: <span className="font-medium text-gray-900 dark:text-white">{event.impact}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Footer Actions */}
            <div className="flex gap-3 p-6 pt-0">
              <Button onClick={handleExport} className="flex-1">
                <CalendarPlus className="w-4 h-4 mr-2" />
                Добавить в календарь
              </Button>
              <Button variant="secondary" onClick={handleShare}>
                <Share2 className="w-4 h-4 mr-2" />
                Поделиться
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

const EventsPage: React.FC<EventsPageProps> = ({ theme: _theme }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedDate, setSelectedDate] = useState('month');
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [calendarOpen, setCalendarOpen] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);

  // Category icons mapping
  const getCategoryIcon = (categoryId: string) => {
    const icons: Record<string, React.ComponentType<any>> = {
      all: CalendarRange,
      crypto: Bitcoin,
      sports: Trophy,
      tech: Cpu,
      world: Globe2,
      markets: LineChart
    };
    return icons[categoryId] || CalendarRange;
  };

  const categories = [
    { id: 'all', label: 'Все' },
    { id: 'crypto', label: 'Криптовалюты' },
    { id: 'sports', label: 'Спорт' },
    { id: 'tech', label: 'Технологии' },
    { id: 'world', label: 'Мир' },
    { id: 'markets', label: 'Рынки' },
  ];

  const dateFilters = [
    { id: 'today', label: 'Сегодня' },
    { id: 'tomorrow', label: 'Завтра' },
    { id: 'week', label: 'Неделя' },
    { id: 'month', label: 'Месяц' },
  ];

  // Hooks for actions
  const { exportEvent } = useCalendarExport();
  const { shareEvent, notification } = useShareEvent();

  // Fetch events from API
  const fetchEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams();
      params.append('min_importance', '0.0');
      
      if (selectedCategory !== 'all') {
        params.append('category', selectedCategory);
      }
      
      const daysMap: { [key: string]: number } = {
        'today': 1,
        'tomorrow': 2,
        'week': 7,
        'month': 30
      };
      params.append('days', daysMap[selectedDate]?.toString() || '30');
      
      const response = await fetch(`/api/events/upcoming?${params.toString()}`);
      const data = await response.json();
      
      if (data.success || data.status === 'success') {
        const transformedEvents: Event[] = data.data.events.map((event: any) => ({
          id: event.id.toString(),
          title: event.title,
          description: event.description || '',
          category: event.category,
          date: new Date(event.starts_at).toISOString().split('T')[0],
          time: new Date(event.starts_at).toTimeString().slice(0, 5),
          importance: event.importance || 0,
          source: event.source,
          impact: event.importance >= 0.8 ? 'Высокий' : event.importance >= 0.6 ? 'Средний' : 'Низкий',
          starts_at: event.starts_at,
          ends_at: event.ends_at,
          location: event.location,
          link: event.link,
        }));
        
        setEvents(transformedEvents);
      } else {
        setError(data.error || 'Ошибка загрузки событий');
      }
    } catch (err) {
      setError('Не удалось загрузить события');
      console.error('Failed to fetch events:', err);
    } finally {
      setLoading(false);
    }
  };

  // Load events on component mount and when filters change
  useEffect(() => {
    fetchEvents();
  }, [selectedCategory, selectedDate]);

  // Track scroll position for Scroll to Top button
  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Group events by date for timeline
  const eventsByDate = useMemo(() => {
    const groups: { [key: string]: Event[] } = {};
    events.forEach(event => {
      const dateKey = event.date;
      if (!groups[dateKey]) {
        groups[dateKey] = [];
      }
      groups[dateKey].push(event);
    });
    return groups;
  }, [events]);

  // Sort dates
  const sortedDates = useMemo(() => {
    return Object.keys(eventsByDate).sort();
  }, [eventsByDate]);

  // Format date for display
  const formatDateDisplay = (dateStr: string) => {
    const date = new Date(dateStr);
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    if (date.toDateString() === today.toDateString()) {
      return 'Сегодня';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'Завтра';
    } else {
      return date.toLocaleDateString('ru', { day: 'numeric', month: 'long' });
    }
  };

  // Handle date selection from calendar
  const handleDateSelect = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    const eventsOnDate = eventsByDate[dateStr];
    
    if (eventsOnDate && eventsOnDate.length > 0) {
      // Scroll to events for this date
      const element = document.getElementById(`date-group-${dateStr}`);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    }
    setCalendarOpen(false);
  };

  // Handle event actions
  const handleExportEvent = (event: Event) => {
    exportEvent(event);
  };

  const handleShareEvent = async (event: Event) => {
    await shareEvent(event);
  };

  const handleOpenDetail = (event: Event) => {
    setSelectedEvent(event);
    setIsModalOpen(true);
  };

  // Scroll to top handler
  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: 'smooth'
    });
  };

  // Get importance color for timeline dot
  const getImportanceColor = (importance: number) => {
    if (importance >= 0.8) return 'bg-red-500 dark:bg-red-600';
    if (importance >= 0.6) return 'bg-yellow-500 dark:bg-yellow-600';
    return 'bg-green-500 dark:bg-green-600';
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  // Show loading state
  if (loading) {
    return (
      <div className="min-h-screen bg-bg">
        <MobileHeader title="События" />
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted">Загрузка событий...</p>
          </div>
        </div>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="min-h-screen bg-bg">
        <MobileHeader title="События" />
        <div className="flex items-center justify-center min-h-[50vh]">
          <div className="text-center">
            <div className="text-error text-6xl mb-4">⚠️</div>
            <h2 className="text-xl font-semibold text-text mb-2">Ошибка загрузки</h2>
            <p className="text-muted mb-4">{error}</p>
            <Button onClick={fetchEvents}>
              Попробовать снова
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg">
      <MobileHeader 
        title="События" 
        actions={
          <Button 
            size="sm" 
            variant="secondary"
            onClick={() => setCalendarOpen(true)}
          >
            <Calendar className="w-4 h-4 mr-2" />
            Календарь
          </Button>
        }
      />

      {/* Notification */}
      {notification && (
        <motion.div
          initial={{ opacity: 0, y: -50 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -50 }}
          className="fixed top-16 left-1/2 -translate-x-1/2 z-50 bg-surface border border-border rounded-lg px-4 py-2 shadow-lg"
        >
          {notification}
        </motion.div>
      )}

      {/* Calendar Modal */}
      <AnimatePresence>
        {calendarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 0.5 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
              onClick={() => setCalendarOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-x-4 top-20 z-50 md:inset-x-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:max-w-md"
            >
              <MiniCalendarWidget 
                events={events}
                onDateSelect={handleDateSelect}
                className="shadow-2xl"
              />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      <main className="container-main pb-32">
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
                    {categories.map((category) => {
                      const IconComponent = getCategoryIcon(category.id);
                      return (
                        <Button
                          key={category.id}
                          variant={selectedCategory === category.id ? 'primary' : 'secondary'}
                          size="sm"
                          onClick={() => setSelectedCategory(category.id)}
                        >
                          <IconComponent className="w-4 h-4 mr-1.5" />
                          {category.label}
                        </Button>
                      );
                    })}
                  </div>
                </CardContent>
              </Card>
            </div>
          </motion.section>

          {/* Events Timeline */}
          <motion.section variants={itemVariants}>
            <div className="space-y-8">
              {sortedDates.length === 0 ? (
                // Empty State
                <motion.div variants={itemVariants} className="text-center py-20">
                  <Calendar className="w-16 h-16 mx-auto mb-4 text-muted opacity-50" />
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
                      setSelectedDate('month');
                    }}
                  >
                    Сбросить фильтры
                  </Button>
                </motion.div>
              ) : (
                sortedDates.map((dateStr, dateIndex) => {
                  const dayEvents = eventsByDate[dateStr];
                  return (
                    <motion.div
                      key={dateStr}
                      id={`date-group-${dateStr}`}
                      variants={itemVariants}
                      transition={{ delay: dateIndex * 0.1 }}
                      className="mb-8"
                    >
                      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                        <CalendarDays className="w-5 h-5" />
                        {formatDateDisplay(dateStr)}
                        <span className="text-sm text-gray-500 dark:text-gray-400 font-normal">({dayEvents.length} событий)</span>
                      </h3>
                      
                      <div className="relative pl-8 space-y-4">
                        {/* Timeline line */}
                        <div className="absolute left-2.5 top-0 bottom-0 w-0.5 bg-border" />
                        
                        {/* Event cards */}
                        {dayEvents.map((event, eventIndex) => (
                          <motion.div
                            key={event.id}
                            className="relative"
                            variants={itemVariants}
                            transition={{ delay: (dateIndex * 0.1) + (eventIndex * 0.05) }}
                          >
                            {/* Timeline dot */}
                            <div className={`absolute -left-6 top-3 w-3 h-3 rounded-full ${getImportanceColor(event.importance)} ring-4 ring-background`} />
                            
                            {/* Card */}
                            <Card className="hover-lift cursor-pointer group">
                              <CardContent className="p-4">
                                {/* Header: time + badges */}
                                <div className="flex items-start justify-between mb-2">
                                  <div className="flex items-center gap-2 text-sm font-medium text-text">
                                    <Clock className="w-4 h-4 text-muted" />
                                    <span>{event.time}</span>
                                  </div>
                                  <div className="flex gap-1.5">
                                    <div className="flex items-center gap-1 text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                                      {(() => {
                                        const IconComponent = getCategoryIcon(event.category);
                                        return <IconComponent className="w-3 h-3" />;
                                      })()}
                                      <span>{categories.find(c => c.id === event.category)?.label}</span>
                                    </div>
                                    <div className={`text-xs px-2 py-1 rounded-full border ${
                                      event.importance >= 0.8 ? 'text-red-600 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800' :
                                      event.importance >= 0.6 ? 'text-yellow-600 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800' :
                                      'text-green-600 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                                    }`}>
                                      {event.importance >= 0.8 ? 'Высокая' : event.importance >= 0.6 ? 'Средняя' : 'Низкая'}
                                    </div>
                                  </div>
                                </div>
                                
                                {/* Title */}
                                <h4 className="font-semibold text-base text-text mb-2 line-clamp-2">{event.title}</h4>
                                
                                {/* Preview */}
                                <p className="text-sm text-gray-500 dark:text-gray-400 line-clamp-2 mb-3">{event.description}</p>
                                
                                {/* Footer: metadata + quick actions */}
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
                                    {event.location && (
                                      <span className="flex items-center gap-1">
                                        <MapPin className="w-3 h-3" />
                                        {event.location}
                                      </span>
                                    )}
                                    <span className="flex items-center gap-1">
                                      <Building className="w-3 h-3" />
                                      {event.source}
                                    </span>
                                  </div>
                                  
                                  {/* Quick actions */}
                                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity md:opacity-100">
                                    <Button 
                                      size="sm" 
                                      variant="ghost" 
                                      onClick={() => handleShareEvent(event)}
                                      title="Поделиться"
                                    >
                                      <Share2 className="w-3.5 h-3.5" />
                                    </Button>
                                    <Button 
                                      size="sm" 
                                      variant="ghost" 
                                      onClick={() => handleExportEvent(event)}
                                      title="Добавить в календарь"
                                    >
                                      <CalendarPlus className="w-3.5 h-3.5" />
                                    </Button>
                                    <Button 
                                      size="sm" 
                                      variant="ghost" 
                                      onClick={() => handleOpenDetail(event)}
                                      title="Подробнее"
                                    >
                                      <ExternalLink className="w-3.5 h-3.5" />
                                    </Button>
                                  </div>
                                </div>
                              </CardContent>
                            </Card>
                          </motion.div>
                        ))}
                      </div>
                    </motion.div>
                  );
                })
              )}
            </div>
          </motion.section>
        </motion.div>
      </main>

      {/* Event Detail Modal */}
      <EventDetailModal 
        event={selectedEvent}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedEvent(null);
        }}
      />

      {/* Scroll to Top Button */}
      <AnimatePresence>
        {showScrollTop && (
          <motion.button
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: 20 }}
            transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            onClick={scrollToTop}
            className="fixed z-40 bottom-24 right-4 md:bottom-8 md:right-8 w-12 h-12 rounded-full bg-primary text-white shadow-lg hover:shadow-xl flex items-center justify-center transition-shadow duration-200"
            aria-label="Вернуться наверх"
          >
            <ChevronUp className="w-5 h-5" />
          </motion.button>
        )}
      </AnimatePresence>
    </div>
  );
};

export default EventsPage;