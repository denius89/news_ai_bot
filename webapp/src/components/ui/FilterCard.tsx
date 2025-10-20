import React from 'react';
import { cn } from '../../lib/utils';

interface FilterCardProps {
    children: React.ReactNode;
    className?: string;
}

export const FilterCard: React.FC<FilterCardProps> = ({
    children,
    className
}) => {
    return (
        <div className={cn(
            'bg-white/70 dark:bg-gray-800/60 backdrop-blur-sm',
            'rounded-2xl px-4 py-6',
            'shadow-sm dark:shadow-md',
            'border border-white/20 dark:border-gray-700/30',
            'space-y-3',
            className
        )}>
            {children}
        </div>
    );
};
