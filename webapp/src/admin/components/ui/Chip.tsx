import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';
import React from 'react';

type ChipProps = {
    children: React.ReactNode;
    active?: boolean;
    onClick?: () => void;
    className?: string;
    size?: 'sm' | 'md';
    disabled?: boolean;
};

export function Chip({ children, active = false, onClick, className = '', size = 'md', disabled = false }: ChipProps) {
    const sizeClasses = size === 'sm' ? 'px-2.5 py-1 text-xs' : 'px-3.5 py-1.5 text-sm';
    const base = 'inline-flex items-center rounded-full border transition-colors select-none focus:outline-none focus:ring-2 focus:ring-primary/20 backdrop-blur-sm';
    const inactive = 'text-muted hover:text-text hover:bg-primary/10 border-border';
    const activeCls = 'bg-primary/15 text-primary border-primary/30 shadow-sm';

    return (
        <motion.button
            whileTap={{ scale: 0.98 }}
            type="button"
            role="switch"
            aria-pressed={active}
            disabled={disabled}
            onClick={onClick}
            className={cn(base, sizeClasses, active ? activeCls : inactive, disabled && 'opacity-60', className)}
        >
            {children}
        </motion.button>
    );
}
