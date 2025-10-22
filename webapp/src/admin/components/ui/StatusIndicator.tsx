/**
 * Status Indicator component
 * Shows visual status with icon, color, and optional label
 */

import { getStatusBgColor, getStatusColor, type StatusType } from '../../utils/colors';

interface StatusIndicatorProps {
    status: StatusType;
    label?: string;
    showDot?: boolean;
    size?: 'sm' | 'md' | 'lg';
}

const sizeClasses = {
    sm: {
        text: 'text-xs',
        dot: 'h-1.5 w-1.5',
    },
    md: {
        text: 'text-sm',
        dot: 'h-2 w-2',
    },
    lg: {
        text: 'text-base',
        dot: 'h-2.5 w-2.5',
    },
};

const statusIcons = {
    running: '🟢',
    stopped: '⚪',
    error: '🔴',
    warning: '🟡',
    success: '✅',
    info: 'ℹ️',
};

export function StatusIndicator({
    status,
    label,
    showDot = true,
    size = 'md'
}: StatusIndicatorProps) {
    const colorClass = getStatusColor(status);
    const bgClass = getStatusBgColor(status);
    const { text: textClass, dot: dotClass } = sizeClasses[size];

    return (
        <div className="flex items-center gap-2">
            {showDot && (
                <span className={`${dotClass} rounded-full ${bgClass}`} />
            )}
            <span className={`font-medium ${colorClass} ${textClass}`}>
                {statusIcons[status]} {status.charAt(0).toUpperCase() + status.slice(1)}
            </span>
            {label && (
                <span className="text-muted text-xs">
                    {label}
                </span>
            )}
        </div>
    );
}
