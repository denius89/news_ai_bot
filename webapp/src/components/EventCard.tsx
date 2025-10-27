import { Calendar, ExternalLink, MapPin } from 'lucide-react';
import React from 'react';
import { OptimizedImage } from './OptimizedImage';

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
    imageUrl?: string;
}

interface EventCardProps {
    event: Event;
    onSelect: (event: Event) => void;
    getImportanceStars: (importance: number) => React.ReactNode;
    truncateText: (text: string, maxLength: number) => string;
}

export const EventCard = React.memo<EventCardProps>(({
    event,
    onSelect,
    getImportanceStars,
    truncateText
}) => {
    const formatDateTime = (dateString: string) => {
        const date = new Date(dateString);
        return {
            date: date.toLocaleDateString('ru-RU'),
            time: date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
        };
    };

    const startTime = formatDateTime(event.starts_at);
    const endTime = event.ends_at ? formatDateTime(event.ends_at) : null;

    return (
        <div className="card p-3 sm:p-4 transition-all duration-300 hover:scale-[1.01]">
            <div className="flex justify-between items-start mb-2">
                <h3 className="card-title text-text dark:text-white flex-1">
                    {truncateText(event.title, 80)}
                </h3>
                <span className="ml-2 card-badge bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
                    {Math.round(event.importance * 100)}%
                </span>
            </div>

            <div className="space-y-2 card-meta text-gray-600 dark:text-gray-400">
                <div className="flex items-center gap-2">
                    <Calendar className="card-icon-md" />
                    <span>
                        {startTime.date} в {startTime.time}
                        {endTime && ` - ${endTime.time}`}
                    </span>
                </div>

                {event.location && (
                    <div className="flex items-center gap-2">
                        <MapPin className="card-icon-md" />
                        <span>{truncateText(event.location, 60)}</span>
                    </div>
                )}

                {event.organizer && (
                    <div className="card-meta text-gray-500">
                        Организатор: {event.organizer}
                    </div>
                )}
            </div>

            {event.imageUrl && (
                <div className="mt-2">
                    <OptimizedImage
                        src={event.imageUrl}
                        alt={event.title}
                        width={300}
                        height={150}
                        className="w-full h-32 object-cover rounded-lg"
                        lazy={true}
                        quality={85}
                    />
                </div>
            )}

            {event.description && (
                <p className="mt-2 card-description text-text/90 line-clamp-2">
                    {truncateText(event.description, 150)}
                </p>
            )}

            <div className="mt-3 flex justify-between items-center">
                <div className="flex items-center gap-1">
                    {getImportanceStars(event.importance)}
                </div>
                <div className="flex items-center gap-2">
                    <span className="card-meta text-gray-500">{event.source}</span>
                    {event.link && (
                        <button
                            className="text-primary font-medium hover:underline flex items-center gap-1 card-footer"
                            onClick={() => onSelect(event)}
                        >
                            Подробнее
                            <ExternalLink className="card-icon-sm" />
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}, (prevProps, nextProps) => {
    // Ререндерить только если изменился event.id
    return prevProps.event.id === nextProps.event.id;
});

EventCard.displayName = 'EventCard';
