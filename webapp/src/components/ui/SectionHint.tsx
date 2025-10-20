import React from 'react';
import { cn } from '../../lib/utils';

interface SectionHintProps {
    icon: string;
    title: string;
    subtitle: string;
    className?: string;
}

export const SectionHint: React.FC<SectionHintProps> = ({
    icon,
    title,
    subtitle,
    className
}) => {
    return (
        <div className={cn(
            'text-center px-4 py-3',
            'space-y-1',
            className
        )}>
            <div className={cn(
                'flex items-center justify-center gap-2',
                'text-primary font-medium text-sm'
            )}>
                <span className="text-base">{icon}</span>
                <span>{title}</span>
            </div>
            <p className={cn(
                'text-xs text-muted leading-relaxed'
            )}>
                {subtitle}
            </p>
        </div>
    );
};
