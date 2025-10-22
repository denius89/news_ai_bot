/**
 * Progress Bar component
 * Reusable progress indicator with automatic color based on percentage
 */

import { getProgressColor } from '../../utils/colors';

interface ProgressBarProps {
    value: number; // 0-100
    label?: string;
    showPercentage?: boolean;
    color?: 'auto' | 'primary' | 'success' | 'warning' | 'error';
    size?: 'sm' | 'md' | 'lg';
    className?: string;
}

const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-4',
};

const colorClasses = {
    auto: '', // Will be determined by percentage
    primary: 'bg-primary',
    success: 'bg-success',
    warning: 'bg-warning',
    error: 'bg-error',
};

export function ProgressBar({
    value,
    label,
    showPercentage = false,
    color = 'auto',
    size = 'md',
    className = '',
}: ProgressBarProps) {
    const percentage = Math.min(Math.max(value, 0), 100);
    const barColor = color === 'auto' ? getProgressColor(percentage) : colorClasses[color];

    return (
        <div className={`w-full ${className}`}>
            {(label || showPercentage) && (
                <div className="flex justify-between mb-2">
                    {label && <span className="text-sm text-muted">{label}</span>}
                    {showPercentage && (
                        <span className="text-sm font-medium">{percentage.toFixed(0)}%</span>
                    )}
                </div>
            )}
            <div className={`w-full bg-muted/30 rounded-full overflow-hidden ${sizeClasses[size]}`}>
                <div
                    className={`${barColor} ${sizeClasses[size]} rounded-full transition-all duration-300 ease-out`}
                    style={{ width: `${percentage}%` }}
                />
            </div>
        </div>
    );
}
