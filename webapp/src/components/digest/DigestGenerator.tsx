import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, Brain, Briefcase, Smile, CalendarDays, Filter, Globe2, Coins, TrendingUp, Trophy, Cpu } from 'lucide-react';
import { DigestMagicProgress } from './DigestMagicProgress';
import { cn } from '../../lib/utils';
import { useDrag } from '@use-gesture/react';
import { useUserPreferences } from '../../hooks/useUserPreferences';
import { initHoloMotion } from '../../utils/holoMotion';
import '../../styles/holographic.css';

interface DigestGeneratorProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (category: string, style: string, period: string) => Promise<string>;
  userId?: string; // Добавляем userId для сохранения предпочтений
}

interface DigestData {
  styles: Record<string, string>;
  categories: Record<string, string>;
  periods: Record<string, string>;
}

const defaultData: DigestData = {
  styles: {
    analytical: "Аналитический",
    business: "Бизнес", 
    meme: "Мемный"
  },
  categories: {
    all: "Все категории",
    crypto: "Криптовалюты",
    sports: "Спорт",
    markets: "Рынки",
    tech: "Технологии",
    world: "Мир"
  },
  periods: {
    today: "Сегодня",
    "7d": "7 дней",
    "30d": "30 дней"
  }
};

export const DigestGenerator: React.FC<DigestGeneratorProps> = ({
  isOpen,
  onClose,
  onGenerate,
  userId
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDigest, setGeneratedDigest] = useState<string>('');
  const [data, setData] = useState<DigestData>(defaultData);
  const [isDark, setIsDark] = useState(false);
  const [deviceOrientation, setDeviceOrientation] = useState({ alpha: 0, beta: 0, gamma: 0 });
  
  // Используем хук предпочтений пользователя
  const {
    preferences,
    isLoading: preferencesLoading,
    savePreferences,
    updateAfterDigestGeneration
  } = useUserPreferences(userId);

  // Состояния для выбранных значений (инициализируются из предпочтений)
  const [selectedCategory, setSelectedCategory] = useState(preferences.preferred_category);
  const [selectedStyle, setSelectedStyle] = useState(preferences.preferred_style);
  const [selectedPeriod, setSelectedPeriod] = useState(preferences.preferred_period);

  // Синхронизируем состояния с предпочтениями при их загрузке
  useEffect(() => {
    if (!preferencesLoading) {
      setSelectedCategory(preferences.preferred_category);
      setSelectedStyle(preferences.preferred_style);
      setSelectedPeriod(preferences.preferred_period);
    }
  }, [preferences, preferencesLoading]);

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
    if (!preferences.enable_haptic_feedback || !navigator.vibrate) return;
    
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
      if (!preferences.enable_gestures || isGenerating) return;
      
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
            periods: categoriesData.data.periods
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
    triggerHapticFeedback('heavy'); // Вибрация при запуске генерации
    
    try {
      const digest = await onGenerate(selectedCategory, selectedStyle, selectedPeriod);
      setGeneratedDigest(digest);
      
      // Сохраняем предпочтения после успешной генерации
      await updateAfterDigestGeneration(selectedCategory, selectedStyle, selectedPeriod);
      
      // Сразу закрываем модальное окно после успешной генерации
      handleClose();
      
    } catch (error) {
      console.error('Failed to generate digest:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleClose = () => {
    setSelectedCategory('all');
    setSelectedStyle('analytical');
    setSelectedPeriod('today');
    setGeneratedDigest('');
    setIsGenerating(false);
    onClose();
  };

  // ОБРАБОТЧИКИ С HAPTIC FEEDBACK И СОХРАНЕНИЕМ ПРЕДПОЧТЕНИЙ
  const handleCategorySelect = async (category: string) => {
    setSelectedCategory(category);
    triggerHapticFeedback('light');
    await savePreferences({ preferred_category: category });
  };

  const handleStyleSelect = async (style: string) => {
    setSelectedStyle(style);
    triggerHapticFeedback('medium');
    await savePreferences({ preferred_style: style });
  };

  const handlePeriodSelect = async (period: string) => {
    setSelectedPeriod(period);
    triggerHapticFeedback('light');
    await savePreferences({ preferred_period: period });
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
      
      <div className="fixed inset-0 flex items-center justify-center z-50 p-4 pb-20">
        <motion.div
          initial={{ y: 60, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
          transition={{ type: "spring", stiffness: 140, damping: 18 }}
          className={cn(
            "relative z-50 max-w-md mx-auto rounded-3xl p-6 pb-8 backdrop-blur-2xl border",
            isDark
              ? "bg-gradient-to-b from-[#0b0f10]/90 via-[#0f1416]/90 to-[#12181a]/90 border-gray-800 shadow-[0_0_20px_rgba(0,0,0,0.6)]"
              : "bg-gradient-to-b from-white/95 via-white/90 to-[#f8f9fa]/95 border-white/60 shadow-[0_4px_35px_rgba(0,0,0,0.08)]"
          )}
        >

          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex flex-col">
              <h2 className={cn(
                "text-[18px] font-semibold flex items-center gap-2",
                isDark ? "text-gray-100" : "text-gray-900"
              )}>
                <Sparkles className="text-emerald-500 w-5 h-5 animate-pulse-sparkle" />
                Создать AI-дайджест
              </h2>
              <p className={cn(
                "text-[14px] mt-1",
                isDark ? "text-gray-400" : "text-gray-500"
              )}>
                AI отберёт лучшее и соберёт персональный дайджест.
              </p>
            </div>
            <button 
              className="p-2 rounded-full hover:bg-gray-100/50 dark:hover:bg-gray-700/50 transition-colors flex-shrink-0"
              onClick={handleClose}
            >
              <X className="w-4 h-4 text-gray-500 dark:text-gray-400" />
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
            <div className="flex-1 overflow-y-auto space-y-5">
              {/* Category Selection */}
              <div {...categoryBind()}>
                <h3 className={cn(
                  "text-[14px] font-medium flex items-center gap-2 mb-3",
                  isDark ? "text-gray-300" : "text-gray-700"
                )}>
                  <Filter className="w-4 h-4 text-gray-400" /> 
                  Категория 
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(data.categories).map(([key, label]) => {
                    const getIcon = (categoryKey: string) => {
                      switch (categoryKey) {
                        case 'all': return <Globe2 className="w-4 h-4 text-emerald-500" />;
                        case 'crypto': return <Coins className="w-4 h-4 text-emerald-500" />;
                        case 'markets': return <TrendingUp className="w-4 h-4 text-emerald-500" />;
                        case 'sports': return <Trophy className="w-4 h-4 text-emerald-500" />;
                        case 'tech': return <Cpu className="w-4 h-4 text-emerald-500" />;
                        case 'world': return <Globe2 className="w-4 h-4 text-emerald-500" />;
                        default: return <Globe2 className="w-4 h-4 text-emerald-500" />;
                      }
                    };
                    
                    return (
                      <motion.button
                        key={key}
                        whileHover={{ scale: 1.03 }}
                        whileTap={{ scale: 0.97 }}
                        className={cn(
                          "flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-sm font-medium border transition-all duration-300",
                          selectedCategory === key
                            ? isDark
                              ? "border-emerald-400/30 bg-emerald-950/40 text-emerald-300 shadow-[0_0_8px_rgba(16,185,129,0.1)]"
                              : "border-emerald-400/40 bg-emerald-50 text-emerald-600 shadow-[0_0_8px_rgba(16,185,129,0.1)]"
                            : isDark
                              ? "border-gray-800 bg-[#1a1e20]/80 text-gray-300 hover:border-gray-700"
                              : "border-gray-200 bg-white hover:border-gray-300 text-gray-600"
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

              {/* Style Selection */}
              <div>
                <h3 className={cn(
                  "text-[14px] font-medium flex items-center gap-2 mb-3",
                  isDark ? "text-gray-300" : "text-gray-700"
                )}>
                  <Brain className="w-4 h-4 text-gray-400" /> 
                  Стиль AI
                </h3>
                <div className="grid grid-cols-3 gap-2">
                  {Object.entries(data.styles).map(([key, label]) => {
                    const icons = {
                      analytical: <Brain className="w-4 h-4" />,
                      business: <Briefcase className="w-4 h-4" />,
                      meme: <Smile className="w-4 h-4" />
                    };
                    
                    
                    return (
                      <motion.button
                        key={key}
                        whileHover={{ scale: 1.03 }}
                        whileTap={{ scale: 0.97 }}
                        className={cn(
                          "flex flex-col items-center gap-1 px-2 py-3 rounded-xl text-xs font-medium transition-all duration-300 relative overflow-hidden",
                          selectedStyle === key
                            ? isDark
                              ? `border-2 ${
                                  key === 'analytical' ? 'border-blue-400/60 bg-blue-950/30 text-blue-300' :
                                  key === 'business' ? 'border-amber-400/60 bg-amber-950/30 text-amber-300' :
                                  'border-pink-400/60 bg-pink-950/30 text-pink-300'
                                } shadow-[0_0_20px_rgba(59,130,246,0.3)]`
                              : `border-2 ${
                                  key === 'analytical' ? 'border-blue-400/60 bg-blue-50 text-blue-600' :
                                  key === 'business' ? 'border-amber-400/60 bg-amber-50 text-amber-600' :
                                  'border-pink-400/60 bg-pink-50 text-pink-600'
                                } shadow-[0_0_20px_rgba(59,130,246,0.2)]`
                            : isDark
                              ? "border border-gray-700 bg-[#1a1e20]/80 text-gray-300 hover:border-gray-600"
                              : "border border-gray-200 bg-white hover:border-gray-300 text-gray-600"
                        )}
                        onClick={() => handleStyleSelect(key)}
                      >
                        {/* Gradient shimmer effect for selected style */}
                        {selectedStyle === key && (
                          <div className={cn(
                            "absolute inset-0 rounded-xl bg-gradient-to-r opacity-20 animate-shimmer",
                            key === 'analytical' && "from-blue-400 via-cyan-400 to-teal-300",
                            key === 'business' && "from-amber-400 via-orange-400 to-yellow-400",
                            key === 'meme' && "from-pink-400 via-fuchsia-400 to-rose-400"
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
                  "text-[14px] font-medium flex items-center gap-2 mb-3",
                  isDark ? "text-gray-300" : "text-gray-700"
                )}>
                  <CalendarDays className="w-4 h-4 text-gray-400" /> Период
                </h3>
                <div className="grid grid-cols-3 gap-2">
                  {Object.entries(data.periods).map(([key, label]) => (
                    <motion.button
                      key={key}
                      whileHover={{ scale: 1.03 }}
                      whileTap={{ scale: 0.97 }}
                      className={cn(
                        "px-3 py-2 rounded-xl text-sm font-medium transition-all duration-300 border",
                        selectedPeriod === key
                          ? isDark
                            ? "bg-emerald-900/40 border border-emerald-400/40 text-emerald-300 shadow-[0_0_6px_rgba(16,185,129,0.2)]"
                            : "bg-emerald-50 border border-emerald-400/40 text-emerald-700 shadow-[0_0_6px_rgba(16,185,129,0.1)]"
                          : isDark
                            ? "bg-[#1a1e20] border border-gray-800 text-gray-400 hover:border-gray-700"
                            : "bg-white border border-gray-200 text-gray-600 hover:border-gray-300"
                      )}
                      onClick={() => handlePeriodSelect(key)}
                    >
                      {label}
                    </motion.button>
                  ))}
                </div>
              </div>

              {/* Generate Button with Holographic Effect */}
              <div className="mt-8">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.96 }}
                  transition={{ type: "spring", stiffness: 220, damping: 18 }}
                  className="holo-button holo-surface w-full py-3.5 text-[15px] font-semibold"
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
                  "text-xs text-center mt-2",
                  isDark ? "text-gray-500" : "text-gray-400"
                )}>
                  Готовлю дайджест как личный аналитик. Это займёт пару секунд.
                </p>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Magic Progress Overlay */}
      {isGenerating && (
        <DigestMagicProgress 
          style={selectedStyle as 'analytical' | 'business' | 'meme'}
          onComplete={() => setIsGenerating(false)}
        />
      )}
    </AnimatePresence>
  );
};

export default DigestGenerator;
