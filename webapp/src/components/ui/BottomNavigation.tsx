import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  href?: string;
  onClick?: () => void;
  active?: boolean;
  badge?: number;
}

interface BottomNavigationProps {
  items: NavItem[];
  className?: string;
}

export const BottomNavigation: React.FC<BottomNavigationProps> = ({ 
  items, 
  className 
}) => {
  return (
    <motion.nav 
      className={cn('nav-bottom safe-bottom', className)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
    >
      {items.map((item, index) => (
        <motion.button
          key={item.id}
          className={cn(
            'nav-item relative',
            item.active && 'active'
          )}
          onClick={item.onClick}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          transition={{ duration: 0.1 }}
          style={{ animationDelay: `${index * 0.05}s` }}
        >
          <div className="relative">
            {item.icon}
            {item.badge && item.badge > 0 && (
              <motion.span 
                className="absolute -top-1 -right-1 bg-error text-white text-xs rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1"
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
              >
                {item.badge > 99 ? '99+' : item.badge}
              </motion.span>
            )}
          </div>
          <span className="text-xs mt-1 font-medium">{item.label}</span>
        </motion.button>
      ))}
    </motion.nav>
  );
};

// Desktop Navigation variant
interface DesktopNavigationProps {
  items: NavItem[];
  className?: string;
}

export const DesktopNavigation: React.FC<DesktopNavigationProps> = ({ 
  items, 
  className 
}) => {
  return (
    <motion.nav 
      className={cn('flex items-center space-x-1', className)}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      {items.map((item) => (
        <motion.button
          key={item.id}
          className={cn(
            'flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors',
            item.active 
              ? 'bg-primary text-white' 
              : 'text-muted hover:text-text hover:bg-surface-alt'
          )}
          onClick={item.onClick}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          transition={{ duration: 0.1 }}
        >
          {item.icon}
          <span>{item.label}</span>
          {item.badge && item.badge > 0 && (
            <span className="bg-error text-white text-xs rounded-full px-2 py-0.5">
              {item.badge > 99 ? '99+' : item.badge}
            </span>
          )}
        </motion.button>
      ))}
    </motion.nav>
  );
};
