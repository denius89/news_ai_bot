import { LucideIcon } from 'lucide-react';
import React from 'react';

interface OptimizedIconProps {
    icon: LucideIcon;
    size?: number;
    className?: string;
    color?: string;
    strokeWidth?: number;
}

export const OptimizedIcon: React.FC<OptimizedIconProps> = ({
    icon: Icon,
    size = 24,
    className = '',
    color,
    strokeWidth = 2
}) => {
    return (
        <Icon
            size={size}
            className={className}
            color={color}
            strokeWidth={strokeWidth}
            style={{
                // Оптимизация для рендеринга
                willChange: 'transform',
                backfaceVisibility: 'hidden',
                transform: 'translateZ(0)'
            }}
        />
    );
};

/**
 * Компонент для кэшированных иконок
 */
interface CachedIconProps extends OptimizedIconProps {
    cacheKey?: string;
}

export const CachedIcon: React.FC<CachedIconProps> = ({
    icon,
    cacheKey,
    ...props
}) => {
    // В будущем можно добавить кэширование SVG
    return <OptimizedIcon icon={icon} {...props} />;
};
