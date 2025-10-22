/**
 * Color utilities for admin panel
 * Provides consistent color mapping based on PulseAI v2 design tokens
 */

export type StatusType = 'running' | 'stopped' | 'error' | 'warning' | 'success' | 'info';

/**
 * Get text color class for status
 */
export const getStatusColor = (status: StatusType): string => {
  const colors: Record<StatusType, string> = {
    running: 'text-success',
    stopped: 'text-muted',
    error: 'text-error',
    warning: 'text-warning',
    success: 'text-success',
    info: 'text-primary',
  };
  return colors[status];
};

/**
 * Get background color class for status
 */
export const getStatusBgColor = (status: StatusType): string => {
  const colors: Record<StatusType, string> = {
    running: 'bg-success',
    stopped: 'bg-muted',
    error: 'bg-error',
    warning: 'bg-warning',
    success: 'bg-success',
    info: 'bg-primary',
  };
  return colors[status];
};

/**
 * Get border color class for status
 */
export const getStatusBorderColor = (status: StatusType): string => {
  const colors: Record<StatusType, string> = {
    running: 'border-success',
    stopped: 'border-muted',
    error: 'border-error',
    warning: 'border-warning',
    success: 'border-success',
    info: 'border-primary',
  };
  return colors[status];
};

/**
 * Get progress bar color based on percentage
 */
export const getProgressColor = (percent: number): string => {
  if (percent < 30) return 'bg-error';
  if (percent < 70) return 'bg-warning';
  return 'bg-success';
};

/**
 * Get badge variant based on status
 */
export const getBadgeVariant = (status: StatusType): 'default' | 'success' | 'warning' | 'error' => {
  const variants: Record<StatusType, 'default' | 'success' | 'warning' | 'error'> = {
    running: 'success',
    stopped: 'default',
    error: 'error',
    warning: 'warning',
    success: 'success',
    info: 'default',
  };
  return variants[status];
};

/**
 * Chart colors palette (PulseAI v2)
 */
export const CHART_COLORS = {
  primary: '#00A6C8',
  accent: '#7CFAD8',
  purple: '#8b5cf6',
  warning: '#f59e0b',
  success: '#16A34A',
  error: '#DC2626',
} as const;

/**
 * Chart colors array for multi-series charts
 */
export const CHART_COLORS_ARRAY = [
  CHART_COLORS.primary,
  CHART_COLORS.accent,
  CHART_COLORS.purple,
  CHART_COLORS.warning,
  CHART_COLORS.success,
  CHART_COLORS.error,
] as const;

