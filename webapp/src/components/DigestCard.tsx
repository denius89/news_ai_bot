import { ExternalLink, ThumbsDown, ThumbsUp } from 'lucide-react';
import React from 'react';
import { cn } from '../utils/cn';
import { OptimizedImage } from './OptimizedImage';

interface DigestItem {
    id: string;
    title?: string;
    summary: string;
    category: string;
    sources?: string[];
    createdAt: string;
    readTime?: number;
    keyPoints?: string[];
    content?: string;
    style?: string;
    period?: string;
    limit?: number;
    preview?: string;
    user_id?: string;
    feedback_score?: number | null;
    imageUrl?: string;
    metadata?: {
        category: string;
        style: string;
        period: string;
        style_name: string;
        category_name: string;
    };
}

interface DigestCardProps {
    digest: DigestItem;
    onSelect: (digest: DigestItem) => void;
    onFeedback: (digestId: string, score: number) => void;
    categories: Record<string, string>;
    truncateText: (text: string, maxLength: number) => string;
}

export const DigestCard = React.memo<DigestCardProps>(({
    digest,
    onSelect,
    onFeedback,
    categories,
    truncateText
}) => {
    const handleFeedback = (score: number) => {
        onFeedback(digest.id, score);
    };

    return (
        <div className="card backdrop-blur-md border border-border rounded-3xl p-3 sm:p-4 pb-3 sm:pb-4 shadow-[0_6px_20px_rgba(0,0,0,0.05)] hover:scale-[1.02] transition-transform duration-300 ease-out">
            {/* Заголовок - извлекаем заголовок из HTML или используем первые слова */}
            <h3 className="card-title text-text">
                {(() => {
                    // Пытаемся извлечь заголовок из HTML (например, <h1>, <h2>, <b>)
                    const htmlText = digest.summary;
                    const titleMatch = htmlText.match(/<(h[1-6]|b|strong)>(.*?)<\/(h[1-6]|b|strong)>/i);
                    if (titleMatch && titleMatch[2]) {
                        return truncateText(titleMatch[2].replace(/<[^>]*>/g, ''), 80);
                    }
                    // Если нет HTML тегов, берем первые слова до точки
                    const firstSentence = htmlText.split('.')[0];
                    return truncateText(firstSentence.replace(/<[^>]*>/g, ''), 80);
                })()}
            </h3>

            {/* Бейджи в одну строку */}
            <div className="flex items-center gap-2 flex-wrap mt-2">
                <span className="inline-flex items-center px-2 py-0.5 rounded-md card-badge bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400">
                    {categories[digest.category] || digest.category}
                </span>

                {digest.metadata?.style_name && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-md card-badge bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400">
                        {digest.metadata.style_name}
                    </span>
                )}

                {digest.readTime && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-md card-badge bg-gray-50 dark:bg-gray-900/20 text-gray-600 dark:text-gray-400">
                        {digest.readTime} мин
                    </span>
                )}
            </div>

            {/* Краткое описание */}
            <p className="mt-3 card-description text-text/80 line-clamp-3">
                {truncateText(digest.summary.replace(/<[^>]*>/g, ''), 200)}
            </p>

            {/* Изображение дайджеста */}
            {digest.imageUrl && (
                <div className="mt-3">
                    <OptimizedImage
                        src={digest.imageUrl}
                        alt={digest.title || 'Digest image'}
                        width={300}
                        height={150}
                        className="w-full h-32 object-cover rounded-lg"
                        lazy={true}
                        quality={85}
                    />
                </div>
            )}

            {/* Источники */}
            {digest.sources && digest.sources.length > 0 && (
                <div className="mt-2 card-meta text-gray-500">
                    Источники: {digest.sources.slice(0, 3).join(', ')}
                    {digest.sources.length > 3 && ` +${digest.sources.length - 3}`}
                </div>
            )}

            {/* Действия */}
            <div className="mt-4 flex justify-between items-center">
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => onSelect(digest)}
                        className="text-primary font-medium hover:underline flex items-center gap-1 card-footer"
                    >
                        Подробнее
                        <ExternalLink className="card-icon-sm" />
                    </button>
                </div>

                {/* Feedback buttons */}
                <div className="flex items-center gap-1">
                    <button
                        onClick={() => handleFeedback(1)}
                        className={cn(
                            "p-1.5 rounded-full transition-colors",
                            digest.feedback_score === 1
                                ? "bg-green-100 text-green-600"
                                : "text-gray-400 hover:text-green-600 hover:bg-green-50"
                        )}
                        aria-label="Понравилось"
                    >
                        <ThumbsUp className="card-icon-md" />
                    </button>
                    <button
                        onClick={() => handleFeedback(0)}
                        className={cn(
                            "p-1.5 rounded-full transition-colors",
                            digest.feedback_score === 0
                                ? "bg-red-100 text-red-600"
                                : "text-gray-400 hover:text-red-600 hover:bg-red-50"
                        )}
                        aria-label="Не понравилось"
                    >
                        <ThumbsDown className="card-icon-md" />
                    </button>
                </div>
            </div>
        </div>
    );
}, (prevProps, nextProps) => {
    // Ререндерить только если изменился digest.id или feedback_score
    return prevProps.digest.id === nextProps.digest.id &&
        prevProps.digest.feedback_score === nextProps.digest.feedback_score;
});

DigestCard.displayName = 'DigestCard';
