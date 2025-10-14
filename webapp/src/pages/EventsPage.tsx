import React, { useState, useEffect } from 'react';
import { Calendar, ChevronDown } from 'lucide-react';
import { Card } from '../components/ui/Card';

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

interface CategoryInfo {
  name: string;
  emoji: string;
  color: string;
  subcategories: Record<string, { name: string; icon: string }>;
}

interface EventsPageProps {
  theme?: string;
  onThemeToggle?: () => void;
  onNavigate?: (page: string) => void;
}

const EventsPage: React.FC<EventsPageProps> = () => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters
  const [category, setCategory] = useState<string>('all');
  const [subcategory, setSubcategory] = useState<string>('all');
  const [dateRange, setDateRange] = useState<'today' | 'week' | 'month'>('week');
  const [categories, setCategories] = useState<Record<string, CategoryInfo>>({});

  // Fetch categories on mount
  useEffect(() => {
    fetchCategories();
  }, []);

  // Fetch events when filters change
  useEffect(() => {
    fetchEvents();
  }, [category, dateRange]);

  const fetchCategories = async () => {
    try {
      const response = await fetch('/api/events/categories');
      const data = await response.json();

      if (data.success) {
        setCategories(data.data);
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

      const response = await fetch(
        `/api/events/upcoming?days=${days}${categoryParam}`
      );
      const data = await response.json();

      if (data.success) {
        setEvents(data.data.events || []);
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

  const filteredEvents = subcategory === 'all' 
    ? events
    : events.filter(e => e.subcategory === subcategory);

  return (
    <div className="min-h-screen bg-[var(--color-bg)]">
      {/* Header */}
      <div className="sticky top-0 z-10 bg-[var(--color-bg)] border-b border-[var(--color-border)] px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Calendar className="w-6 h-6 text-primary" />
            <h1 className="text-xl font-bold text-[var(--color-text)]">Events</h1>
          </div>
          <button
            onClick={fetchEvents}
            className="text-sm text-primary hover:text-primary/80"
          >
            Refresh
          </button>
        </div>

        {/* Filters */}
        <div className="mt-3 space-y-2">
          {/* Date Range Filter */}
          <div className="flex space-x-2">
            {(['today', 'week', 'month'] as const).map((range) => (
              <button
                key={range}
                onClick={() => setDateRange(range)}
                className={`flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  dateRange === range
                    ? 'bg-primary text-white'
                    : 'bg-[var(--color-surface)] text-[var(--color-text)]-secondary hover:bg-[var(--color-surface)]-hover'
                }`}
              >
                {range === 'today' ? 'Today' : range === 'week' ? 'Week' : 'Month'}
              </button>
            ))}
          </div>

          {/* Category Filter */}
          <div className="flex overflow-x-auto space-x-2 pb-2 scrollbar-hide">
            <button
              onClick={() => {
                setCategory('all');
                setSubcategory('all');
              }}
              className={`px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                category === 'all'
                  ? 'bg-primary text-white'
                  : 'bg-[var(--color-surface)] text-[var(--color-text)]-secondary hover:bg-[var(--color-surface)]-hover'
              }`}
            >
              All
            </button>
            {Object.entries(categories).map(([key, cat]) => (
              <button
                key={key}
                onClick={() => {
                  setCategory(key);
                  setSubcategory('all');
                }}
                className={`px-3 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-colors ${
                  category === key
                    ? 'bg-primary text-white'
                    : 'bg-[var(--color-surface)] text-[var(--color-text)]-secondary hover:bg-[var(--color-surface)]-hover'
                }`}
              >
                {cat.emoji} {cat.name}
              </button>
            ))}
          </div>

          {/* Subcategory Filter (if category selected) */}
          {category !== 'all' && getSubcategories().length > 0 && (
            <div className="flex overflow-x-auto space-x-2 pb-2 scrollbar-hide">
              <button
                onClick={() => setSubcategory('all')}
                className={`px-2 py-1 rounded text-xs font-medium whitespace-nowrap ${
                  subcategory === 'all'
                    ? 'bg-primary/20 text-primary'
                    : 'bg-[var(--color-surface)] text-[var(--color-text)]-secondary hover:bg-[var(--color-surface)]-hover'
                }`}
              >
                All
              </button>
              {getSubcategories().map(([key, sub]) => (
                <button
                  key={key}
                  onClick={() => setSubcategory(key)}
                  className={`px-2 py-1 rounded text-xs font-medium whitespace-nowrap ${
                    subcategory === key
                      ? 'bg-primary/20 text-primary'
                      : 'bg-[var(--color-surface)] text-[var(--color-text)]-secondary hover:bg-[var(--color-surface)]-hover'
                  }`}
                >
                  {sub.icon} {sub.name}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-4 pb-20">
        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-2 text-[var(--color-text)]-secondary">Loading events...</p>
          </div>
        )}

        {error && (
          <Card className="p-4 bg-[var(--color-error)]/10 border-[var(--color-error)]">
            <p className="text-[var(--color-error)] text-center">{error}</p>
          </Card>
        )}

        {!loading && !error && filteredEvents.length === 0 && (
          <Card className="p-8">
            <div className="text-center">
              <Calendar className="w-12 h-12 mx-auto text-[var(--color-text)]-secondary/50" />
              <p className="mt-2 text-[var(--color-text)]-secondary">No events found</p>
            </div>
          </Card>
        )}

        {!loading && !error && filteredEvents.length > 0 && (
          <div className="space-y-3">
            {filteredEvents.map((event) => (
              <EventCard key={event.id} event={event} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const EventCard: React.FC<{ event: Event }> = ({ event }) => {
  const [expanded, setExpanded] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
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
      className={`cursor-pointer transition-all hover:shadow-md ${
        expanded ? 'shadow-lg' : ''
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
            className={`w-5 h-5 text-[var(--color-text)]-secondary transition-transform ${
              expanded ? 'rotate-180' : ''
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
                🔗 View Details
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

