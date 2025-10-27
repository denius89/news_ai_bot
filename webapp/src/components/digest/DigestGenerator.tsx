import { useDrag } from '@use-gesture/react';
import { AnimatePresence, motion } from 'framer-motion';
import { Brain, CalendarDays, Coins, Cpu, FileText, Filter, Globe2, Sparkles, TrendingUp, Trophy, X } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import { cn } from '../../lib/utils';
// import { useUserPreferences } from '../../hooks/useUserPreferences';
import '../../styles/holographic.css';
import { initHoloMotion } from '../../utils/holoMotion';

interface DigestGeneratorProps {
    isOpen: boolean;
    onClose: () => void;
    onGenerate: (category: string, style: string, period: string, length: string, subcategory?: string | null) => Promise<string>;
    userId?: string; // Добавляем userId для сохранения предпочтений
}

interface DigestData {
    styles: Record<string, string>;
    categories: Record<string, string>;
    subcategories: Record<string, Record<string, string>>;
    periods: Record<string, string>;
    lengths: Record<string, string>;
}

// Helper function to shorten long category labels
const shortenCategoryLabel = (label: string): string => {
    if (label.includes(',')) return label.split(',')[0].trim();
    if (label.length > 15) return label.split(' ')[0];
    return label;
};

const defaultData: DigestData = {
    styles: {
        newsroom: "Ньюсрум",
        analytical: "Аналитический",
        magazine: "Магазин",
        casual: "Простой",
        business: "Бизнес",
        explanatory: "Объяснительный",
        technical: "Технический"
    },
    categories: {
        all: "Все категории",
        crypto: "Криптовалюты",
        sports: "Спорт",
        markets: "Рынки",
        tech: "Технологии",
        world: "Мир"
    },
    subcategories: {},
    periods: {
        today: "Сегодня",
        "7d": "За неделю",
        "30d": "За месяц"
    },
    lengths: {
        short: "Короткий",
        medium: "Средний",
        long: "Длинный"
    }
};

export const DigestGenerator: React.FC<DigestGeneratorProps> = ({
    isOpen,
    onClose,
    onGenerate,
    userId: _userId
}) => {
    const [isGenerating, setIsGenerating] = useState(false);
    const [data, setData] = useState<DigestData>(defaultData);
    const [isDark, setIsDark] = useState(false);
    const [deviceOrientation, setDeviceOrientation] = useState({ alpha: 0, beta: 0, gamma: 0 });
    const [error, setError] = useState<string | null>(null);

    // Используем хук предпочтений пользователя
    // Временно отключено - используется старый интерфейс
    // const {
    //   preferences,
    //   isLoading: preferencesLoading,
    //   savePreferences,
    //   updateAfterDigestGeneration
    // } = useUserPreferences(userId);

    // Состояния для выбранных значений (временно с дефолтными значениями)
    const [selectedCategory, setSelectedCategory] = useState("all");
    const [selectedSubcategory, setSelectedSubcategory] = useState<string | null>(null);
    const [selectedStyle, setSelectedStyle] = useState("analytical");
    const [selectedPeriod, setSelectedPeriod] = useState("today");
    const [selectedLength, setSelectedLength] = useState('medium');

    // Синхронизируем состояния с предпочтениями при их загрузке
    // useEffect(() => {
    //   if (!preferencesLoading) {
    //     setSelectedCategory(preferences.preferred_category);
    //     setSelectedStyle(preferences.preferred_style);
    //     setSelectedPeriod(preferences.preferred_period);
    //   }
    // }, [preferences, preferencesLoading]);

    // Определяем тему на основе CSS класса или data-атрибута основного приложения
    useEffect(() => {
        const checkTheme = () => {
            // Проверяем наличие dark класса на html или body
            const htmlElement = document.documentElement;
            const bodyElement = document.body;

            const hasDarkClass = htmlElement.classList.contains('dark') ||
                bodyElement.classList.contains('dark') ||
                htmlElement.getAttribute('data-theme') === 'dark';

            console.log('HTML classes:', htmlElement.className);
            console.log('Body classes:', bodyElement.className);
            console.log('HTML data-theme:', htmlElement.getAttribute('data-theme'));
            console.log('Detected isDark:', hasDarkClass);

            setIsDark(hasDarkClass);
        };

        // Проверяем сразу
        checkTheme();

        // Создаем наблюдатель за изменениями классов
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'attributes' &&
                    (mutation.attributeName === 'class' || mutation.attributeName === 'data-theme')) {
                    checkTheme();
                }
            });
        });

        // Наблюдаем за изменениями в html элементе
        observer.observe(document.documentElement, {
            attributes: true,
            attributeFilter: ['class', 'data-theme']
        });

        // Также наблюдаем за body на всякий случай
        observer.observe(document.body, {
            attributes: true,
            attributeFilter: ['class']
        });

        return () => {
            observer.disconnect();
        };
    }, []);

    // Отслеживание ориентации устройства для голографического эффекта
    useEffect(() => {
        const handleOrientationChange = (event: DeviceOrientationEvent) => {
            setDeviceOrientation({
                alpha: event.alpha || 0,
                beta: event.beta || 0,
                gamma: event.gamma || 0
            });
        };

        // Запрашиваем разрешение на доступ к датчикам ориентации
        if (typeof DeviceOrientationEvent !== 'undefined' &&
            typeof (DeviceOrientationEvent as any).requestPermission === 'function') {
            (DeviceOrientationEvent as any).requestPermission()
                .then((response: string) => {
                    if (response === 'granted') {
                        window.addEventListener('deviceorientation', handleOrientationChange);
                    }
                })
                .catch(() => {
                    // Если разрешение не получено, используем fallback
                    console.log('Device orientation permission denied');
                });
        } else {
            // Для браузеров без запроса разрешения
            window.addEventListener('deviceorientation', handleOrientationChange);
        }

        return () => {
            window.removeEventListener('deviceorientation', handleOrientationChange);
        };
    }, []);

    // Инициализация голографического эффекта
    useEffect(() => {
        initHoloMotion(deviceOrientation);
    }, [deviceOrientation]);

    // Блокировка скролла body при открытии модалки
    useEffect(() => {
        if (isOpen) {
            // Сохраняем текущую позицию скролла
            const scrollY = window.scrollY;

            // Блокируем скролл body
            document.body.style.overflow = 'hidden';
            document.body.style.position = 'fixed';
            document.body.style.top = `-${scrollY}px`;
            document.body.style.width = '100%';
        } else {
            // Восстанавливаем скролл
            const scrollY = document.body.style.top;
            document.body.style.overflow = '';
            document.body.style.position = '';
            document.body.style.top = '';
            document.body.style.width = '';

            // Восстанавливаем позицию скролла
            window.scrollTo(0, parseInt(scrollY || '0') * -1);
        }

        return () => {
            // Cleanup при размонтировании
            document.body.style.overflow = '';
            document.body.style.position = '';
            document.body.style.top = '';
            document.body.style.width = '';
        };
    }, [isOpen]);

    // ФУНКЦИИ ДЛЯ МОБИЛЬНЫХ ЖЕСТОВ И HAPTIC FEEDBACK
    const triggerHapticFeedback = (type: 'light' | 'medium' | 'heavy' = 'light') => {
        // if (!preferences.enable_haptic_feedback || !navigator.vibrate) return;
        if (!navigator.vibrate) return;

        const patterns = {
            light: [10],
            medium: [20],
            heavy: [30]
        };

        navigator.vibrate(patterns[type]);
    };

    const getNextCategory = (currentCategory: string) => {
        const categories = Object.keys(data.categories);
        const currentIndex = categories.indexOf(currentCategory);
        return categories[(currentIndex + 1) % categories.length];
    };

    const getPrevCategory = (currentCategory: string) => {
        const categories = Object.keys(data.categories);
        const currentIndex = categories.indexOf(currentCategory);
        return categories[(currentIndex - 1 + categories.length) % categories.length];
    };

    // ЖЕСТЫ ДЛЯ КАТЕГОРИЙ
    const categoryBind = useDrag(
        ({ direction: [dx], distance }) => {
            // if (!preferences.enable_gestures || isGenerating) return;
            if (isGenerating) return;

            // Горизонтальный swipe для переключения категорий
            if (Math.abs(dx) > Math.abs(distance[0]) * 0.7) {
                if (dx > 0) {
                    // Swipe вправо - предыдущая категория
                    setSelectedCategory(getPrevCategory(selectedCategory));
                    triggerHapticFeedback('light');
                } else {
                    // Swipe влево - следующая категория
                    setSelectedCategory(getNextCategory(selectedCategory));
                    triggerHapticFeedback('light');
                }
            }
        },
        {
            axis: 'x',
            threshold: 50,
            preventDefault: true
        }
    );


    // Load data from API on mount
    React.useEffect(() => {
        const loadData = async () => {
            try {
                const [stylesRes, categoriesRes] = await Promise.all([
                    fetch('/api/digests/styles'),
                    fetch('/api/digests/categories')
                ]);

                const stylesData = await stylesRes.json();
                const categoriesData = await categoriesRes.json();

                if (stylesData.status === 'success' && categoriesData.status === 'success') {
                    // Используем периоды напрямую из API (без нормализации)
                    // API уже возвращает правильные тексты: "Сегодня", "За неделю", "За месяц"

                    // Применяем переводы к стилям из API
                    const translateStyles = (styles: Record<string, string>) => {
                        const translations: Record<string, string> = {
                            'newsroom': 'Ньюсрум',
                            'magazine': 'Журнальный',
                            'Newsroom': 'Ньюсрум',
                            'Magazine': 'Журнальный'
                        };

                        const translatedStyles = { ...styles };
                        for (const key in translatedStyles) {
                            if (translations[translatedStyles[key]]) {
                                translatedStyles[key] = translations[translatedStyles[key]];
                            }
                        }
                        return translatedStyles;
                    };

                    setData({
                        styles: translateStyles(stylesData.data.styles),
                        categories: { all: 'Все категории', ...categoriesData.data.categories },
                        subcategories: categoriesData.data.subcategories || {},
                        periods: categoriesData.data.periods || defaultData.periods,
                        lengths: {
                            short: "Короткий",
                            medium: "Средний",
                            long: "Длинный"
                        }
                    });
                }
            } catch (error) {
                console.warn('Failed to load digest data, using defaults:', error);
            }
        };

        if (isOpen) {
            loadData();
        }
    }, [isOpen]);

    const handleGenerate = async () => {
        setIsGenerating(true);
        setError(null); // Сбрасываем предыдущую ошибку
        triggerHapticFeedback('heavy'); // Вибрация при запуске генерации

        try {
            // Запускаем генерацию
            const digestPromise = onGenerate(selectedCategory, selectedStyle, selectedPeriod, selectedLength, selectedSubcategory);

            // Ждем немного, чтобы убедиться что запрос начался
            await new Promise(resolve => setTimeout(resolve, 100));

            // Закрываем модальное окно после того как генерация началась
            handleClose();

            // Ждем завершения для обработки возможных ошибок
            await digestPromise;

            // Сохраняем предпочтения после успешной генерации
            // await updateAfterDigestGeneration(selectedCategory, selectedStyle, selectedPeriod);

        } catch (error) {
            console.error('Failed to generate digest:', error);
            // Ошибки обрабатываются в DigestPage через showNotification
            // Здесь просто логируем для отладки
            const errorMessage = error instanceof Error ? error.message : 'Произошла ошибка при генерации дайджеста';
            console.error('Digest generation error:', errorMessage);
        } finally {
            setIsGenerating(false);
        }
    };

    const handleClose = () => {
        setSelectedCategory('all');
        setSelectedSubcategory(null);
        setSelectedStyle('analytical');
        setSelectedPeriod('today');
        setIsGenerating(false);
        setError(null);
        onClose();
    };

    // ОБРАБОТЧИКИ С HAPTIC FEEDBACK И СОХРАНЕНИЕМ ПРЕДПОЧТЕНИЙ
    const handleCategorySelect = async (category: string) => {
        setSelectedCategory(category);
        setSelectedSubcategory(null); // Reset subcategory when category changes
        setError(null); // Сбрасываем ошибку при изменении параметров
        triggerHapticFeedback('light');
        // await savePreferences({ preferred_category: category });
    };

    const handleStyleSelect = async (style: string) => {
        setSelectedStyle(style);
        setError(null); // Сбрасываем ошибку при изменении параметров
        triggerHapticFeedback('medium');
        // await savePreferences({ preferred_style: style });
    };

    const handlePeriodSelect = async (period: string) => {
        setSelectedPeriod(period);
        setError(null); // Сбрасываем ошибку при изменении параметров
        triggerHapticFeedback('light');
        // await savePreferences({ preferred_period: period });
    };

    const handleSubcategorySelect = (subcategory: string | null) => {
        setSelectedSubcategory(subcategory);
        setError(null); // Сбрасываем ошибку при изменении параметров
        triggerHapticFeedback('light');
    };

    const handleLengthSelect = (length: string) => {
        setSelectedLength(length);
        setError(null); // Сбрасываем ошибку при изменении параметров
        triggerHapticFeedback('light');
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 0.5 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.3 }}
                        className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
                        onClick={handleClose}
                        onTouchMove={(e) => e.preventDefault()}
                    />

                    <div className="fixed inset-0 flex items-center justify-center z-50 p-3 pb-16">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.98 }}
                            animate={{ opacity: 1, scale: 1 }}
                            exit={{ y: 100, opacity: 0 }}
                            transition={{ duration: 0.35, ease: "easeOut" }}
                            className={cn(
                                "relative z-50 max-w-md mx-auto rounded-2xl p-4 pb-[100px] backdrop-blur-2xl border max-h-[90vh] flex flex-col",
                                isDark
                                    ? "glass shadow-card-hover"
                                    : "glass shadow-card"
                            )}
                        >

                            {/* Header */}
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex flex-col">
                                    <h2 className={cn(
                                        "text-sm font-semibold flex items-center gap-2",
                                        "text-text"
                                    )}>
                                        <Sparkles className="text-blue-500 w-4 h-4 animate-pulse-sparkle" />
                                        Создать AI-дайджест
                                    </h2>
                                    <p className={cn(
                                        "text-[10px] mt-0.5",
                                        "text-muted"
                                    )}>
                                        Я соберу свежие новости и оформлю их в подборку.
                                    </p>
                                </div>
                                <button
                                    className="p-1.5 rounded-full hover:bg-gray-100/50 dark:hover:bg-gray-700/50 transition-colors flex-shrink-0"
                                    onClick={handleClose}
                                >
                                    <X className="w-4 h-4 text-muted" />
                                </button>
                            </div>

                            {/* Generation Form */}
                            <div
                                className="flex-1 overflow-y-auto scrollbar-hide space-y-3"
                                style={{
                                    overscrollBehavior: 'contain',
                                    WebkitOverflowScrolling: 'touch',
                                    touchAction: 'pan-y'
                                }}
                            >
                                {/* Error Display */}
                                {error && (
                                    <div className="mb-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
                                        <div className="flex items-center gap-2 text-red-700 dark:text-red-300">
                                            <div className="w-4 h-4 rounded-full bg-red-500 flex-shrink-0"></div>
                                            <span className="font-medium text-sm">Ошибка генерации</span>
                                        </div>
                                        <p className="text-red-600 dark:text-red-400 text-xs mt-1">
                                            {error}
                                        </p>
                                    </div>
                                )}

                                {/* Category Selection */}
                                <motion.section
                                    initial={{ opacity: 0, y: 8 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0, duration: 0.25, ease: "easeOut" }}
                                >
                                    <div {...categoryBind()}>
                                        <h3 className={cn(
                                            "text-xs font-medium flex items-center gap-1.5 mb-1",
                                            "text-text"
                                        )}>
                                            <Filter className="w-3.5 h-3.5 text-muted" />
                                            Тематика
                                        </h3>
                                        <p className={cn(
                                            "text-gray-400 dark:text-gray-500 text-[10px] leading-tight mb-2"
                                        )}>
                                            Что тебе интересно сейчас
                                        </p>
                                        <div className="flex flex-wrap gap-2">
                                            {Object.entries(data.categories).map(([key, label]) => {
                                                const getIcon = (categoryKey: string) => {
                                                    switch (categoryKey) {
                                                        case 'all': return <Globe2 className="w-3.5 h-3.5 text-emerald-500" />;
                                                        case 'crypto': return <Coins className="w-3.5 h-3.5 text-emerald-500" />;
                                                        case 'markets': return <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />;
                                                        case 'sports': return <Trophy className="w-3.5 h-3.5 text-emerald-500" />;
                                                        case 'tech': return <Cpu className="w-3.5 h-3.5 text-emerald-500" />;
                                                        case 'world': return <Globe2 className="w-3.5 h-3.5 text-emerald-500" />;
                                                        default: return <Globe2 className="w-3.5 h-3.5 text-emerald-500" />;
                                                    }
                                                };

                                                return (
                                                    <motion.button
                                                        key={key}
                                                        whileHover={{ scale: 1.03 }}
                                                        whileTap={{ scale: 0.97 }}
                                                        className={cn(
                                                            "chip flex items-center justify-center gap-1.5",
                                                            selectedCategory === key
                                                                ? "chip-active"
                                                                : "chip-inactive"
                                                        )}
                                                        onClick={() => handleCategorySelect(key)}
                                                    >
                                                        {getIcon(key)}
                                                        {label}
                                                    </motion.button>
                                                );
                                            })}
                                        </div>
                                    </div>
                                </motion.section>

                                {/* Subcategory Selection */}
                                {selectedCategory !== "all" && data.subcategories[selectedCategory] && Object.keys(data.subcategories[selectedCategory]).length > 0 && (
                                    <div>
                                        <h3 className={cn(
                                            "text-[13px] font-medium flex items-center gap-1.5 mb-2",
                                            "text-text"
                                        )}>
                                            <FileText className="w-3.5 h-3.5 text-muted" />
                                            Подкатегория
                                        </h3>
                                        <div className="grid grid-cols-2 gap-2">
                                            <button
                                                className={cn(
                                                    "chip flex items-center justify-center gap-1.5",
                                                    selectedSubcategory === null
                                                        ? "chip-active"
                                                        : "chip-inactive"
                                                )}
                                                onClick={() => handleSubcategorySelect(null)}
                                            >
                                                <Globe2 className="w-3.5 h-3.5 text-emerald-500" />
                                                Все
                                            </button>
                                            {Object.entries(data.subcategories[selectedCategory]).map(([key, label]) => (
                                                <button
                                                    key={key}
                                                    className={cn(
                                                        "chip flex items-center justify-center gap-1.5",
                                                        selectedSubcategory === key
                                                            ? "chip-active"
                                                            : "chip-inactive"
                                                    )}
                                                    onClick={() => handleSubcategorySelect(key)}
                                                >
                                                    <FileText className="w-3.5 h-3.5 text-emerald-500" />
                                                    <span className="truncate">{shortenCategoryLabel(label)}</span>
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Style Selection */}
                                <motion.section
                                    initial={{ opacity: 0, y: 8 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.05, duration: 0.25, ease: "easeOut" }}
                                >
                                    <h3 className={cn(
                                        "text-xs font-medium flex items-center gap-1.5 mb-1",
                                        "text-text"
                                    )}>
                                        <Brain className="w-3.5 h-3.5 text-gray-400" />
                                        Стиль текста
                                    </h3>
                                    <p className={cn(
                                        "text-gray-400 dark:text-gray-500 text-xs leading-tight mb-2"
                                    )}>
                                        Как подать материал
                                    </p>
                                    <div className="grid grid-cols-3 gap-2">
                                        {Object.entries(data.styles).map(([key, label]) => {
                                            return (
                                                <motion.button
                                                    key={key}
                                                    whileHover={{ scale: 1.03 }}
                                                    whileTap={{ scale: 0.97 }}
                                                    className={cn(
                                                        "flex items-center justify-center px-3 py-2 rounded-lg text-xs font-medium transition-all duration-300",
                                                        selectedStyle === key
                                                            ? "text-white"
                                                            : "bg-surface-alt text-muted hover:bg-surfaceAlt"
                                                    )}
                                                    style={selectedStyle === key ? {
                                                        background: 'var(--grad-ai-flow)',
                                                        boxShadow: '0 0 12px rgba(0, 166, 200, 0.3)'
                                                    } : undefined}
                                                    onClick={() => handleStyleSelect(key)}
                                                >
                                                    <span className="text-center leading-tight">{label}</span>
                                                </motion.button>
                                            );
                                        })}
                                    </div>
                                </motion.section>

                                {/* Period Selection */}
                                <motion.section
                                    initial={{ opacity: 0, y: 8 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.1, duration: 0.25, ease: "easeOut" }}
                                >
                                    <h3 className={cn(
                                        "text-xs font-medium flex items-center gap-1.5 mb-1",
                                        "text-text"
                                    )}>
                                        <CalendarDays className="w-3.5 h-3.5 text-muted" /> Когда опубликовано
                                    </h3>
                                    <p className={cn(
                                        "text-gray-400 dark:text-gray-500 text-xs leading-tight mb-2"
                                    )}>
                                        Новости за какой период
                                    </p>
                                    <div className="grid grid-cols-3 gap-2">
                                        {Object.entries(data.periods)
                                            .sort(([a], [b]) => {
                                                // Сортируем в логичном порядке: сегодня -> неделя -> месяц
                                                const order = { 'today': 0, '7d': 1, '30d': 2 };
                                                return (order[a as keyof typeof order] || 999) - (order[b as keyof typeof order] || 999);
                                            })
                                            .map(([key, label]) => (
                                                <motion.button
                                                    key={key}
                                                    whileHover={{ scale: 1.03 }}
                                                    whileTap={{ scale: 0.97 }}
                                                    className={cn(
                                                        "chip",
                                                        selectedPeriod === key
                                                            ? "chip-active"
                                                            : "chip-inactive"
                                                    )}
                                                    onClick={() => handlePeriodSelect(key)}
                                                >
                                                    {label}
                                                </motion.button>
                                            ))}
                                    </div>
                                </motion.section>

                                {/* Length Selection */}
                                <motion.section
                                    initial={{ opacity: 0, y: 8 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.15, duration: 0.25, ease: "easeOut" }}
                                >
                                    <h3 className={cn(
                                        "text-xs font-medium flex items-center gap-1.5 mb-1",
                                        "text-text"
                                    )}>
                                        <FileText className="w-3.5 h-3.5 text-muted" /> Объём дайджеста
                                    </h3>
                                    <p className={cn(
                                        "text-gray-400 dark:text-gray-500 text-xs leading-tight mb-2"
                                    )}>
                                        Сколько хочешь читать
                                    </p>
                                    <div className="grid grid-cols-3 gap-2">
                                        {Object.entries(data.lengths).map(([key, label]) => (
                                            <motion.button
                                                key={key}
                                                whileHover={{ scale: 1.03 }}
                                                whileTap={{ scale: 0.97 }}
                                                className={cn(
                                                    "chip",
                                                    selectedLength === key
                                                        ? "chip-active"
                                                        : "chip-inactive"
                                                )}
                                                onClick={() => handleLengthSelect(key)}
                                            >
                                                {label}
                                            </motion.button>
                                        ))}
                                    </div>
                                </motion.section>

                                {/* Generate Button with Holographic Effect */}
                                <div className="mt-4">
                                    <motion.button
                                        whileHover={!isGenerating ? { scale: 1.02 } : {}}
                                        whileTap={!isGenerating ? { scale: 0.96 } : {}}
                                        transition={{ type: "spring", stiffness: 220, damping: 18 }}
                                        className={cn(
                                            "w-full py-2.5 text-xs font-semibold rounded-lg transition-all duration-300",
                                            isGenerating
                                                ? "opacity-60 cursor-not-allowed"
                                                : "cursor-pointer"
                                        )}
                                        style={{
                                            background: isGenerating
                                                ? 'linear-gradient(90deg, rgba(0,166,200,0.7), rgba(79,70,229,0.7))'
                                                : 'var(--grad-ai-flow)',
                                            color: 'white',
                                            boxShadow: isGenerating
                                                ? '0 0 6px rgba(0, 166, 200, 0.2)'
                                                : '0 0 12px rgba(0, 166, 200, 0.3)'
                                        }}
                                        onClick={handleGenerate}
                                        disabled={isGenerating}
                                    >
                                        {isGenerating ? (
                                            <div className="flex items-center justify-center gap-2">
                                                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                                AI анализирует…
                                            </div>
                                        ) : (
                                            <motion.span
                                                animate={{ opacity: [0.8, 1, 0.8] }}
                                                transition={{ duration: 3, repeat: Infinity }}
                                                className="flex items-center justify-center gap-2"
                                            >
                                                <Sparkles className="inline w-4 h-4" /> Сгенерировать дайджест
                                            </motion.span>
                                        )}
                                    </motion.button>

                                    <p className={cn(
                                        "text-[10px] text-center mt-1.5",
                                        "text-muted"
                                    )}>
                                        Подготовка займёт несколько секунд…
                                    </p>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    );
};

export default DigestGenerator;
