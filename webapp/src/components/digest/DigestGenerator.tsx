import { useDrag } from '@use-gesture/react';
import { AnimatePresence, motion } from 'framer-motion';
import { BookOpen, BookOpenCheck, Brain, Briefcase, CalendarDays, Coins, Cpu, FileText, Filter, Globe2, MessageCircle, Newspaper, Settings, Smile, Sparkles, TrendingUp, Trophy, X } from 'lucide-react';
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

const defaultData: DigestData = {
    styles: {
        newsroom: "Newsroom",
        analytical: "Аналитический",
        magazine: "Magazine",
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
        "7d": "7 дней",
        "30d": "30 дней"
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
    const [generatedDigest, setGeneratedDigest] = useState<string>('');
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
                    setData({
                        styles: stylesData.data.styles,
                        categories: { all: 'Все категории', ...categoriesData.data.categories },
                        subcategories: categoriesData.data.subcategories || {},
                        periods: categoriesData.data.periods,
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
        setGeneratedDigest('');
        setError(null); // Сбрасываем предыдущую ошибку
        triggerHapticFeedback('heavy'); // Вибрация при запуске генерации

        try {
            // Запускаем генерацию
            const digestPromise = onGenerate(selectedCategory, selectedStyle, selectedPeriod, selectedLength, selectedSubcategory);

            // Ждем немного, чтобы убедиться что запрос начался
            await new Promise(resolve => setTimeout(resolve, 100));

            // Закрываем модальное окно после того как генерация началась
            handleClose();

            // Опционально: можем подождать завершения для обработки результата
            // Но так как ошибки показываются через систему уведомлений в DigestPage,
            // это не обязательно
            const digest = await digestPromise;
            setGeneratedDigest(digest);

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
        setGeneratedDigest('');
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
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.5 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
            />

            <div className="fixed inset-0 flex items-center justify-center z-50 p-3 pb-16">
                <motion.div
                    initial={{ y: 60, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: 100, opacity: 0 }}
                    transition={{ type: "spring", stiffness: 140, damping: 18 }}
                    className={cn(
                        "relative z-50 max-w-md mx-auto rounded-2xl p-4 pb-6 backdrop-blur-2xl border max-h-[90vh] flex flex-col",
                        isDark
                            ? "glass shadow-card-hover"
                            : "glass shadow-card"
                    )}
                >

                    {/* Header */}
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex flex-col">
                            <h2 className={cn(
                                "text-[16px] font-semibold flex items-center gap-2",
                                "text-text"
                            )}>
                                <Sparkles className="text-emerald-500 w-4 h-4 animate-pulse-sparkle" />
                                Создать AI-дайджест
                            </h2>
                            <p className={cn(
                                "text-[12px] mt-0.5",
                                "text-muted"
                            )}>
                                AI отберёт лучшее и соберёт персональный дайджест.
                            </p>
                        </div>
                        <button
                            className="p-1.5 rounded-full hover:bg-gray-100/50 dark:hover:bg-gray-700/50 transition-colors flex-shrink-0"
                            onClick={handleClose}
                        >
                            <X className="w-4 h-4 text-muted" />
                        </button>
                    </div>

                    {generatedDigest ? (
                        /* Generated Digest Display */
                        <div className="flex-1 overflow-y-auto px-6">
                            <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
                                <div className="flex items-center gap-2 text-green-700 dark:text-green-300">
                                    <Sparkles className="w-5 h-5" />
                                    <span className="font-medium">AI собрал ваш новый дайджест</span>
                                </div>
                                <p className="text-green-600 dark:text-green-400 text-sm mt-1">
                                    Дайджест сохранен и добавлен в вашу коллекцию.
                                </p>
                            </div>

                            <div className="prose prose-sm max-w-none dark:prose-invert">
                                <div
                                    className="text-text dark:text-white leading-relaxed"
                                    dangerouslySetInnerHTML={{ __html: generatedDigest }}
                                />
                            </div>
                            <div className="mt-6 flex gap-3 pb-6">
                                <button
                                    className="flex-1 bg-primary text-white py-3 px-4 rounded-xl font-medium hover:bg-primary/90 transition-colors"
                                    onClick={() => navigator.clipboard.writeText(generatedDigest.replace(/<[^>]*>/g, ''))}
                                >
                                    Копировать
                                </button>
                                <button
                                    className="flex-1 bg-gray-100 dark:bg-gray-700 text-text dark:text-white py-3 px-4 rounded-xl font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                                    onClick={handleClose}
                                >
                                    Закрыть
                                </button>
                            </div>
                        </div>
                    ) : (
                        /* Generation Form */
                        <div className="flex-1 overflow-y-auto space-y-3">
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
                            <div {...categoryBind()}>
                                <h3 className={cn(
                                    "text-[13px] font-medium flex items-center gap-1.5 mb-2",
                                    "text-text"
                                )}>
                                    <Filter className="w-3.5 h-3.5 text-muted" />
                                    Категория
                                </h3>
                                <div className="grid grid-cols-2 gap-2">
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
                                                    "chip flex items-center justify-center gap-1.5 text-xs",
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
                                                "chip flex items-center justify-center gap-1.5 text-xs",
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
                                                    "chip flex items-center justify-center gap-1.5 text-xs",
                                                    selectedSubcategory === key
                                                        ? "chip-active"
                                                        : "chip-inactive"
                                                )}
                                                onClick={() => handleSubcategorySelect(key)}
                                            >
                                                <FileText className="w-3.5 h-3.5 text-emerald-500" />
                                                <span className="truncate">{label}</span>
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Style Selection */}
                            <div>
                                <h3 className={cn(
                                    "text-[13px] font-medium flex items-center gap-1.5 mb-2",
                                    "text-text"
                                )}>
                                    <Brain className="w-3.5 h-3.5 text-gray-400" />
                                    Стиль AI
                                </h3>
                                <div className="grid grid-cols-3 gap-2">
                                    {Object.entries(data.styles).map(([key, label]) => {
                                        const icons = {
                                            analytical: <Brain className="w-3.5 h-3.5" />,
                                            business: <Briefcase className="w-3.5 h-3.5" />,
                                            meme: <Smile className="w-3.5 h-3.5" />,
                                            newsroom: <Newspaper className="w-3.5 h-3.5" />,
                                            magazine: <BookOpen className="w-3.5 h-3.5" />,
                                            casual: <MessageCircle className="w-3.5 h-3.5" />,
                                            explanatory: <BookOpenCheck className="w-3.5 h-3.5" />,
                                            technical: <Settings className="w-3.5 h-3.5" />
                                        };


                                        return (
                                            <motion.button
                                                key={key}
                                                whileHover={{ scale: 1.03 }}
                                                whileTap={{ scale: 0.97 }}
                                                className={cn(
                                                    "flex flex-col items-center gap-0.5 px-1.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-300 relative overflow-hidden",
                                                    selectedStyle === key
                                                        ? isDark
                                                            ? `border-2 ${key === 'newsroom' ? 'border-red-400/60 bg-red-950/30 text-red-300' :
                                                                key === 'analytical' ? 'border-blue-400/60 bg-blue-950/30 text-blue-300' :
                                                                    key === 'magazine' ? 'border-purple-400/60 bg-purple-950/30 text-purple-300' :
                                                                        key === 'casual' ? 'border-green-400/60 bg-green-950/30 text-green-300' :
                                                                            key === 'business' ? 'border-orange-400/60 bg-orange-950/30 text-orange-300' :
                                                                                key === 'explanatory' ? 'border-cyan-400/60 bg-cyan-950/30 text-cyan-300' :
                                                                                    key === 'technical' ? 'border-indigo-400/60 bg-indigo-950/30 text-indigo-300' :
                                                                                        'border-gray-400/60 bg-gray-950/30 text-gray-300'
                                                            } shadow-[0_0_20px_rgba(59,130,246,0.3)]`
                                                            : `border-2 ${key === 'newsroom' ? 'border-red-400/60 bg-red-50 text-red-600' :
                                                                key === 'analytical' ? 'border-blue-400/60 bg-blue-50 text-blue-600' :
                                                                    key === 'magazine' ? 'border-purple-400/60 bg-purple-50 text-purple-600' :
                                                                        key === 'casual' ? 'border-green-400/60 bg-green-50 text-green-600' :
                                                                            key === 'business' ? 'border-orange-400/60 bg-orange-50 text-orange-600' :
                                                                                key === 'explanatory' ? 'border-cyan-400/60 bg-cyan-50 text-cyan-600' :
                                                                                    key === 'technical' ? 'border-indigo-400/60 bg-indigo-50 text-indigo-600' :
                                                                                        'border-gray-400/60 bg-gray-50 text-gray-600'
                                                            } shadow-[0_0_20px_rgba(59,130,246,0.2)]`
                                                        : isDark
                                                            ? "border bg-surface-alt text-text hover:border-primary-700"
                                                            : "border bg-surface hover:border-primary text-text"
                                                )}
                                                onClick={() => handleStyleSelect(key)}
                                            >
                                                {/* Gradient shimmer effect for selected style */}
                                                {selectedStyle === key && (
                                                    <div className={cn(
                                                        "absolute inset-0 rounded-xl bg-gradient-to-r opacity-20 animate-shimmer",
                                                        key === 'newsroom' && "from-red-400 via-orange-400 to-red-300",
                                                        key === 'analytical' && "from-blue-400 via-cyan-400 to-teal-300",
                                                        key === 'magazine' && "from-purple-400 via-violet-400 to-purple-300",
                                                        key === 'casual' && "from-green-400 via-emerald-400 to-green-300",
                                                        key === 'business' && "from-orange-400 via-amber-400 to-orange-300",
                                                        key === 'explanatory' && "from-cyan-400 via-blue-400 to-cyan-300",
                                                        key === 'technical' && "from-indigo-400 via-purple-400 to-indigo-300"
                                                    )} />
                                                )}
                                                <div className="relative z-10">
                                                    {icons[key as keyof typeof icons]}
                                                    <span className="text-center leading-tight">{label}</span>
                                                </div>
                                            </motion.button>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Period Selection */}
                            <div>
                                <h3 className={cn(
                                    "text-[13px] font-medium flex items-center gap-1.5 mb-2",
                                    "text-text"
                                )}>
                                    <CalendarDays className="w-3.5 h-3.5 text-muted" /> Период
                                </h3>
                                <div className="grid grid-cols-3 gap-2">
                                    {Object.entries(data.periods).map(([key, label]) => (
                                        <motion.button
                                            key={key}
                                            whileHover={{ scale: 1.03 }}
                                            whileTap={{ scale: 0.97 }}
                                            className={cn(
                                                "chip text-xs",
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
                            </div>

                            {/* Length Selection */}
                            <div>
                                <h3 className={cn(
                                    "text-[13px] font-medium flex items-center gap-1.5 mb-2",
                                    "text-text"
                                )}>
                                    <FileText className="w-3.5 h-3.5 text-muted" /> Длина текста
                                </h3>
                                <div className="grid grid-cols-3 gap-2">
                                    {Object.entries(data.lengths).map(([key, label]) => (
                                        <motion.button
                                            key={key}
                                            whileHover={{ scale: 1.03 }}
                                            whileTap={{ scale: 0.97 }}
                                            className={cn(
                                                "chip text-xs",
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
                            </div>

                            {/* Generate Button with Holographic Effect */}
                            <div className="mt-4">
                                <motion.button
                                    whileHover={!isGenerating ? { scale: 1.02 } : {}}
                                    whileTap={!isGenerating ? { scale: 0.96 } : {}}
                                    transition={{ type: "spring", stiffness: 220, damping: 18 }}
                                    className={cn(
                                        "w-full py-2.5 text-[14px] font-semibold rounded-lg transition-all duration-300",
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
                                    Готовлю дайджест как личный аналитик. Это займёт пару секунд.
                                </p>
                            </div>
                        </div>
                    )}
                </motion.div>
            </div>

            {/* Magic Progress теперь показывается на уровне DigestPage */}
        </AnimatePresence>
    );
};

export default DigestGenerator;
