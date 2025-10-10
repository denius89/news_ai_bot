import { motion } from "framer-motion";
import { useEffect, useState } from "react";
import { Sparkles, Bot, Briefcase, Brain, Laugh, Newspaper, BookOpen, MessageCircle } from "lucide-react";

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
  }
};

interface DigestMagicProgressProps {
  style?: 'analytical' | 'business' | 'meme' | 'newsroom' | 'magazine' | 'casual';
  tone?: 'neutral' | 'insightful' | 'critical' | 'optimistic';
  length?: 'short' | 'medium' | 'long';
  onComplete?: () => void;
}

export const DigestMagicProgress: React.FC<DigestMagicProgressProps> = ({ 
  style = "analytical", 
  tone = "neutral",
  length = "medium",
  onComplete 
}) => {
  const persona = personalities[style] || personalities.analytical;
  
  // Адаптация фраз по тону
  const getPhrases = (style: string, tone?: string) => {
    const basePersona = personalities[style];
    
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
  
  const adaptedPhrases = getPhrases(style, tone);
  const [phrase, setPhrase] = useState(adaptedPhrases[0]);

  useEffect(() => {
    const interval = setInterval(() => {
      setPhrase(prev => {
        const currentIndex = adaptedPhrases.indexOf(prev);
        const nextIndex = (currentIndex + 1) % adaptedPhrases.length;
        return adaptedPhrases[nextIndex];
      });
    }, 3000);
    
    return () => clearInterval(interval);
  }, [adaptedPhrases]);

  // Динамическое время генерации
  const getGenerationTime = (length?: string) => {
    switch (length) {
      case 'short': return 10000; // 10 секунд
      case 'medium': return 15000; // 15 секунд
      case 'long': return 20000; // 20 секунд
      default: return 15000;
    }
  };

  // Auto-complete after some time (optional)
  useEffect(() => {
    if (onComplete) {
      const timer = setTimeout(() => {
        onComplete();
      }, getGenerationTime(length));
      
      return () => clearTimeout(timer);
    }
  }, [onComplete, length]);

  return (
    <motion.div 
      className={`fixed inset-0 flex flex-col items-center justify-center 
                  bg-gradient-to-br ${persona.color} 
                  dark:from-[#0d0d0d] dark:via-[#1a1a1a] dark:to-[#222] 
                  backdrop-blur-xl text-center z-50 px-6 transition-all`}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.5 }}
    >
      {/* Animated Icons */}
      <motion.div
        className="flex items-center justify-center mb-6"
        animate={{ rotate: 360 }}
        transition={{ repeat: Infinity, duration: 8, ease: "linear" }}
      >
        {persona.icon}
        <Bot className="w-10 h-10 text-white/80 mx-2" />
        <Sparkles className="w-10 h-10 text-white/70" />
      </motion.div>

      {/* Dynamic Title */}
      <motion.h2
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-2xl font-semibold text-white mb-3 drop-shadow-lg"
      >
        AI думает в стиле "{style}"...
      </motion.h2>

      {/* Dynamic Phrases */}
      <motion.p
        key={phrase}
        initial={{ opacity: 0, y: 5 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-white/90 text-base max-w-md px-4 leading-relaxed mb-5"
      >
        {phrase}
      </motion.p>

      {/* Animated Progress Bar */}
      <motion.div
        className="mt-4 h-1 w-3/4 bg-white/20 rounded-full overflow-hidden"
        initial={{ scaleX: 0 }}
        animate={{ scaleX: 1 }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
      >
        <motion.div 
          className="h-full w-full bg-gradient-to-r from-white/70 via-white/40 to-white/80"
          animate={{ 
            x: ["-100%", "100%"],
            opacity: [0.7, 1, 0.7]
          }}
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
            }}
            animate={{
              y: [-20, 20, -20],
              opacity: [0.3, 0.8, 0.3],
            }}
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
  );
};

export default DigestMagicProgress;
