/**
 * Основной layout для Admin панели
 */

import { cn } from '@/lib/utils';
import { BarChart3, Bot, FileText, LayoutDashboard, LogOut, Settings, Zap } from 'lucide-react';
import { Link, Outlet, useLocation } from 'react-router-dom';

const navItems = [
    { path: '/admin/dashboard', icon: LayoutDashboard, label: 'Панель' },
    { path: '/admin/metrics', icon: BarChart3, label: 'Метрики' },
    { path: '/admin/content', icon: Zap, label: 'Контент' },
    { path: '/admin/logs', icon: FileText, label: 'Логи' },
    { path: '/admin/config', icon: Settings, label: 'Настройки' },
    { path: '/admin/telegram', icon: Bot, label: 'Telegram Bot' },
];

export function AdminLayout() {
    const location = useLocation();

    const handleLogout = () => {
        // Очищаем session и редиректим
        window.location.href = '/';
    };

    return (
        <div className="flex h-screen bg-background">
            {/* Sidebar */}
            <aside className="w-64 border-r glass flex flex-col">
                <div className="p-6">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                        PulseAI Admin
                    </h1>
                    <p className="text-sm text-muted mt-1">Панель управления</p>
                </div>

                {/* Navigation */}
                <nav className="flex-1 space-y-1 px-3">
                    {navItems.map((item) => {
                        const isActive = location.pathname.startsWith(item.path);
                        const baseClasses = 'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors';
                        const activeClasses = 'bg-primary/15 text-primary border border-primary/30';
                        const inactiveClasses = 'text-muted hover:text-text hover:bg-primary/10';

                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={cn(baseClasses, isActive ? activeClasses : inactiveClasses)}
                            >
                                <item.icon className={cn('h-5 w-5', isActive ? 'text-primary' : 'text-muted')} />
                                <span className="font-medium">{item.label}</span>
                            </Link>
                        );
                    })}
                </nav>

                {/* Logout Button */}
                <div className="p-3 border-t">
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-3 px-3 py-2 rounded-lg transition-colors hover:bg-primary/10 text-muted hover:text-text w-full"
                    >
                        <LogOut className="h-5 w-5" />
                        <span className="font-medium">Выйти</span>
                    </button>
                </div>
            </aside>

            {/* Main content */}
            <main className="flex-1 overflow-y-auto">
                <div className="container mx-auto p-8">
                    <Outlet />
                </div>
            </main>
        </div>
    );
}
