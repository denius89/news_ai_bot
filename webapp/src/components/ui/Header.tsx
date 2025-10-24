import { motion } from 'framer-motion';
import React from 'react';
import { cn } from '../../utils/cn';
import { ThemeToggle } from './ThemeToggle';

interface HeaderProps {
    title: string;
    subtitle?: string;
    actions?: React.ReactNode;
    className?: string;
    theme?: 'light' | 'dark';
    onThemeToggle?: () => void;
    icon?: React.ReactNode;
    showBack?: boolean;
    onBack?: () => void;
}

export const Header: React.FC<HeaderProps> = ({
    title,
    subtitle,
    actions,
    className,
    theme,
    onThemeToggle,
    icon,
    showBack = false,
    onBack
}) => {
    // Компактный режим: subtitle inline если короткий
    const isCompactMode = subtitle && subtitle.length <= 40;

    return (
        <motion.header
            className={cn('nav-header py-2 sm:py-3', className)}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
        >
            <div className="flex items-center space-x-3">
                {showBack && (
                    <button
                        onClick={onBack}
                        className="p-2 -ml-2 text-muted hover:text-text transition-colors"
                        aria-label="Назад"
                    >
                        <svg
                            className="w-5 h-5"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M15 19l-7-7 7-7"
                            />
                        </svg>
                    </button>
                )}
                {icon && !showBack && (
                    <div className="flex-shrink-0 flex items-center justify-center h-8">
                        {icon}
                    </div>
                )}

                {isCompactMode ? (
                    // Компактный режим: title и subtitle в одну строку
                    <div className="flex items-center space-x-2">
                        <h1 className="text-lg sm:text-xl font-semibold text-text">{title}</h1>
                        <span className="text-xs sm:text-sm text-muted-foreground">•</span>
                        <p className="text-xs sm:text-sm text-muted-foreground">{subtitle}</p>
                    </div>
                ) : (
                    // Обычный режим: subtitle на отдельной строке
                    <div className="flex flex-col space-y-1">
                        <h1 className="text-lg sm:text-xl font-semibold text-text">{title}</h1>
                        {subtitle && (
                            <p className="text-xs sm:text-sm text-muted-strong">{subtitle}</p>
                        )}
                    </div>
                )}
            </div>

            <div className="flex items-center space-x-2">
                {theme && onThemeToggle && (
                    <ThemeToggle
                        theme={theme}
                        onToggle={onThemeToggle}
                        size="sm"
                    />
                )}
                {actions}
            </div>
        </motion.header>
    );
};

// For backwards compatibility
export const MobileHeader = Header;
