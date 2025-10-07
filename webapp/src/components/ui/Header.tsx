import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';
import { ThemeToggle } from './ThemeToggle';

interface HeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
  className?: string;
  theme?: 'light' | 'dark';
  onThemeToggle?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ 
  title, 
  subtitle, 
  actions, 
  className,
  theme,
  onThemeToggle
}) => {
  return (
    <motion.header 
      className={cn('nav-header', className)}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex flex-col space-y-1">
        <h1 className="text-xl font-semibold text-text">{title}</h1>
        {subtitle && (
          <p className="text-sm text-muted-strong">{subtitle}</p>
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

// Mobile Header variant
interface MobileHeaderProps extends HeaderProps {
  showBack?: boolean;
  onBack?: () => void;
}

export const MobileHeader: React.FC<MobileHeaderProps> = ({ 
  title, 
  subtitle, 
  actions, 
  showBack = false,
  onBack,
  className,
  theme,
  onThemeToggle
}) => {
  return (
    <motion.header 
      className={cn('nav-header safe-top', className)}
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
        
        <div className="flex flex-col space-y-1">
          <h1 className="text-lg font-semibold text-text">{title}</h1>
          {subtitle && (
            <p className="text-xs text-muted-strong">{subtitle}</p>
          )}
        </div>
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
