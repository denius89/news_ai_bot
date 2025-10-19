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
        // Core positioning and layout - AI Dock v4.1: Perfect Balance
        'fixed bottom-4 left-1/2 -translate-x-1/2 z-50',
        'flex justify-around items-center',
        'w-[92%] max-w-[580px] px-3 py-2 rounded-3xl',
        
        // Perfect Balance Glass effects
        'backdrop-blur-xl',
        'border-t border-white/40 dark:border-white/10',
        
        // Enhanced gradient backgrounds for natural depth
        'bg-[linear-gradient(180deg,rgba(255,255,255,0.75)_0%,rgba(245,248,250,0.6)_60%,rgba(230,235,240,0.55)_100%)]',
        'dark:bg-[linear-gradient(180deg,rgba(28,30,35,0.55)_0%,rgba(20,22,26,0.45)_80%,rgba(12,14,18,0.4)_100%)]',
        
        // Ambient shadow + inner light + soft edge
        'shadow-[0_10px_20px_rgba(0,0,0,0.08),inset_0_1px_0_rgba(255,255,255,0.3)]',
        'dark:shadow-[0_10px_20px_rgba(0,0,0,0.4),inset_0_1px_0_rgba(255,255,255,0.1)]',
        'filter drop-shadow-[0_8px_16px_rgba(0,0,0,0.08)]',
        'dark:filter dark:drop-shadow-[0_8px_16px_rgba(0,0,0,0.3)]',
        
        // Premium transitions and overflow
        'transition-all duration-300',
        'overflow-hidden relative',
        
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: [0.4, 0, 0.2, 1] }}
    >
      {/* Верхний блик - имитация отражения света в стекле */}
      <div className="absolute top-0 left-0 right-0 h-[35%] bg-white/35 dark:bg-white/10 blur-xl rounded-3xl pointer-events-none" />

      {/* Внутренний свет снизу - добавляет объём и глубину */}
      <div className="absolute bottom-0 left-0 right-0 h-[40%] bg-gradient-to-b from-transparent to-white/25 dark:to-white/10 opacity-40 rounded-3xl pointer-events-none" />

      {items.map((item) => (
        <motion.button
          key={item.id}
          onClick={item.onClick}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
          className={cn(
            'flex flex-col items-center justify-center text-[11px] font-medium',
            'transition-all duration-200 relative',
            'px-2 py-1 rounded-xl',
            item.active
              ? 'text-[var(--color-primary)] drop-shadow-[0_0_8px_rgba(0,191,166,0.35)]'
              : 'text-[rgba(30,41,59,0.65)] dark:text-[rgba(232,234,237,0.6)] hover:text-[var(--color-primary)]'
          )}
        >
          <div className={cn(
            'relative w-5 h-5 mb-[2px] opacity-90 transition-transform duration-200',
            item.active && 'scale-110 drop-shadow-[0_0_6px_rgba(0,191,166,0.25)]'
          )}>
            {item.icon}
            {item.badge && item.badge > 0 && (
              <span className="absolute -top-1 -right-1 bg-error text-white text-[10px] rounded-full min-w-[16px] h-4 flex items-center justify-center px-1">
                {item.badge > 99 ? '99+' : item.badge}
              </span>
            )}
          </div>
          <span>{item.label}</span>
          {/* Light Flow indicator for active state */}
          {item.active && (
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-8 h-[2px] bg-[var(--color-primary)]/60 rounded-full blur-[1px]" />
          )}
        </motion.button>
      ))}
    </motion.nav>
  );
};
