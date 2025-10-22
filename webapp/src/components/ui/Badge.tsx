/**
 * Badge component with PulseAI v2 design tokens
 * Supports semantic color variants
 */

interface BadgeProps {
    children: React.ReactNode;
    variant?: 'default' | 'success' | 'warning' | 'error' | 'info' | 'outline' | 'secondary' | 'destructive';
    className?: string;
}

export function Badge({ children, variant = 'default', className = '' }: BadgeProps) {
    const variants = {
        default: 'bg-primary/10 text-primary border border-primary/20',
        success: 'status-success',
        warning: 'status-warning',
        error: 'status-error',
        info: 'bg-primary/10 text-primary border border-primary/20',
        outline: 'border border-border bg-transparent text-text',
        // Legacy support
        secondary: 'bg-muted/10 text-muted border border-muted/20',
        destructive: 'status-error',
    };

    return (
        <span
            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold transition-colors ${variants[variant]} ${className}`}
        >
            {children}
        </span>
    );
}
