import { motion } from 'framer-motion';
import React from 'react';
import { cn } from '../../lib/utils';

interface FilterOption {
    id: string;
    label: string;
}

interface FilterBarProps {
    type: 'category' | 'status' | 'time';
    options: FilterOption[];
    activeId: string;
    onChange: (id: string) => void;
    className?: string;
}

export const FilterBar: React.FC<FilterBarProps> = ({
    type: _type,
    options,
    activeId,
    onChange,
    className
}) => {
    return (
        <div className={cn('flex flex-wrap justify-center gap-2', className)}>
            {options.map((option) => (
                <motion.button
                    key={option.id}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => onChange(option.id)}
                    className={cn(
                        'chip transition-all duration-200 ease-out',
                        activeId === option.id
                            ? 'chip-active'
                            : 'chip-inactive'
                    )}
                >
                    {option.label}
                </motion.button>
            ))}
        </div>
    );
};
