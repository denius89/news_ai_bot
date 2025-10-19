import { AnimatePresence, motion } from "framer-motion";
import { BookOpen, Brain, Briefcase, Cpu, FileText, Laugh, MessageCircle, Newspaper } from "lucide-react";
import { useEffect, useState } from "react";

const personalities = {
    analytical: {
        color: "from-blue-400 via-cyan-300 to-blue-500",
        icon: <Brain className="w-10 h-10 text-blue-400" />,
        phrases: [
            "Провожу глубокий анализ новостных трендов...",
            "Сравниваю источники и выявляю закономерности...",
            "Оцениваю достоверность и важность...",
            "Формирую объективный дайджест на основе данных..."
        ]
    },
    business: {
        color: "from-amber-400 via-yellow-300 to-orange-400",
        icon: <Briefcase className="w-10 h-10 text-amber-400" />,
        phrases: [
            "Отбираю ключевые экономические события...",
            "Ищу сигналы для решений и инвестиций...",
            "Проверяю отчёты и тенденции...",
            "Создаю дайджест в деловом тоне..."
        ]
    },
    meme: {
        color: "from-pink-400 via-purple-400 to-fuchsia-400",
        icon: <Laugh className="w-10 h-10 text-pink-400" />,
        phrases: [
            "Перевожу новости на язык мемов 😎",
            "Добавляю немного сарказма...",
            "AI с чувством юмора на связи 🤖",
            "Собираю весёлую сводку событий!"
        ]
    },

    // НОВЫЕ СТИЛИ v2
    newsroom: {
        color: "from-slate-400 via-gray-300 to-slate-500",
        icon: <Newspaper className="w-10 h-10 text-slate-400" />,
        phrases: [
            "Собираю факты из проверенных источников...",
            "Анализирую ключевые события и цифры...",
            "Проверяю достоверность информации...",
            "Формирую краткую сводку в стиле Reuters..."
        ]
    },

    magazine: {
        color: "from-violet-400 via-purple-300 to-indigo-400",
        icon: <BookOpen className="w-10 h-10 text-violet-400" />,
        phrases: [
            "Ищу интересные детали и контекст...",
            "Превращаю факты в увлекательную историю...",
            "Добавляю глубину и storytelling...",
            "Создаю дайджест в стиле The Atlantic..."
        ]
    },

    casual: {
        color: "from-teal-400 via-cyan-300 to-emerald-400",
        icon: <MessageCircle className="w-10 h-10 text-teal-400" />,
        phrases: [
            "Перевожу новости на простой язык...",
            "Убираю все сложное и скучное...",
            "Делаю дайджест для чтения в метро 🚇",
            "Формирую удобную сводку для Telegram..."
        ]
    },

    explanatory: {
        color: "from-indigo-400 via-blue-300 to-purple-400",
        icon: <FileText className="w-10 h-10 text-indigo-400" />,
        phrases: [
            "Объясняю сложные термины простыми словами...",
            "Добавляю контекст и историю вопроса...",
            "Разбираю причины и следствия событий...",
            "Делаю новости понятными для всех..."
        ]
    },

    technical: {
        color: "from-emerald-400 via-green-300 to-teal-400",
        icon: <Cpu className="w-10 h-10 text-emerald-400" />,
        phrases: [
            "Анализирую технические детали и спецификации...",
            "Изучаю архитектуру и алгоритмы...",
            "Сравниваю производительность и benchmark'и...",
            "Формирую дайджест для разработчиков..."
        ]
    }
};

interface DigestMagicProgressProps {
    style: 'analytical' | 'business' | 'meme' | 'newsroom' | 'magazine' | 'casual' | 'explanatory' | 'technical';
    tone?: 'neutral' | 'insightful' | 'critical' | 'optimistic';
    isGenerating: boolean; // Передаётся из DigestPage
    onComplete?: () => void; // Callback для родителя (опционально)
}

export const DigestMagicProgress: React.FC<DigestMagicProgressProps> = ({
    style = "analytical",
    tone = "neutral",
    isGenerating,
    onComplete
}) => {
    // Гибридный timing system - состояния
    const [showOverlay, setShowOverlay] = useState(false);
    const [isVisible, setIsVisible] = useState(false);
    const [isReady, setIsReady] = useState(false);
    const [minTimePassed, setMinTimePassed] = useState(false);
    const [showFlare, setShowFlare] = useState(false);
    const [phraseIndex, setPhraseIndex] = useState(0);

    // Check for reduced motion preference
    const prefersReducedMotion = typeof window !== 'undefined' &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Защита от неожиданных значений style
    const safeStyle = style && personalities[style as keyof typeof personalities] ? style : "analytical";
    const persona = personalities[safeStyle] || personalities.analytical;

    // Адаптация фраз по тону
    const getPhrases = (style: string, tone?: string) => {
        const basePersona = personalities[style as keyof typeof personalities] || personalities.analytical;

        if (!basePersona || !basePersona.phrases) {
            return ["Генерирую дайджест..."];
        }

        if (tone === 'critical') {
            return [
                ...basePersona.phrases,
                "Проверяю противоречия в источниках...",
                "Анализирую скрытые мотивы..."
            ];
        }

        if (tone === 'optimistic') {
            return [
                ...basePersona.phrases,
                "Ищу позитивные тренды...",
                "Выделяю успешные решения..."
            ];
        }

        return basePersona.phrases;
    };

    const adaptedPhrases = getPhrases(safeStyle, tone);

    // Гибридный timing system - минимум 5s, максимум 15s
    useEffect(() => {
        if (!isGenerating) return;

        // Минимум 5 секунд
        const minTimer = setTimeout(() => setMinTimePassed(true), 5000);

        // Максимум 15 секунд - force complete
        const maxTimer = setTimeout(() => {
            setShowFlare(true);
            setTimeout(() => onComplete?.(), 800);
        }, 15000);

        return () => {
            clearTimeout(minTimer);
            clearTimeout(maxTimer);
        };
    }, [isGenerating, onComplete]);

    // Когда API завершился и минимум прошёл
    useEffect(() => {
        if (!isGenerating && minTimePassed) {
            setShowFlare(true);
            setTimeout(() => onComplete?.(), 800);
        }
    }, [isGenerating, minTimePassed, onComplete]);

    // Показ overlay при запуске генерации
    useEffect(() => {
        if (isGenerating) {
            const timer = setTimeout(() => setShowOverlay(true), 120);
            return () => clearTimeout(timer);
        } else {
            setShowOverlay(false);
        }
    }, [isGenerating]);

    // Анимация во второй кадр через requestAnimationFrame
    useEffect(() => {
        if (showOverlay) {
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    setIsReady(true);
                    requestAnimationFrame(() => {
                        setIsVisible(true);
                    });
                });
            });
        } else {
            setIsReady(false);
            setIsVisible(false);
        }
    }, [showOverlay]);

    // Смена фраз каждые 2.5s (ускорено с 3s)
    useEffect(() => {
        if (!isVisible || adaptedPhrases.length === 0) return;

        const interval = setInterval(() => {
            setPhraseIndex(prev => (prev + 1) % adaptedPhrases.length);
        }, 2500);

        return () => clearInterval(interval);
    }, [isVisible, adaptedPhrases.length]);

    // Не показываем overlay если не начата генерация
    if (!showOverlay || !isGenerating) {
        return null;
    }

    return (
        <div
            className="fixed inset-0 z-[9999] transform-gpu"
            style={{
                opacity: isReady ? (isVisible ? 1 : 0) : 0,
                visibility: isReady ? (isVisible ? 'visible' : 'hidden') : 'hidden',
                willChange: 'opacity, transform',
                pointerEvents: isReady ? 'auto' : 'none'
            }}
        >
            {/* Gradient Flow Backdrop */}
            <motion.div
                className={`fixed inset-0 bg-gradient-to-br ${persona.color}
                    dark:from-[#0d0d0d] dark:via-[#1a1a1a] dark:to-[#222]
                    backdrop-blur-xl`}
                initial={{ opacity: 0 }}
                animate={{
                    opacity: isReady && isVisible ? 1 : 0,
                    backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
                }}
                exit={{ opacity: 0 }}
                transition={{
                    opacity: { duration: 0.4, ease: [0.23, 1, 0.32, 1] },
                    backgroundPosition: prefersReducedMotion ? {} : { duration: 8, repeat: Infinity, ease: 'linear' }
                }}
                style={{
                    willChange: 'opacity, background-position',
                    opacity: isReady ? undefined : 0,
                    backgroundSize: '200% 200%'
                }}
            />

            {/* Content Layer */}
            <motion.div
                className="fixed inset-0 flex flex-col items-center justify-center text-center px-6 transform-gpu"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{
                    opacity: isReady && isVisible ? 1 : 0,
                    scale: isReady && isVisible ? 1 : 0.98
                }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{
                    duration: 0.4,
                    ease: [0.23, 1, 0.32, 1],
                    delay: 0.1
                }}
                style={{
                    willChange: 'opacity, transform',
                    opacity: isReady ? undefined : 0
                }}
            >
                {/* AI Core - пульсирующий центр */}
                <motion.div
                    className="w-20 h-20 rounded-full bg-white/10 blur-xl mb-6 transform-gpu"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{
                        opacity: isReady && isVisible ? (prefersReducedMotion ? 0.8 : [0.6, 1, 0.6]) : 0,
                        scale: isReady && isVisible ? (prefersReducedMotion ? 1 : [0.98, 1.02, 0.98]) : 0.8
                    }}
                    transition={{
                        opacity: prefersReducedMotion ? {} : { duration: 3, repeat: Infinity, ease: 'easeInOut' },
                        scale: prefersReducedMotion ? {} : { duration: 3, repeat: Infinity, ease: 'easeInOut' }
                    }}
                    style={{ willChange: 'opacity, transform' }}
                />

                {/* Dynamic Title */}
                <motion.h2
                    initial={{ opacity: 0, y: 20 }}
                    animate={{
                        opacity: isReady && isVisible ? 1 : 0,
                        y: isReady && isVisible ? 0 : 20
                    }}
                    transition={{ duration: 0.6, delay: 0.3, ease: "easeOut" }}
                    className="text-2xl font-semibold text-white mb-3 drop-shadow-lg"
                    style={{ willChange: 'opacity, transform' }}
                >
                    AI думает в стиле "{safeStyle}"...
                </motion.h2>

                {/* Dynamic Phrases with improved animation */}
                <AnimatePresence mode="wait">
                    <motion.p
                        key={phraseIndex}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{
                            opacity: isReady && isVisible ? [0, 1, 1, 0] : 0,
                            y: isReady && isVisible ? [10, 0, 0, -10] : 10
                        }}
                        transition={{ duration: 2.4, ease: "easeInOut" }}
                        className="text-white/90 text-base max-w-md px-4 leading-relaxed mb-5"
                        style={{ willChange: 'opacity, transform' }}
                    >
                        {adaptedPhrases[phraseIndex] || adaptedPhrases[0] || "Генерирую дайджест..."}
                    </motion.p>
                </AnimatePresence>

                {/* Animated Progress Bar */}
                <motion.div
                    className="mt-4 h-1 w-3/4 bg-white/20 rounded-full overflow-hidden transform-gpu"
                    initial={{ opacity: 0, scaleX: 0 }}
                    animate={{
                        opacity: isReady && isVisible ? 1 : 0,
                        scaleX: isReady && isVisible ? 1 : 0
                    }}
                    transition={{
                        opacity: { duration: 0.6, delay: 0.45 },
                        scaleX: { duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1.0 }
                    }}
                    style={{ willChange: 'opacity, transform' }}
                >
                    <motion.div
                        className="h-full w-full bg-gradient-to-r from-white/70 via-white/40 to-white/80"
                        animate={isReady && isVisible ? {
                            x: ["-100%", "100%"],
                            opacity: [0.7, 1, 0.7]
                        } : { opacity: 0 }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: "easeInOut"
                        }}
                    />
                </motion.div>
            </motion.div>

            {/* Soft Particles - 6 плавающих точек */}
            {!prefersReducedMotion && (
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    {[...Array(6)].map((_, i) => (
                        <motion.div
                            key={i}
                            className="absolute w-2 h-2 rounded-full bg-white/20 transform-gpu"
                            style={{
                                left: `${20 + i * 12}%`,
                                top: `${30 + (i % 3) * 15}%`,
                                opacity: isReady && isVisible ? undefined : 0
                            }}
                            animate={isReady && isVisible ? {
                                y: [-10, 10, -10],
                                opacity: [0.2, 0.4, 0.2],
                            } : { opacity: 0 }}
                            transition={{
                                duration: 5 + Math.random() * 3,
                                repeat: Infinity,
                                ease: "easeInOut",
                                delay: i * 0.3,
                            }}
                        />
                    ))}
                </div>
            )}

            {/* Flare Flash - финальная вспышка */}
            <AnimatePresence>
                {showFlare && (
                    <motion.div
                        className="absolute inset-0 bg-white/60 rounded-full blur-3xl transform-gpu"
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: [0, 1, 0], scale: [0.8, 1.5, 2] }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.8, ease: 'easeOut' }}
                        style={{ willChange: 'opacity, transform' }}
                    />
                )}
            </AnimatePresence>
        </div>
    );
};

export default DigestMagicProgress;
