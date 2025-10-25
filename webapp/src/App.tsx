import { AnimatePresence, motion } from 'framer-motion';
import React, { Suspense, lazy, useEffect, useMemo, useState } from 'react';
import { BrowserRouter as Router, useLocation } from 'react-router-dom';

// Lazy load pages for code splitting
const DigestPage = lazy(() => import('./pages/DigestPage'));
const EventsPage = lazy(() => import('./pages/EventsPage'));
const HomePage = lazy(() => import('./pages/HomePage'));
const NewsPage = lazy(() => import('./pages/NewsPage'));
const SettingsPage = lazy(() => import('./pages/SettingsPage'));
const TestPage = lazy(() => import('./pages/TestPage'));

// Admin Panel
import { AdminRoutes } from './admin/AdminRoutes';

// Components
import AuthDebugger from './components/AuthDebugger';
import PerformanceDisplay from './components/PerformanceDisplay';
import { TelegramWebApp } from './components/TelegramWebApp';
import { BottomNav } from './components/ui/BottomNav';

// Utils
import { AuthProvider } from './context/AuthContext';
import { shouldReduceMotion } from './utils/performance';
import { performanceMonitor } from './utils/performanceMonitor';
import { registerServiceWorker } from './utils/serviceWorker';
import { getThemePreference, initializeTheme, toggleTheme, type Theme } from './utils/theme';

// Styles
import './styles/index.css';

const App: React.FC = () => {

    const [isMobile, setIsMobile] = useState(false);
    const [activePage, setActivePage] = useState('home');
    const [theme, setTheme] = useState<Theme>('light');

    // Аутентификация теперь обрабатывается через AuthProvider

    useEffect(() => {
        const checkMobile = () => {
            setIsMobile(window.innerWidth < 768);
        };

        checkMobile();
        window.addEventListener('resize', checkMobile);

        return () => window.removeEventListener('resize', checkMobile);
    }, []);

    useEffect(() => {
        // Initialize theme system
        initializeTheme();
        setTheme(getThemePreference());

        // Register Service Worker for caching
        registerServiceWorker();

        // Initialize performance monitoring
        performanceMonitor.init();

        // Listen for theme changes from other tabs/windows
        const handleStorageChange = (e: StorageEvent) => {
            if (e.key === 'pulseai-theme') {
                const newTheme = e.newValue as Theme;
                if (newTheme === 'light' || newTheme === 'dark') {
                    setTheme(newTheme);
                }
            }
        };

        window.addEventListener('storage', handleStorageChange);

        return () => {
            window.removeEventListener('storage', handleStorageChange);
        };
    }, []);

    const handleThemeToggle = () => {
        const newTheme = toggleTheme();
        setTheme(newTheme);
    };

    const navigationItems = [
        {
            id: 'home',
            label: 'Главная',
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
            ),
            onClick: () => setActivePage('home'),
            active: activePage === 'home',
        },
        {
            id: 'news',
            label: 'Новости',
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
            ),
            onClick: () => setActivePage('news'),
            active: activePage === 'news',
        },
        {
            id: 'digest',
            label: 'Дайджест',
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
            ),
            onClick: () => setActivePage('digest'),
            active: activePage === 'digest',
        },
        {
            id: 'events',
            label: 'События',
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
            ),
            onClick: () => setActivePage('events'),
            active: activePage === 'events',
        },
        {
            id: 'settings',
            label: 'Настройки',
            icon: (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
            ),
            onClick: () => setActivePage('settings'),
            active: activePage === 'settings',
        },
    ];

    // Определяем нужно ли упростить анимации
    const reduceMotion = useMemo(() => shouldReduceMotion(), []);

    const pageVariants = useMemo(() => {
        if (reduceMotion) {
            return {
                initial: { opacity: 1 },
                in: { opacity: 1 },
                out: { opacity: 1 },
            };
        }
        return {
            initial: { opacity: 0 },
            in: { opacity: 1 },
            out: { opacity: 0 },
        };
    }, [reduceMotion]);

    const pageTransition = useMemo(() => {
        if (reduceMotion) {
            return {
                duration: 0,
            };
        }
        return {
            type: 'tween' as const,
            ease: 'easeOut' as const,
            duration: 0.2,
        };
    }, [reduceMotion]);

    const renderPage = () => {
        const pageProps = {
            theme,
            onThemeToggle: handleThemeToggle,
            onNavigate: setActivePage
        };

        const LoadingFallback = () => (
            <div className="flex items-center justify-center min-h-screen">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
        );

        switch (activePage) {
            case 'home':
                return (
                    <Suspense fallback={<LoadingFallback />}>
                        <HomePage {...pageProps} />
                    </Suspense>
                );
            case 'news':
                return (
                    <Suspense fallback={<LoadingFallback />}>
                        <NewsPage {...pageProps} />
                    </Suspense>
                );
            case 'digest':
                return (
                    <Suspense fallback={<LoadingFallback />}>
                        <DigestPage {...pageProps} />
                    </Suspense>
                );
            case 'events':
                return (
                    <Suspense fallback={<LoadingFallback />}>
                        <EventsPage {...pageProps} />
                    </Suspense>
                );
            case 'settings':
                return (
                    <Suspense fallback={<LoadingFallback />}>
                        <SettingsPage {...pageProps} />
                    </Suspense>
                );
            case 'test':
                return (
                    <Suspense fallback={<LoadingFallback />}>
                        <TestPage />
                    </Suspense>
                );
            default:
                return (
                    <Suspense fallback={<LoadingFallback />}>
                        <HomePage {...pageProps} />
                    </Suspense>
                );
        }
    };

    return (
        <TelegramWebApp>
            <AuthProvider>
                <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
                    <AppContent
                        isMobile={isMobile}
                        activePage={activePage}
                        navigationItems={navigationItems}
                        renderPage={renderPage}
                        pageVariants={pageVariants}
                        pageTransition={pageTransition}
                    />
                </Router>
            </AuthProvider>
        </TelegramWebApp>
    );
};

// Вспомогательный компонент для рендеринга контента
const AppContent: React.FC<{
    isMobile: boolean;
    activePage: string;
    navigationItems: any[];
    renderPage: () => React.ReactNode;
    pageVariants: any;
    pageTransition: any;
}> = ({ isMobile, activePage, navigationItems, renderPage, pageVariants, pageTransition }) => {
    const location = useLocation();

    // Если путь начинается с /admin, рендерим Admin панель
    if (location.pathname.startsWith('/admin')) {
        return <AdminRoutes />;
    }

    // Иначе рендерим обычное приложение
    return (
        <div className="min-h-screen bg-bg">
            <AnimatePresence mode="wait">
                <motion.div
                    key={activePage}
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                >
                    {renderPage()}
                </motion.div>
            </AnimatePresence>

            {/* Bottom Navigation for Mobile */}
            {isMobile && (
                <BottomNav
                    items={navigationItems}
                />
            )}

            {/* Desktop Navigation */}
            {!isMobile && (
                <nav className="fixed top-4 right-4 z-50">
                    <div className="flex items-center space-x-2 bg-white/90 dark:bg-surface/90 backdrop-blur-sm rounded-xl p-2 shadow-soft border border-border/50">
                        {navigationItems.map((item) => (
                            <motion.button
                                key={item.id}
                                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${item.active
                                    ? 'bg-primary text-white'
                                    : 'text-muted hover:text-text hover:bg-surface-alt'
                                    }`}
                                onClick={item.onClick}
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                            >
                                {item.icon}
                                <span>{item.label}</span>
                                {item.badge && item.badge > 0 && (
                                    <span className="bg-error text-white text-xs rounded-full px-1.5 py-0.5">
                                        {item.badge > 99 ? '99+' : item.badge}
                                    </span>
                                )}
                            </motion.button>
                        ))}
                    </div>
                </nav>
            )}

            {/* Performance Display (Development Only) */}
            <PerformanceDisplay />

            {/* Auth Debugger (Development Only) */}
            <AuthDebugger />
        </div>
    );
};

export default App;
