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
        // Core positioning and layout
        'fixed bottom-6 z-50',
        'left-1/2 -translate-x-1/2',
        'flex justify-around items-center',
        'w-[92%] max-w-[600px]',
        'px-3 py-2 rounded-2xl',
        
        // AI Glass Dock v3 styling
        'bg-[linear-gradient(135deg,rgba(255,255,255,0.75),rgba(240,245,250,0.65))]',
        'dark:bg-[linear-gradient(135deg,rgba(22,25,30,0.55),rgba(12,14,18,0.55))]',
        'border border-white/20 dark:border-white/10',
        
        // Enhanced shadows and effects
        'shadow-[0_4px_22px_rgba(0,0,0,0.08),inset_0_0_0.5px_rgba(255,255,255,0.3)]',
        'dark:shadow-[0_4px_22px_rgba(0,0,0,0.5),inset_0_0_0.5px_rgba(255,255,255,0.1)]',
        
        // Backdrop and transitions
        'backdrop-blur-xl',
        'transition-all duration-300',
        'overflow-hidden',
        
        className
      )}
      style={{
        left: '50%',
        transform: 'translateX(-50%)'
      }}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
    >
      {/* AI Depth Balance Layer */}
      <div
        className="
          absolute inset-0 pointer-events-none z-[-1]
          bg-[linear-gradient(to_top,rgba(0,0,0,0.05),rgba(255,255,255,0))]
          dark:bg-[linear-gradient(to_top,rgba(0,0,0,0.25),rgba(255,255,255,0))]
          rounded-2xl
        "
      />

      {items.map((item) => (
        <motion.button
          key={item.id}
          onClick={item.onClick}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
          className={cn(
            'flex flex-col items-center justify-center text-[11px] font-medium',
            'transition-all duration-200',
            'px-2 py-1 rounded-xl',
            item.active
              ? 'text-primary drop-shadow-[0_0_6px_rgba(0,191,166,0.35)]'
              : 'text-[rgba(30,41,59,0.65)] dark:text-[rgba(232,234,237,0.6)] hover:text-primary'
          )}
        >
          <div className="relative w-5 h-5 mb-[2px] opacity-90">
            {item.icon}
            {item.badge && item.badge > 0 && (
              <span className="absolute -top-1 -right-1 bg-error text-white text-[10px] rounded-full min-w-[16px] h-4 flex items-center justify-center px-1">
                {item.badge > 99 ? '99+' : item.badge}
              </span>
            )}
          </div>
          <span>{item.label}</span>
        </motion.button>
      ))}
    </motion.nav>
  );
};
