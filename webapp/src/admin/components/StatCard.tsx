/**
 * Карточка статистики для Dashboard
 * Updated with PulseAI v2 design tokens
 */

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
    label: string;
    value: number | string;
    icon: LucideIcon;
    /**
     * Icon color using design tokens
     * - 'primary' (default): бирюзовый
     * - 'accent': мятный
     * - 'warning': оранжевый
     * - 'success': зеленый
     * - 'error': красный
     * - 'purple': фиолетовый
     */
    iconColor?: 'primary' | 'accent' | 'warning' | 'success' | 'error' | 'purple';
    delay?: number;
}

const iconColorClasses = {
    primary: 'text-primary',
    accent: 'text-accent',
    warning: 'text-warning',
    success: 'text-success',
    error: 'text-error',
    purple: 'text-[#8b5cf6]',
};

export function StatCard({
    label,
    value,
    icon: Icon,
    iconColor = 'primary',
    delay = 0
}: StatCardProps) {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay, duration: 0.3 }}
        >
            <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                    <CardTitle className="text-sm font-medium text-muted">
                        {label}
                    </CardTitle>
                    <Icon className={`h-4 w-4 ${iconColorClasses[iconColor]}`} />
                </CardHeader>
                <CardContent>
                    <div className="text-2xl font-bold">{value}</div>
                </CardContent>
            </Card>
        </motion.div>
    );
}
