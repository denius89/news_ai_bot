import { motion, MotionProps } from 'framer-motion';
import React from 'react';
import { isMobileDevice } from '../utils/performance';

interface OptimizedMotionProps extends MotionProps {
    children: React.ReactNode;
    className?: string;
    disableOnMobile?: boolean;
    reduceMotion?: boolean;
}

export const OptimizedMotion: React.FC<OptimizedMotionProps> = ({
    children,
    className = '',
    disableOnMobile = true,
    reduceMotion = false,
    ...motionProps
}) => {
    const shouldDisableMotion =
        disableOnMobile && isMobileDevice() ||
        reduceMotion;

    if (shouldDisableMotion) {
        return <div className={className}>{children}</div>;
    }

    return (
        <motion.div
            className={className}
            {...motionProps}
            style={{
                // Оптимизация для GPU
                willChange: 'transform',
                backfaceVisibility: 'hidden',
                transform: 'translateZ(0)',
                ...motionProps.style
            }}
        >
            {children}
        </motion.div>
    );
};

/**
 * Компонент для оптимизированных hover эффектов
 */
interface OptimizedHoverProps {
    children: React.ReactNode;
    className?: string;
    hoverClassName?: string;
    disabled?: boolean;
}

export const OptimizedHover: React.FC<OptimizedHoverProps> = ({
    children,
    className = '',
    hoverClassName = '',
    disabled = false
}) => {
    const shouldDisableHover = disabled || isMobileDevice();

    if (shouldDisableHover) {
        return <div className={className}>{children}</div>;
    }

    return (
        <OptimizedMotion
            className={`${className} ${hoverClassName}`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
        >
            {children}
        </OptimizedMotion>
    );
};
