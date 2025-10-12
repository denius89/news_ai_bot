import React, { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader } from '../ui/Card';
import { Button } from '../ui/Button';
import { CalendarDays, ChevronLeft, ChevronRight } from 'lucide-react';

interface Event {
  id: string;
  date: string;
  importance: number;
}

interface MiniCalendarWidgetProps {
  events: Event[];
  onDateSelect: (date: Date) => void;
  className?: string;
}

export const MiniCalendarWidget: React.FC<MiniCalendarWidgetProps> = ({ 
  events, 
  onDateSelect,
  className = ''
}) => {
  const [currentMonth, setCurrentMonth] = useState(new Date());
  
  // Group events by date for quick lookup
  const eventsByDate = useMemo(() => {
    const map = new Map<string, {count: number, maxImportance: number}>();
    events.forEach(e => {
      const dateKey = e.date;
      const existing = map.get(dateKey) || {count: 0, maxImportance: 0};
      map.set(dateKey, {
        count: existing.count + 1,
        maxImportance: Math.max(existing.maxImportance, e.importance || 0)
      });
    });
    return map;
  }, [events]);
  
  // Get days in month
  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startDayOfWeek = firstDay.getDay();
    
    const days: (Date | null)[] = [];
    
    // Add empty cells for days before month starts (Monday = 1, Sunday = 0 -> 6)
    const offset = startDayOfWeek === 0 ? 6 : startDayOfWeek - 1;
    for (let i = 0; i < offset; i++) {
      days.push(null);
    }
    
    // Add all days in month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };
  
  const days = getDaysInMonth(currentMonth);
  const monthName = currentMonth.toLocaleDateString('ru', { month: 'long', year: 'numeric' });
  
  // Check if date is today
  const isToday = (date: Date | null): boolean => {
    if (!date) return false;
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };
  
  // Navigate months
  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };
  
  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };
  
  const goToToday = () => {
    const today = new Date();
    setCurrentMonth(today);
    onDateSelect(today);
  };
  
  // Get importance color
  const getImportanceColor = (importance: number): string => {
    if (importance >= 0.8) return 'bg-red-500 dark:bg-red-600';
    if (importance >= 0.6) return 'bg-yellow-500 dark:bg-yellow-600';
    return 'bg-green-500 dark:bg-green-600';
  };
  
  return (
    <Card className={`${className}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-base capitalize text-gray-900 dark:text-white">{monthName}</h3>
          <div className="flex gap-1">
            <Button size="sm" variant="ghost" onClick={prevMonth} aria-label="Предыдущий месяц">
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <Button size="sm" variant="ghost" onClick={nextMonth} aria-label="Следующий месяц">
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-3">
        {/* Week days */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'].map(day => (
            <div key={day} className="text-xs text-center text-gray-500 dark:text-gray-400 py-1 font-medium">
              {day}
            </div>
          ))}
        </div>
        
        {/* Calendar grid */}
        <div className="grid grid-cols-7 gap-1">
          {days.map((date, i) => {
            const dateKey = date?.toISOString().split('T')[0];
            const eventsData = dateKey ? eventsByDate.get(dateKey) : null;
            const isTodayDate = isToday(date);
            
            return (
              <button
                key={i}
                onClick={() => date && onDateSelect(date)}
                disabled={!date}
                className={`
                  relative aspect-square rounded-lg text-sm transition-all
                  ${!date ? 'invisible' : ''}
                  ${isTodayDate 
                    ? 'bg-primary text-white font-bold shadow-sm ring-2 ring-primary/30' 
                    : eventsData 
                      ? 'bg-primary/5 dark:bg-primary/10 font-medium text-gray-800 dark:text-gray-200 hover:bg-primary/10 dark:hover:bg-primary/15' 
                      : 'text-gray-700 dark:text-gray-300 hover:bg-surface-alt'}
                  disabled:cursor-default
                `}
              >
                {date && (
                  <>
                    <span>{date.getDate()}</span>
                    {eventsData && (
                      <div className="absolute bottom-0.5 left-1/2 -translate-x-1/2 flex gap-0.5">
                        {eventsData.count > 1 ? (
                          [...Array(Math.min(eventsData.count, 3))].map((_, idx) => (
                            <div 
                              key={idx} 
                              className={`w-1 h-1 rounded-full ${getImportanceColor(eventsData.maxImportance)}`} 
                            />
                          ))
                        ) : (
                          <div 
                            className={`w-2 h-2 rounded-full ${getImportanceColor(eventsData.maxImportance)} ring-1 ring-white dark:ring-gray-800`}
                            title={`${eventsData.count} событий`}
                          />
                        )}
                      </div>
                    )}
                  </>
                )}
              </button>
            );
          })}
        </div>
        
        {/* Legend */}
        <div className="mt-3 pt-3 border-t border-border space-y-1.5 text-xs">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-red-500 dark:bg-red-600" />
              <span className="text-gray-600 dark:text-gray-400">Высокая важность</span>
            </div>
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
              {events.filter(e => e.importance >= 0.8).length}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-yellow-500 dark:bg-yellow-600" />
              <span className="text-gray-600 dark:text-gray-400">Средняя важность</span>
            </div>
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
              {events.filter(e => e.importance >= 0.6 && e.importance < 0.8).length}
            </span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500 dark:bg-green-600" />
              <span className="text-gray-600 dark:text-gray-400">Низкая важность</span>
            </div>
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400">
              {events.filter(e => e.importance < 0.6).length}
            </span>
          </div>
        </div>
        
        {/* Quick action */}
        <Button 
          size="sm" 
          variant="primary" 
          className="w-full mt-3"
          onClick={goToToday}
        >
          <CalendarDays className="w-4 h-4 mr-2" />
          Сегодня
        </Button>
      </CardContent>
    </Card>
  );
};
