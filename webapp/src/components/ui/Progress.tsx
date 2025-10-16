/**
 * Simple Progress bar component
 */

interface ProgressProps {
  value: number;
  className?: string;
}

export function Progress({ value, className = '' }: ProgressProps) {
  const clampedValue = Math.min(Math.max(value, 0), 100);
  
  return (
    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
      <div
        className={`h-full transition-all duration-300 ${className || 'bg-blue-500'}`}
        style={{ width: `${clampedValue}%` }}
      />
    </div>
  );
}

