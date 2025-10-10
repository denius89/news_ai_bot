import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'outline';
  size?: 'sm' | 'default' | 'lg';
  fullWidth?: boolean;
  loading?: boolean;
  animate?: boolean;
  children: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant = 'primary', 
    size = 'default', 
    fullWidth = false,
    loading = false,
    animate = true,
    children, 
    disabled,
    ...props 
  }, ref) => {
    const baseClasses = 'btn interactive focus-ring';
    
    const variantClasses = {
      primary: 'btn-primary',
      secondary: 'btn-secondary',
      ghost: 'btn-ghost',
      outline: 'btn-secondary border-2',
    };
    
    const sizeClasses = {
      sm: 'btn-sm',
      default: '',
      lg: 'btn-lg',
    };
    
    const widthClasses = fullWidth ? 'btn-full' : '';
    const disabledClasses = (disabled || loading) ? 'opacity-50 cursor-not-allowed' : '';

    const Component = animate ? motion.button : 'button';
    const motionProps = animate ? {
      whileHover: { scale: disabled || loading ? 1 : 1.02 },
      whileTap: { scale: disabled || loading ? 1 : 0.98 },
      transition: { duration: 0.1 },
    } : {} as any;

    return (
      <Component
        ref={ref}
        className={cn(
          baseClasses,
          'transition-colors duration-300',
          variantClasses[variant],
          sizeClasses[size],
          widthClasses,
          disabledClasses,
          className
        )}
        disabled={disabled || loading}
        {...motionProps}
        {...props}
      >
        {loading && (
          <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        )}
        {children}
      </Component>
    );
  }
);

Button.displayName = 'Button';

// Icon Button variant
interface IconButtonProps extends Omit<ButtonProps, 'children'> {
  icon: React.ReactNode;
  'aria-label': string;
}

export const IconButton = React.forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, icon, 'aria-label': ariaLabel, ...props }, ref) => (
    <Button
      ref={ref}
      className={cn('p-2', className)}
      aria-label={ariaLabel}
      {...props}
    >
      {icon}
    </Button>
  )
);

IconButton.displayName = 'IconButton';
