import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  onClick?: () => void;
  active?: boolean;
  badge?: number;
}

interface BottomNavProps {
  items: NavItem[];
  className?: string;
}

export const BottomNav: React.FC<BottomNavProps> = ({ items, className }) => {
  return (
    <motion.nav
      className={cn(
        'navbar-glass',
        'bottom-6 z-50',
        'flex justify-around items-center',
        'w-[90%] max-w-[600px]',
        'px-3 py-2 rounded-2xl',
        'backdrop-blur-xl',
        'transition-all duration-300',
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {items.map((item) => (
        <motion.button
          key={item.id}
          onClick={item.onClick}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className={cn(
            'flex flex-col items-center justify-center text-xs font-medium transition-all',
            'px-2 py-1 rounded-xl',
            item.active
              ? 'text-primary bg-primary/20 shadow-[0_0_12px_rgba(0,166,200,0.3)] border border-primary/20'
              : 'text-muted hover:text-primary hover:bg-primary/5'
          )}
        >
          <div className="relative w-5 h-5 opacity-90">
            {item.icon}
            {item.badge && item.badge > 0 && (
              <span className="absolute -top-1 -right-1 bg-error text-white text-[10px] rounded-full min-w-[16px] h-4 flex items-center justify-center px-1">
                {item.badge > 99 ? '99+' : item.badge}
              </span>
            )}
          </div>
          <span className="mt-[2px]">{item.label}</span>
        </motion.button>
      ))}
    </motion.nav>
  );
};
