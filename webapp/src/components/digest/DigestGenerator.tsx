import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, Brain, Briefcase, Laugh, Calendar, Filter } from 'lucide-react';
import { DigestMagicProgress } from './DigestMagicProgress';

interface DigestGeneratorProps {
  isOpen: boolean;
  onClose: () => void;
  onGenerate: (category: string, style: string, period: string) => Promise<string>;
}

interface DigestData {
  styles: Record<string, string>;
  categories: Record<string, string>;
  periods: Record<string, string>;
}

const defaultData: DigestData = {
  styles: {
    analytical: "📰 Аналитический",
    business: "💼 Бизнес", 
    meme: "😂 Мемный"
  },
  categories: {
    crypto: "₿ Криптовалюты",
    sports: "⚽ Спорт",
    markets: "📈 Рынки",
    tech: "🤖 Технологии",
    world: "🌍 Мир"
  },
  periods: {
    today: "📅 Сегодня",
    "7d": "📅 7 дней",
    "30d": "📅 30 дней"
  }
};

export const DigestGenerator: React.FC<DigestGeneratorProps> = ({
  isOpen,
  onClose,
  onGenerate
}) => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedStyle, setSelectedStyle] = useState('analytical');
  const [selectedPeriod, setSelectedPeriod] = useState('today');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDigest, setGeneratedDigest] = useState<string>('');
  const [data, setData] = useState<DigestData>(defaultData);

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
            categories: { all: '🌐 Все категории', ...categoriesData.data.categories },
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
    
    try {
      const digest = await onGenerate(selectedCategory, selectedStyle, selectedPeriod);
      setGeneratedDigest(digest);
      
      // Автоматически закрываем модальное окно через 2 секунды после успешной генерации
      setTimeout(() => {
        handleClose();
      }, 2000);
      
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

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      >
        <motion.div
          className="w-full max-w-2xl max-h-[85vh] 
                     bg-white/95 dark:bg-surface-alt/95 
                     backdrop-blur-lg rounded-3xl 
                     shadow-[0_8px_32px_rgba(0,0,0,0.12)] 
                     p-6 overflow-hidden flex flex-col"
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 20 }}
          transition={{ duration: 0.25, ease: "easeOut" }}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Sparkles className="w-6 h-6 text-primary" />
              <h2 className="text-xl font-semibold text-text dark:text-white">
                Создать AI-дайджест
              </h2>
            </div>
            <button 
              className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              onClick={handleClose}
            >
              <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>
          </div>

          {generatedDigest ? (
            /* Generated Digest Display */
            <div className="flex-1 overflow-y-auto">
              <div className="mb-4 p-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl">
                <div className="flex items-center gap-2 text-green-700 dark:text-green-300">
                  <Sparkles className="w-5 h-5" />
                  <span className="font-medium">Дайджест успешно создан!</span>
                </div>
                <p className="text-green-600 dark:text-green-400 text-sm mt-1">
                  Дайджест сохранен в вашу коллекцию. Модальное окно закроется автоматически.
                </p>
              </div>
              
              <div className="prose prose-sm max-w-none dark:prose-invert">
                <div 
                  className="text-text dark:text-white leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: generatedDigest }}
                />
              </div>
              <div className="mt-6 flex gap-3">
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
            <div className="flex-1 overflow-y-auto space-y-6">
              {/* Category Selection */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-text dark:text-white mb-3">
                  <Filter className="w-4 h-4" />
                  Категория
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(data.categories).map(([key, label]) => (
                    <button
                      key={key}
                      className={`p-3 rounded-xl text-sm font-medium transition-all ${
                        selectedCategory === key
                          ? "bg-primary/10 text-primary border-2 border-primary/20"
                          : "bg-gray-100 dark:bg-gray-700 text-text dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600"
                      }`}
                      onClick={() => setSelectedCategory(key)}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Style Selection */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-text dark:text-white mb-3">
                  <Brain className="w-4 h-4" />
                  Стиль AI
                </label>
                <div className="grid grid-cols-1 gap-2">
                  {Object.entries(data.styles).map(([key, label]) => {
                    const icons = {
                      analytical: <Brain className="w-4 h-4" />,
                      business: <Briefcase className="w-4 h-4" />,
                      meme: <Laugh className="w-4 h-4" />
                    };
                    
                    return (
                      <button
                        key={key}
                        className={`p-3 rounded-xl text-sm font-medium transition-all flex items-center gap-3 ${
                          selectedStyle === key
                            ? "bg-primary/10 text-primary border-2 border-primary/20"
                            : "bg-gray-100 dark:bg-gray-700 text-text dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600"
                        }`}
                        onClick={() => setSelectedStyle(key)}
                      >
                        {icons[key as keyof typeof icons]}
                        {label}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Period Selection */}
              <div>
                <label className="flex items-center gap-2 text-sm font-medium text-text dark:text-white mb-3">
                  <Calendar className="w-4 h-4" />
                  Период
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {Object.entries(data.periods).map(([key, label]) => (
                    <button
                      key={key}
                      className={`p-3 rounded-xl text-sm font-medium transition-all ${
                        selectedPeriod === key
                          ? "bg-primary/10 text-primary border-2 border-primary/20"
                          : "bg-gray-100 dark:bg-gray-700 text-text dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600"
                      }`}
                      onClick={() => setSelectedPeriod(key)}
                    >
                      {label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Generate Button */}
              <button
                className="w-full bg-gradient-to-r from-primary to-primary/80 text-white py-4 px-6 rounded-xl font-semibold hover:from-primary/90 hover:to-primary/70 transition-all transform hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                onClick={handleGenerate}
                disabled={isGenerating}
              >
                {isGenerating ? (
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Генерирую...
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-2">
                    <Sparkles className="w-5 h-5" />
                    Создать дайджест
                  </div>
                )}
              </button>
            </div>
          )}
        </motion.div>

        {/* Magic Progress Overlay */}
        {isGenerating && (
          <DigestMagicProgress 
            style={selectedStyle as 'analytical' | 'business' | 'meme'}
            onComplete={() => setIsGenerating(false)}
          />
        )}
      </motion.div>
    </AnimatePresence>
  );
};

export default DigestGenerator;
