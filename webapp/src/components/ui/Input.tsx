import React from 'react';
import { cn } from '../../utils/cn';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  variant?: 'default' | 'sm' | 'lg';
  error?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, variant = 'default', error, icon, iconPosition = 'left', type, ...props }, ref) => {
    const baseClasses = 'input focus-ring';
    
    const variantClasses = {
      default: '',
      sm: 'input-sm',
      lg: 'input-lg',
    };
    
    const errorClasses = error ? 'border-error focus:ring-error' : '';
    
    const inputElement = (
      <input
        ref={ref}
        type={type}
        className={cn(
          baseClasses,
          variantClasses[variant],
          errorClasses,
          icon && iconPosition === 'left' && 'pl-10',
          icon && iconPosition === 'right' && 'pr-10',
          className
        )}
        {...props}
      />
    );

    if (icon) {
      return (
        <div className="relative">
          {iconPosition === 'left' && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted">
              {icon}
            </div>
          )}
          {inputElement}
          {iconPosition === 'right' && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 text-muted">
              {icon}
            </div>
          )}
        </div>
      );
    }

    return inputElement;
  }
);

Input.displayName = 'Input';

// Textarea variant
interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  variant?: 'default' | 'sm' | 'lg';
  error?: boolean;
  resize?: boolean;
}

export const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, variant = 'default', error, resize = true, ...props }, ref) => {
    const baseClasses = 'input focus-ring min-h-[80px]';
    
    const variantClasses = {
      default: '',
      sm: 'input-sm min-h-[60px]',
      lg: 'input-lg min-h-[100px]',
    };
    
    const errorClasses = error ? 'border-error focus:ring-error' : '';
    const resizeClasses = resize ? '' : 'resize-none';

    return (
      <textarea
        ref={ref}
        className={cn(
          baseClasses,
          variantClasses[variant],
          errorClasses,
          resizeClasses,
          className
        )}
        {...props}
      />
    );
  }
);

Textarea.displayName = 'Textarea';
