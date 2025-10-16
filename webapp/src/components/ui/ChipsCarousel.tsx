import React, { useRef, useState, useCallback, useEffect } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

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
      {label && <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">{label}</p>}
      <div className="flex items-center gap-2">
        {showLeftArrow && (
          <button 
            onClick={() => scroll('left')}
            className="shrink-0 p-1 bg-white dark:bg-surface-alt rounded-full shadow-md hover:shadow-lg transition-shadow"
            aria-label="Scroll left"
          >
            <ChevronLeft className="w-4 h-4 text-gray-600 dark:text-gray-300" />
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
              className={`shrink-0 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center gap-2 whitespace-nowrap ${
                selectedId === chip.id
                  ? 'bg-gradient-to-r from-[#00BFA6]/10 to-[#00E3BE]/10 text-primary shadow-[0_0_6px_rgba(0,191,166,0.2)]'
                  : 'border border-border text-gray-600 dark:text-gray-300 hover:text-primary hover:border-primary/50'
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
            className="shrink-0 p-1 bg-white dark:bg-surface-alt rounded-full shadow-md hover:shadow-lg transition-shadow"
            aria-label="Scroll right"
          >
            <ChevronRight className="w-4 h-4 text-gray-600 dark:text-gray-300" />
          </button>
        )}
      </div>
    </div>
  );
};

