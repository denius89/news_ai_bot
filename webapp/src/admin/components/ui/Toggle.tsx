import { cn } from '@/lib/utils';
import { motion } from 'framer-motion';

type ToggleProps = {
    checked: boolean;
    onChange: (checked: boolean) => void;
    disabled?: boolean;
    className?: string;
    label?: string;
};

export function Toggle({ checked, onChange, disabled = false, className = '', label }: ToggleProps) {
    return (
        <label className={cn('flex items-center gap-2 cursor-pointer', disabled && 'opacity-60', className)}>
            <motion.div
                className={cn(
                    'relative w-9 h-5 rounded-full transition-colors',
                    checked ? 'bg-primary' : 'bg-muted'
                )}
                whileTap={{ scale: 0.95 }}
            >
                <motion.div
                    className="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow-sm"
                    animate={{
                        x: checked ? 16 : 2,
                    }}
                    transition={{
                        type: 'spring',
                        stiffness: 500,
                        damping: 30,
                    }}
                />
            </motion.div>
            {label && (
                <span className="text-sm text-text">
                    {label}
                </span>
            )}
            <input
                type="checkbox"
                checked={checked}
                onChange={(e) => onChange(e.target.checked)}
                disabled={disabled}
                className="sr-only"
            />
        </label>
    );
}
