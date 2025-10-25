import { motion } from 'framer-motion';
import { ArrowUp, Calendar, ChevronDown, RefreshCw } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { Card } from '../components/ui/Card';
import { FilterBar } from '../components/ui/FilterBar';
import { FilterCard } from '../components/ui/FilterCard';
import { Header } from '../components/ui/Header';
import { apiUrl } from '../config/api';
import { useAuth } from '../context/AuthContext';
import { useTelegramUser } from '../hooks/useTelegramUser';
import { useTranslation } from '../i18n/useTranslation';
import { formatCount, PLURAL_FORMS } from '../utils/formatters';

interface Event {
    id: number;
    title: string;
    category: string;
    subcategory: string;
    starts_at: string;
    ends_at?: string;
    source: string;
    link?: string;
    importance: number;
    description?: string;
    location?: string;
    organizer?: string;
    metadata?: Record<string, any>;
    group_name?: string;
}

interface EventsPageProps {
    theme?: string;
    onThemeToggle?: () => void;
    onNavigate?: (page: string) => void;
}

interface CategoryData {
    name: string;
    emoji: string;
    color: string;
    subcategories: Record<string, { name: string; icon: string }>;
}

const EventsPage: React.FC<EventsPageProps> = () => {
    const [events, setEvents] = useState<Event[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Filters
    const [category, setCategory] = useState<string>('all');
    const [subcategory, setSubcategory] = useState<string>('all');
    const [dateRange, setDateRange] = useState<'today' | 'week' | 'month'>('week');
    const [categories, setCategories] = useState<Record<string, CategoryData>>({});
    const [isFilteredBySubscriptions, setIsFilteredBySubscriptions] = useState(false);
    const [showScrollTop, setShowScrollTop] = useState(false);

    // Pagination для infinite scroll
    const [displayedCount, setDisplayedCount] = useState(100); // Сколько событий показано
    const [loadingMore, setLoadingMore] = useState(false);

    // Get user data from authentication context
    const { userData } = useTelegramUser();
    const { authHeaders } = useAuth();
    const { getCategoryName } = useTranslation();
    const userId = userData?.user_id;

    // Fetch categories on mount
    useEffect(() => {
        fetchCategories();
    }, []);

    // Fetch events when filters change or userId becomes available
    useEffect(() => {
        if (userId !== undefined) {
            fetchEvents();
        }
    }, [category, dateRange, userId]);

    // Сбрасываем displayedCount при смене подкатегории
    useEffect(() => {
        setDisplayedCount(100);
    }, [subcategory]);

    // Scroll detection for "scroll to top" button
    useEffect(() => {
        const handleScroll = () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            setShowScrollTop(scrollTop > 300);
        };

        let timeoutId: NodeJS.Timeout;
        const throttledHandleScroll = () => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(handleScroll, 300);
        };

        window.addEventListener('scroll', throttledHandleScroll, { passive: true });
        return () => {
            window.removeEventListener('scroll', throttledHandleScroll);
            clearTimeout(timeoutId);
        };
    }, []);

    // Scroll to top function
    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const fetchCategories = async () => {
        try {
            const response = await fetch(apiUrl('/api/events/categories'));
            const data = await response.json();

            if (data.success) {
                // Переводим категории на русский язык
                const translatedCategories: Record<string, CategoryData> = {};

                Object.entries(data.data).forEach(([key, catData]: [string, any]) => {
                    translatedCategories[key] = {
                        name: getCategoryName(key),
                        emoji: catData.emoji || '📁',
                        color: catData.color || '#666',
                        subcategories: catData.subcategories || {}
                    };
                });

                setCategories(translatedCategories);
            }
        } catch (err) {
            console.error('Error fetching categories:', err);
        }
    };

    const fetchEvents = async () => {
        setLoading(true);
        setError(null);

        try {
            const days = dateRange === 'today' ? 1 : dateRange === 'week' ? 7 : 30;
            const categoryParam = category !== 'all' ? `&category=${category}` : '';

            // Build API URL with filtering
            let apiPath = `/api/events/upcoming?days=${days}${categoryParam}`;

            if (userId) {
                apiPath += `&filter_by_subscriptions=true`;
            }

            const response = await fetch(apiUrl(apiPath), {
                headers: authHeaders
            });
            const data = await response.json();

            if (data.success) {
                const allEvents = data.data.events || [];

                // Сохраняем ВСЕ события, но отображаем постепенно
                setEvents(allEvents);
                setDisplayedCount(100); // Показываем первые 100
                setIsFilteredBySubscriptions(data.data.filtered_by_subscriptions || false);

                console.log(`📊 Загружено событий: ${allEvents.length}, показано: 100`);
            } else {
                setError(data.error || 'Failed to fetch events');
            }
        } catch (err) {
            setError('Network error occurred');
            console.error('Error fetching events:', err);
        } finally {
            setLoading(false);
        }
    };

    const getSubcategories = () => {
        if (category === 'all' || !categories[category]) {
            return [];
        }
        return Object.entries(categories[category].subcategories);
    };

    // Фильтрация + пагинация для infinite scroll
    const allFilteredEvents = subcategory === 'all'
        ? events
        : events.filter(e => e.subcategory === subcategory);

    // Показываем только первые displayedCount событий
    const filteredEvents = allFilteredEvents.slice(0, displayedCount);

    // Load more events function для infinite scroll
    const loadMoreEvents = () => {
        if (loadingMore || displayedCount >= allFilteredEvents.length) {
            return;
        }

        setLoadingMore(true);

        // Имитируем задержку для плавности
        setTimeout(() => {
            const newCount = Math.min(displayedCount + 50, allFilteredEvents.length);
            setDisplayedCount(newCount);
            setLoadingMore(false);

            console.log(`📊 Показано событий: ${newCount} из ${allFilteredEvents.length}`);
        }, 300);
    };

    // Infinite scroll для событий
    React.useEffect(() => {
        const handleScroll = () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const scrollHeight = document.documentElement.scrollHeight;
            const clientHeight = window.innerHeight;

            const isNearBottom = scrollTop + clientHeight >= scrollHeight - 200;

            if (isNearBottom && !loadingMore && displayedCount < allFilteredEvents.length) {
                console.log('🔄 Загружаем ещё события...');
                loadMoreEvents();
            }
        };

        let timeoutId: NodeJS.Timeout;
        const throttledHandleScroll = () => {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(handleScroll, 300);
        };

        window.addEventListener('scroll', throttledHandleScroll, { passive: true });
        return () => {
            window.removeEventListener('scroll', throttledHandleScroll);
            clearTimeout(timeoutId);
        };
    }, [loadingMore, displayedCount, allFilteredEvents.length]);

    // Группировка событий по group_name и дате
    const { groupedEvents, standaloneEvents } = React.useMemo(() => {
        const groups: Record<string, Event[]> = {};
        const standalone: Event[] = [];

        filteredEvents.forEach(event => {
            // Группируем только если есть group_name и это спорт или крипто
            if (event.group_name && (event.category === 'sports' || event.category === 'crypto')) {
                const date = new Date(event.starts_at).toDateString();
                const key = `${event.group_name}|${date}`;

                if (!groups[key]) {
                    groups[key] = [];
                }
                groups[key].push(event);
            } else {
                standalone.push(event);
            }
        });

        // Разбиваем группы: если <3 событий - в standalone
        const finalGroups: Record<string, Event[]> = {};
        Object.entries(groups).forEach(([key, evts]) => {
            if (evts.length >= 3) {
                finalGroups[key] = evts;
            } else {
                standalone.push(...evts);
            }
        });

        return { groupedEvents: finalGroups, standaloneEvents: standalone };
    }, [filteredEvents]);

    return (
        <div className="min-h-screen bg-bg">
            <Header
                title="События"
                subtitle={isFilteredBySubscriptions ? "Ближайшие события" : formatCount(filteredEvents.length, PLURAL_FORMS.EVENTS)}
                icon={<Calendar className="w-6 h-6 text-primary" />}
                actions={
                    <motion.button
                        onClick={fetchEvents}
                        className="p-2 rounded-lg hover:bg-surface-alt transition-colors"
                        title="Обновить"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95, rotate: 180 }}
                        transition={{ duration: 0.2 }}
                    >
                        <RefreshCw className="w-5 h-5 text-primary hover:text-primary/80" />
                    </motion.button>
                }
            />

            {/* Filters */}
            <FilterCard className="mx-4 mb-3 p-3">
                {/* Date Range Filter */}
                <div>
                    <FilterBar
                        type="time"
                        options={[
                            { id: 'today', label: 'Сегодня' },
                            { id: 'week', label: 'Неделя' },
                            { id: 'month', label: 'Месяц' }
                        ]}
                        activeId={dateRange}
                        onChange={(id) => setDateRange(id as 'today' | 'week' | 'month')}
                    />
                </div>

                {/* Category Filter */}
                <div>
                    <FilterBar
                        type="category"
                        options={[
                            { id: 'all', label: 'Все' },
                            ...Object.entries(categories).map(([key, cat]) => ({ id: key, label: cat.name }))
                        ]}
                        activeId={category}
                        onChange={(id) => {
                            setCategory(id);
                            setSubcategory('all');
                        }}
                    />
                </div>

                {/* Subcategory Filter (if category selected) */}
                {category !== 'all' && getSubcategories().length > 0 && (
                    <>
                        {/* Разделитель */}
                        <div className="flex items-center my-3">
                            <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700"></div>
                            <span className="px-3 text-xs text-muted-foreground font-medium">Подкатегории</span>
                            <div className="flex-1 h-px bg-gray-200 dark:bg-gray-700"></div>
                        </div>

                        <div>
                            <FilterBar
                                type="category"
                                options={[
                                    { id: 'all', label: 'Все' },
                                    ...getSubcategories().map(([key, sub]) => ({ id: key, label: sub.name }))
                                ]}
                                activeId={subcategory}
                                onChange={setSubcategory}
                            />
                        </div>
                    </>
                )}
            </FilterCard>

            {/* Content */}
            <main className="container-main pb-24">
                {loading && (
                    <div className="text-center py-8">
                        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                        <p className="mt-2 text-[var(--color-text)]-secondary">Загружаем события...</p>
                    </div>
                )}

                {error && (
                    <Card className="p-4 bg-[var(--color-error)]/10 border-[var(--color-error)]">
                        <p className="text-[var(--color-error)] text-center">{error}</p>
                    </Card>
                )}

                {!loading && !error && filteredEvents.length === 0 && (
                    <Card className="p-6">
                        <div className="text-center">
                            <Calendar className="w-10 h-10 mx-auto text-[var(--color-text)]-secondary/50" />
                            <p className="mt-2 text-[var(--color-text)]-secondary">Нет новых событий</p>
                        </div>
                    </Card>
                )}

                {!loading && !error && (filteredEvents.length > 0 || Object.keys(groupedEvents).length > 0) && (
                    <>
                        <div className="space-y-3">
                            {/* Группы событий */}
                            {Object.entries(groupedEvents).map(([key, evts]) => (
                                <GroupedEventCard key={key} events={evts} groupKey={key} />
                            ))}

                            {/* Отдельные события */}
                            {standaloneEvents.map((event) => (
                                <EventCard key={event.id} event={event} />
                            ))}
                        </div>

                        {/* Индикатор загрузки при infinite scroll */}
                        {loadingMore && (
                            <div className="mt-4 text-center py-4">
                                <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
                                <p className="mt-2 text-sm text-[var(--color-text)]-secondary">Загружаем ещё...</p>
                            </div>
                        )}

                        {/* Индикатор прогресса */}
                        {!loadingMore && displayedCount < allFilteredEvents.length && (
                            <div className="mt-4 text-center py-4">
                                <p className="text-sm text-[var(--color-text)]-secondary">
                                    📊 Показано {displayedCount} из {allFilteredEvents.length} событий
                                </p>
                                <p className="text-xs text-primary mt-1">
                                    Пролистай вниз
                                </p>
                            </div>
                        )}

                        {/* Индикатор окончания */}
                        {displayedCount >= allFilteredEvents.length && allFilteredEvents.length > 0 && (
                            <div className="mt-4 text-center py-4">
                                <p className="text-sm text-[var(--color-text)]-secondary">
                                    ✅ Все события загружены ({allFilteredEvents.length})
                                </p>
                            </div>
                        )}
                    </>
                )}
            </main>

            {/* Scroll to Top Button */}
            {showScrollTop && (
                <motion.button
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.8 }}
                    onClick={scrollToTop}
                    className="fixed bottom-20 right-4 z-40
                     bg-primary hover:bg-primary/90
                     text-white
                     rounded-full p-3
                     shadow-lg hover:shadow-xl
                     transition-all duration-300"
                    aria-label="Вернуться наверх"
                >
                    <ArrowUp className="w-6 h-6" />
                </motion.button>
            )}
        </div>
    );
};

// Компонент для группы событий (например, матчи одной лиги в один день)
const GroupedEventCard: React.FC<{ events: Event[]; groupKey: string }> = ({ events, groupKey }) => {
    const [expanded, setExpanded] = useState(false);

    if (events.length === 0) return null;

    const [groupName, dateStr] = groupKey.split('|');
    const firstEvent = events[0];

    // Защита от Invalid Date
    let date: Date;
    try {
        date = dateStr ? new Date(dateStr) : new Date(firstEvent.starts_at);
        if (isNaN(date.getTime())) {
            date = new Date(firstEvent.starts_at);
        }
    } catch {
        date = new Date(firstEvent.starts_at);
    }

    const getCategoryIcon = () => {
        const icons: Record<string, string> = {
            sports: '🏆',
            crypto: '🪙',
            tech: '💻',
            markets: '📈',
            world: '🌍'
        };
        return icons[firstEvent.category] || '📅';
    };

    const formatGroupDate = () => {
        try {
            const now = new Date();
            const tomorrow = new Date(now);
            tomorrow.setDate(tomorrow.getDate() + 1);

            if (date.toDateString() === now.toDateString()) return 'Today';
            if (date.toDateString() === tomorrow.toDateString()) return 'Tomorrow';

            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        } catch {
            return 'Unknown';
        }
    };

    return (
        <Card
            className={`cursor-pointer transition-all hover:shadow-md ${expanded ? 'shadow-lg' : ''
                }`}
            onClick={() => setExpanded(!expanded)}
        >
            <div className="p-4">
                <div className="flex items-start justify-between">
                    <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                            <span className="text-xl">{getCategoryIcon()}</span>
                            <span className="px-2 py-0.5 rounded text-xs font-medium bg-primary/20 text-primary border border-primary/20">
                                {events.length} событий
                            </span>
                        </div>

                        <h3 className="font-semibold text-[var(--color-text)] mb-1">{groupName}</h3>

                        <p className="text-sm text-[var(--color-text)]-secondary">
                            {formatGroupDate()} • {firstEvent.subcategory}
                        </p>
                    </div>

                    <ChevronDown
                        className={`w-5 h-5 text-[var(--color-text)]-secondary transition-transform ${expanded ? 'rotate-180' : ''
                            }`}
                    />
                </div>

                {/* Список событий в группе */}
                {expanded && (
                    <div className="mt-4 pt-4 border-t border-[var(--color-border)] space-y-2">
                        {events.map((event, idx) => (
                            <div
                                key={event.id}
                                className={`py-2 ${idx > 0 ? 'border-t border-[var(--color-border)]/50' : ''}`}
                            >
                                <div className="flex items-start justify-between">
                                    <div className="flex-1">
                                        <h4 className="text-sm font-medium text-[var(--color-text)]">{event.title}</h4>
                                        <p className="text-xs text-[var(--color-text)]-secondary mt-0.5">
                                            {new Date(event.starts_at).toLocaleTimeString('en-US', {
                                                hour: '2-digit',
                                                minute: '2-digit',
                                                hour12: false
                                            })}
                                            {event.location && ` • ${event.location}`}
                                        </p>
                                    </div>
                                    {event.link && (
                                        <a
                                            href={event.link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            onClick={(e) => e.stopPropagation()}
                                            className="text-primary hover:text-primary/80 text-xs ml-2"
                                        >
                                            🔗
                                        </a>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </Card>
    );
};

const EventCard: React.FC<{ event: Event }> = ({ event }) => {
    const [expanded, setExpanded] = useState(false);

    const formatDate = (dateString: string) => {
        try {
            const date = new Date(dateString);
            if (isNaN(date.getTime())) {
                return 'Unknown date';
            }

            const now = new Date();
            const tomorrow = new Date(now);
            tomorrow.setDate(tomorrow.getDate() + 1);

            const isToday = date.toDateString() === now.toDateString();
            const isTomorrow = date.toDateString() === tomorrow.toDateString();

            const time = date.toLocaleTimeString('en-US', {
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });

            if (isToday) return `Today at ${time}`;
            if (isTomorrow) return `Tomorrow at ${time}`;

            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false
            });
        } catch {
            return 'Unknown date';
        }
    };

    const getCategoryIcon = () => {
        const icons: Record<string, string> = {
            sports: '🏆',
            crypto: '🪙',
            tech: '💻',
            markets: '📈',
            world: '🌍'
        };
        return icons[event.category] || '📅';
    };

    const getImportanceColor = () => {
        if (event.importance >= 0.8) return 'bg-[var(--color-error)]/20 text-[var(--color-error)] border-[var(--color-error)]/30';
        if (event.importance >= 0.6) return 'bg-[var(--color-warning)]/20 text-[var(--color-warning)] border-[var(--color-warning)]/30';
        return 'bg-primary/10 text-primary border-primary/20';
    };

    return (
        <Card
            className={`cursor-pointer transition-all hover:shadow-md ${expanded ? 'shadow-lg' : ''
                }`}
            onClick={() => setExpanded(!expanded)}
        >
            <div className="p-4">
                <div className="flex items-start justify-between">
                    <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                            <span className="text-lg">{getCategoryIcon()}</span>
                            <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getImportanceColor()}`}>
                                {event.subcategory}
                            </span>
                        </div>

                        <h3 className="font-semibold text-[var(--color-text)] mb-1">{event.title}</h3>

                        <p className="text-sm text-[var(--color-text)]-secondary">
                            {formatDate(event.starts_at)}
                        </p>

                        {event.location && (
                            <p className="text-xs text-[var(--color-text)]-secondary mt-1">
                                📍 {event.location}
                            </p>
                        )}
                    </div>

                    <ChevronDown
                        className={`w-5 h-5 text-[var(--color-text)]-secondary transition-transform ${expanded ? 'rotate-180' : ''
                            }`}
                    />
                </div>

                {/* Expanded Details */}
                {expanded && (
                    <div className="mt-4 pt-4 border-t border-[var(--color-border)] space-y-2">
                        {event.description && (
                            <p className="text-sm text-[var(--color-text)]-secondary">{event.description}</p>
                        )}

                        {/* Category-specific metadata */}
                        {event.metadata && Object.keys(event.metadata).length > 0 && (
                            <div className="mt-3 space-y-1">
                                <EventMetadata event={event} />
                            </div>
                        )}

                        {event.link && (
                            <a
                                href={event.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                onClick={(e) => e.stopPropagation()}
                                className="inline-block mt-3 text-sm text-primary hover:underline"
                            >
                                🔗 Подробнее
                            </a>
                        )}
                    </div>
                )}
            </div>
        </Card>
    );
};

const EventMetadata: React.FC<{ event: Event }> = ({ event }) => {
    const { category, subcategory, metadata } = event;

    if (!metadata) return null;

    // Sports/Esports
    if (category === 'sports') {
        const esportsCategories = ['dota2', 'csgo', 'lol', 'valorant', 'pubg', 'overwatch'];

        if (esportsCategories.includes(subcategory)) {
            return (
                <>
                    {metadata.team1 && metadata.team2 && (
                        <p className="text-sm">
                            <span className="font-medium">🎮 Match:</span> {metadata.team1} vs {metadata.team2}
                        </p>
                    )}
                    {metadata.tournament && (
                        <p className="text-sm">
                            <span className="font-medium">🏆 Tournament:</span> {metadata.tournament}
                        </p>
                    )}
                    {metadata.format && (
                        <p className="text-sm">
                            <span className="font-medium">⚔️ Format:</span> {metadata.format}
                        </p>
                    )}
                </>
            );
        }

        // Traditional sports
        return (
            <>
                {metadata.home_team && metadata.away_team && (
                    <p className="text-sm">
                        <span className="font-medium">⚽ Match:</span> {metadata.home_team} vs {metadata.away_team}
                    </p>
                )}
                {metadata.competition && (
                    <p className="text-sm">
                        <span className="font-medium">🏆 Competition:</span> {metadata.competition}
                    </p>
                )}
                {metadata.matchday && (
                    <p className="text-sm">
                        <span className="font-medium">📅 Matchday:</span> {metadata.matchday}
                    </p>
                )}
            </>
        );
    }

    // Crypto
    if (category === 'crypto') {
        return (
            <>
                {metadata.coins && metadata.coins.length > 0 && (
                    <p className="text-sm">
                        <span className="font-medium">💰 Coins:</span> {metadata.coins.slice(0, 3).join(', ')}
                    </p>
                )}
                {metadata.vote_count && (
                    <p className="text-sm">
                        <span className="font-medium">👥 Votes:</span> {metadata.vote_count.toLocaleString()}
                    </p>
                )}
                {metadata.categories && metadata.categories.length > 0 && (
                    <p className="text-sm">
                        <span className="font-medium">🏷️ Categories:</span> {metadata.categories.slice(0, 3).join(', ')}
                    </p>
                )}
            </>
        );
    }

    // Markets
    if (category === 'markets') {
        return (
            <>
                {metadata.fact && metadata.fact !== '—' && (
                    <p className="text-sm">
                        <span className="font-medium">📊 Fact:</span> {metadata.fact}
                    </p>
                )}
                {metadata.forecast && metadata.forecast !== '—' && (
                    <p className="text-sm">
                        <span className="font-medium">📈 Forecast:</span> {metadata.forecast}
                    </p>
                )}
                {metadata.previous && metadata.previous !== '—' && (
                    <p className="text-sm">
                        <span className="font-medium">📉 Previous:</span> {metadata.previous}
                    </p>
                )}
            </>
        );
    }

    // Tech
    if (category === 'tech') {
        return (
            <>
                {metadata.version && (
                    <p className="text-sm">
                        <span className="font-medium">📦 Version:</span> {metadata.version}
                    </p>
                )}
                {metadata.project && (
                    <p className="text-sm">
                        <span className="font-medium">💻 Project:</span> {metadata.project}
                    </p>
                )}
            </>
        );
    }

    return null;
};

export default EventsPage;
