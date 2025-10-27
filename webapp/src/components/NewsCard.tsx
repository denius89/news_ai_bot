import { ExternalLink } from 'lucide-react';
import React from 'react';
import { OptimizedImage } from './OptimizedImage';

interface NewsItem {
    id: string;
    title: string;
    content: string;
    source: string;
    category: string;
    subcategory?: string;
    publishedAt: string;
    credibility: number;
    importance: number;
    url?: string;
    imageUrl?: string;
}

interface NewsCardProps {
    item: NewsItem;
    onSelect: (item: NewsItem) => void;
    categories: Array<{ id: string; label: string; icon: string }>;
    getImportanceStars: (importance: number) => React.ReactNode;
    truncateText: (text: string, maxLength: number) => string;
}

export const NewsCard = React.memo<NewsCardProps>(({
    item,
    onSelect,
    categories,
    getImportanceStars,
    truncateText
}) => {
    return (
        <div
            className="card p-3 sm:p-4 transition-all duration-300 hover:scale-[1.01]"
        >
            <div>
                <div className="flex justify-between items-start">
                    <h3 className="card-title text-text dark:text-white">
                        {truncateText(item.title, 100)}
                    </h3>
                    <span className="ml-2 card-badge bg-green-50 text-green-600 px-2 py-0.5 rounded-full">
                        {Math.round(item.importance * 100)}%
                    </span>
                </div>

                <p className="card-meta text-gray-500 dark:text-gray-400 mt-1">
                    {item.url ? (
                        <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-primary hover:text-primary/80 underline"
                        >
                            {item.source}
                        </a>
                    ) : (
                        item.source
                    )} • {new Date(item.publishedAt).toLocaleDateString('ru-RU')}
                </p>

                {item.imageUrl && (
                    <div className="mt-2">
                        <OptimizedImage
                            src={item.imageUrl}
                            alt={item.title}
                            width={300}
                            height={200}
                            className="w-full h-48 object-cover rounded-lg"
                            lazy={true}
                            quality={85}
                        />
                    </div>
                )}

                <p className="mt-2 card-description text-text/90 line-clamp-3">
                    {truncateText(item.content, 200)}
                </p>

                <div className="mt-3 flex justify-between items-center card-footer">
                    <div className="flex items-center gap-1">
                        {getImportanceStars(item.importance)}
                    </div>
                    <span className="text-gray-500 dark:text-gray-400">
                        {categories.find(c => c.id === item.category)?.label}
                    </span>
                    <button
                        className="text-primary font-medium hover:underline flex items-center gap-1"
                        onClick={() => onSelect(item)}
                    >
                        Читать полностью
                        <ExternalLink className="card-icon-sm" />
                    </button>
                </div>
            </div>
        </div>
    );
}, (prevProps, nextProps) => {
    // Ререндерить только если изменился item.id
    return prevProps.item.id === nextProps.item.id;
});

NewsCard.displayName = 'NewsCard';
