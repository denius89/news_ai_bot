import { ChevronLeft, ChevronRight } from 'lucide-react';
import React, { useCallback, useEffect, useRef, useState } from 'react';

interface Chip {
    id: string;
    label: string;
    icon?: string;
}

interface ChipsCarouselProps {
    chips: Chip[];
    selectedId: string;
    onSelect: (id: string) => void;
    label?: string;
}

export const ChipsCarousel: React.FC<ChipsCarouselProps> = ({
    chips,
    selectedId,
    onSelect,
    label
}) => {
    const scrollRef = useRef<HTMLDivElement>(null);
    const [showLeftArrow, setShowLeftArrow] = useState(false);
    const [showRightArrow, setShowRightArrow] = useState(true);

    // Проверка видимости стрелок
    const checkScroll = useCallback(() => {
        if (scrollRef.current) {
            const { scrollLeft, scrollWidth, clientWidth } = scrollRef.current;
            setShowLeftArrow(scrollLeft > 10);
            setShowRightArrow(scrollLeft < scrollWidth - clientWidth - 10);
        }
    }, []);

    useEffect(() => {
        checkScroll();
        const scrollElement = scrollRef.current;

        if (scrollElement) {
            scrollElement.addEventListener('scroll', checkScroll);
            window.addEventListener('resize', checkScroll);

            return () => {
                scrollElement.removeEventListener('scroll', checkScroll);
                window.removeEventListener('resize', checkScroll);
            };
        }
    }, [checkScroll, chips]);

    const scroll = (direction: 'left' | 'right') => {
        if (scrollRef.current) {
            const scrollAmount = 200;
            const newScrollLeft = scrollRef.current.scrollLeft +
                (direction === 'left' ? -scrollAmount : scrollAmount);

            scrollRef.current.scrollTo({
                left: newScrollLeft,
                behavior: 'smooth'
            });
        }
    };

    return (
        <div className="relative">
            {label && <p className="text-xs text-muted mb-2">{label}</p>}
            <div className="flex items-center gap-2">
                {showLeftArrow && (
                    <button
                        onClick={() => scroll('left')}
                        className="shrink-0 p-1 bg-surface rounded-full shadow-md hover:shadow-lg transition-shadow"
                        aria-label="Scroll left"
                    >
                        <ChevronLeft className="w-4 h-4 text-text" />
                    </button>
                )}
                <div
                    ref={scrollRef}
                    className="flex gap-2 overflow-x-auto news-chips-scrollbar-hide scroll-smooth"
                    style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
                >
                    {chips.map(chip => (
                        <button
                            key={chip.id}
                            onClick={() => onSelect(chip.id)}
                            className={`chip ${selectedId === chip.id
                                    ? 'chip-active'
                                    : 'chip-inactive'
                                }`}
                        >
                            {chip.icon && <span>{chip.icon}</span>}
                            {chip.label}
                        </button>
                    ))}
                </div>
                {showRightArrow && (
                    <button
                        onClick={() => scroll('right')}
                        className="shrink-0 p-1 bg-surface rounded-full shadow-md hover:shadow-lg transition-shadow"
                        aria-label="Scroll right"
                    >
                        <ChevronRight className="w-4 h-4 text-text" />
                    </button>
                )}
            </div>
        </div>
    );
};
