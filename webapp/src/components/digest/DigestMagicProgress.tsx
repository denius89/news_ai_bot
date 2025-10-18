import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";
import { Sparkles, Bot, Briefcase, Brain, Laugh, Newspaper, BookOpen, MessageCircle, FileText, Cpu } from "lucide-react";

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
  style?: 'analytical' | 'business' | 'meme' | 'newsroom' | 'magazine' | 'casual' | 'explanatory' | 'technical';
  tone?: 'neutral' | 'insightful' | 'critical' | 'optimistic';
  length?: 'short' | 'medium' | 'long';
  onComplete?: () => void;
}

export const DigestMagicProgress: React.FC<DigestMagicProgressProps> = ({ 
  style = "analytical", 
  tone = "neutral"
  // length и onComplete больше не используются - полагаемся на реальное завершение
}) => {
  // Состояния для оптимизированной анимации
  const [showOverlay, setShowOverlay] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [isReady, setIsReady] = useState(false);
  
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
  const [phrase, setPhrase] = useState(adaptedPhrases[0] || "Генерирую дайджест...");

  // Оптимизированная задержка для показа overlay
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowOverlay(true);
    }, 120);

    return () => clearTimeout(timer);
  }, []);

  // Анимация во второй кадр через requestAnimationFrame с дополнительной защитой
  useEffect(() => {
    if (showOverlay) {
      // Двойной requestAnimationFrame для гарантии стабильности
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          // Помечаем как готовый к рендерингу во втором кадре
          setIsReady(true);
          
          // Анимация видимости в следующем кадре
          requestAnimationFrame(() => {
            setIsVisible(true);
          });
        });
      });
    }
  }, [showOverlay]);

  useEffect(() => {
    if (adaptedPhrases.length === 0) {
      return;
    }
    
    const interval = setInterval(() => {
      setPhrase((prev: string) => {
        const currentIndex = adaptedPhrases.indexOf(prev);
        const nextIndex = (currentIndex + 1) % adaptedPhrases.length;
        return adaptedPhrases[nextIndex] || adaptedPhrases[0] || "Генерирую дайджест...";
      });
    }, 3000);
    
    return () => clearInterval(interval);
  }, [adaptedPhrases]);

  // Убрали автотаймер и getGenerationTime - полагаемся только на реальное завершение генерации
  // Автотаймер может скрыть экран раньше времени, если генерация затягивается

  // Не показываем overlay если не прошло 120мс
  if (!showOverlay) {
    return null;
  }

  return (
    <div 
      className="fixed inset-0 z-50"
      style={{ 
        opacity: isReady ? (isVisible ? 1 : 0) : 0,
        visibility: isReady ? (isVisible ? 'visible' : 'hidden') : 'hidden',
        willChange: 'opacity, transform',
        pointerEvents: isReady ? 'auto' : 'none'
      }}
    >
      {/* Backdrop Layer - отдельно */}
      <motion.div
        className={`fixed inset-0 
                    bg-gradient-to-br ${persona.color} 
                    dark:from-[#0d0d0d] dark:via-[#1a1a1a] dark:to-[#222] 
                    backdrop-blur-xl`}
        initial={{ opacity: 0 }}
        animate={{ opacity: isReady && isVisible ? 1 : 0 }}
        exit={{ opacity: 0 }}
        transition={{ 
          duration: 0.4,
          ease: [0.23, 1, 0.32, 1]
        }}
        style={{ 
          willChange: 'opacity',
          opacity: isReady ? undefined : 0
        }}
      />
      
      {/* Content Layer - отдельно */}
      <motion.div 
        className="fixed inset-0 flex flex-col items-center justify-center text-center px-6"
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
      {/* Animated Icons */}
      <motion.div
        className="flex items-center justify-center mb-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ 
          opacity: isReady && isVisible ? 1 : 0, 
          y: isReady && isVisible ? 0 : 20,
          rotate: isReady && isVisible ? [0, 360, 720, 1080] : 0
        }}
        transition={{ 
          opacity: { duration: 0.6, delay: 0.15 },
          y: { duration: 0.6, delay: 0.15, ease: "easeOut" },
          rotate: { 
            duration: 8, 
            repeat: Infinity, 
            ease: "linear", 
            delay: isReady && isVisible ? 0.8 : 0,
            times: [0, 0.33, 0.66, 1]
          }
        }}
        style={{ 
          willChange: 'opacity, transform',
          opacity: isReady ? undefined : 0,
          transform: isReady ? undefined : 'translateY(20px)'
        }}
      >
        {persona.icon}
        <Bot className="w-10 h-10 text-white/80 mx-2" />
        <Sparkles className="w-10 h-10 text-white/70" />
      </motion.div>

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

      {/* Dynamic Phrases */}
      <motion.p
        key={phrase}
        initial={{ opacity: 0, y: 5 }}
        animate={{ 
          opacity: isReady && isVisible ? 1 : 0, 
          y: isReady && isVisible ? 0 : 5 
        }}
        transition={{ duration: 0.6 }}
        className="text-white/90 text-base max-w-md px-4 leading-relaxed mb-5"
        style={{ willChange: 'opacity, transform' }}
      >
        {phrase}
      </motion.p>

      {/* Animated Progress Bar */}
      <motion.div
        className="mt-4 h-1 w-3/4 bg-white/20 rounded-full overflow-hidden"
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

      {/* Floating Particles Effect */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white/30 rounded-full"
            style={{
              left: `${20 + i * 15}%`,
              top: `${30 + (i % 3) * 20}%`,
              opacity: isReady && isVisible ? undefined : 0
            }}
            animate={isReady && isVisible ? {
              y: [-20, 20, -20],
              opacity: [0.3, 0.8, 0.3],
            } : { opacity: 0 }}
            transition={{
              duration: 3 + i * 0.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.3,
            }}
          />
        ))}
      </div>
      </motion.div>
    </div>
  );
};

export default DigestMagicProgress;
