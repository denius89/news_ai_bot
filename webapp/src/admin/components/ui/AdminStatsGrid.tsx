/**
 * AdminStatsGrid component
 * Reusable grid layout for statistics cards
 */

import React from 'react';

interface AdminStatsGridProps {
    children: React.ReactNode;
    columns?: 2 | 3 | 4;
    className?: string;
}

const gridClasses = {
    2: 'grid gap-4 md:grid-cols-2',
    3: 'grid gap-4 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid gap-4 md:grid-cols-2 lg:grid-cols-4',
};

export function AdminStatsGrid({
    children,
    columns = 4,
    className = ''
}: AdminStatsGridProps) {
    return (
        <div className={`${gridClasses[columns]} ${className}`}>
            {children}
        </div>
    );
}
