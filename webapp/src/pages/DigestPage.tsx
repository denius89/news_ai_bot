import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Header } from '../components/ui/Header';
import { DigestGenerator } from '../components/digest/DigestGenerator';
import { DigestMagicProgress } from '../components/digest/DigestMagicProgress';
import { Bot, Sparkles, Filter, Trash2, Archive, RotateCcw, Eye, ExternalLink, X, Bitcoin, LineChart, Trophy, Cpu, Globe2, CalendarDays, Newspaper, BookOpen, MessageCircle, ThumbsUp, ThumbsDown, ArrowUp, FileText, Settings } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useTelegramUser } from '../hooks/useTelegramUser';

interface DigestItem {
  id: string;
  title?: string;
  summary: string;
  category: string;
  sources?: string[];
  createdAt: string;
  readTime?: number;
  keyPoints?: string[];
  content?: string;
  style?: string;
  period?: string;
  limit?: number;
  preview?: string;
  user_id?: string;
  feedback_score?: number | null; // 0.0 = палец вниз, 1.0 = палец вверх, null = нет отзыва
  metadata?: {
    category: string;
    style: string;
    period: string;
    style_name: string;
    category_name: string;
  };
}

interface DigestPageProps {
  theme: 'light' | 'dark';
  onThemeToggle: () => void;
}

const DigestPage: React.FC<DigestPageProps> = () => {
  const [digests, setDigests] = useState<DigestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isGeneratorOpen, setIsGeneratorOpen] = useState(false);
  const [categories, setCategories] = useState<Record<string, string>>({});
  const [styles, setStyles] = useState<Record<string, string>>({});
  const [activeTab, setActiveTab] = useState<'active' | 'archived' | 'deleted'>('active');
  const [deletedDigests, setDeletedDigests] = useState<DigestItem[]>([]);
  const [archivedDigests, setArchivedDigests] = useState<DigestItem[]>([]);
  const [notification, setNotification] = useState<{type: 'success' | 'error', message: string} | null>(null);
  const [selectedDigest, setSelectedDigest] = useState<DigestItem | null>(null);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState<Record<string, 'up' | 'down'>>({});
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [isGeneratingDigest, setIsGeneratingDigest] = useState(false);
  const [generatingStyle, setGeneratingStyle] = useState<'analytical' | 'business' | 'meme' | 'newsroom' | 'magazine' | 'casual' | 'explanatory' | 'technical'>('analytical');
  
  // 🚀 Гибридный подход: useTelegramUser для UI, useAuth для API
  const { userData } = useTelegramUser();
  const { authHeaders } = useAuth();
  const userId = userData?.user_id;

  // Функция для показа уведомлений
  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 3000);
  };

  // Функция для отправки feedback
  const handleFeedback = async (digestId: string, score: number) => {
    // Проверяем, не отправлен ли уже отзыв для этого дайджеста
    if (feedbackSubmitted[digestId]) {
      showNotification('error', 'Отзыв уже отправлен');
      return;
    }

    try {
      const response = await fetch('/api/feedback', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...authHeaders
        },
        body: JSON.stringify({ digest_id: digestId, score })
      });
      
      if (response.ok) {
        // Сохраняем тип отзыва (палец вверх или вниз)
        const feedbackType = score === 1 ? 'up' : 'down';
        setFeedbackSubmitted(prev => ({ ...prev, [digestId]: feedbackType }));
        showNotification('success', 'Спасибо за отзыв!');
      } else {
        const errorData = await response.json();
        showNotification('error', errorData.message || 'Ошибка отправки отзыва');
      }
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      showNotification('error', 'Ошибка отправки отзыва');
    }
  };

  // Load categories and styles from API
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await fetch('/api/digests/categories');
        const data = await response.json();
        if (data.status === 'success') {
          setCategories({ all: 'Все категории', ...data.data.categories });
        }
      } catch (error) {
        console.warn('Failed to load categories, using defaults:', error);
        setCategories({
          all: 'Все категории',
          crypto: 'Криптовалюты',
          sports: 'Спорт',
          markets: 'Рынки',
          tech: 'Технологии',
          world: 'Мир'
        });
      }
    };

    const loadStyles = async () => {
      try {
        const response = await fetch('/api/digests/styles');
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'success' && data.data?.styles) {
            setStyles({ ...data.data.styles });
            return;
          }
        }
        console.warn('API response not successful, using defaults');
      } catch (error) {
        console.warn('Failed to load styles, using defaults:', error);
      }
      
      // Fallback styles
      setStyles({
        newsroom: "Newsroom",
        analytical: "Аналитический",
        magazine: "Magazine", 
        casual: "Простой",
        business: "Бизнес",
        explanatory: "Объясняющий",
        technical: "Технический",
        meme: "Мемный"
      });
    };
    
    loadCategories();
    loadStyles();
  }, []);

  // Load digest history from API
  const loadDigestHistory = async () => {
    try {
      // 🚀 Используем автоматически полученный user_id из Telegram WebApp
      if (!userId) {
        console.warn('⚠️ User ID not available yet, skipping digest history load');
        return;
      }
      
      console.log('🔄 Loading digest history for user:', userId);
      
      // Заголовки для аутентификации уже установлены в AuthContext
      
      // Загружаем активные дайджесты (не удаленные и не архивированные)
      const activeResponse = await fetch(`/api/digests/history?limit=10&include_deleted=false&include_archived=false`, {
        headers: authHeaders
      });
      const activeData = await activeResponse.json();
      console.log('📋 Active digests response:', activeData);
      
      // Загружаем архивированные дайджесты
      const archivedResponse = await fetch(`/api/digests/history?limit=10&include_deleted=false&include_archived=true`, {
        headers: authHeaders
      });
      const archivedData = await archivedResponse.json();
      
      // Загружаем удаленные дайджесты
      const deletedResponse = await fetch(`/api/digests/history?limit=10&include_deleted=true&include_archived=false`, {
        headers: authHeaders
      });
      const deletedData = await deletedResponse.json();
      
      const processDigests = (digestsData: any[]) => digestsData.map((digest: any) => ({
        id: digest.id,
        summary: digest.summary,
        category: digest.category,
        createdAt: digest.created_at,
        style: digest.style,
        period: digest.period,
        limit: digest.limit,
        preview: digest.preview,
        content: digest.summary,
        feedback_score: digest.feedback_score, // Добавляем поле отзыва
        readTime: Math.ceil(digest.summary.length / 1000), // Примерное время чтения
        sources: ['AI Generated'],
        keyPoints: []
      }));
      
      if (activeData.status === 'success') {
        const historyDigests = processDigests(activeData.data.digests);
        setDigests(historyDigests); // Используем только реальные данные
        
        // Построить мапу отзывов из активных дайджестов
        const feedbackMap: Record<string, 'up' | 'down'> = {};
        historyDigests.forEach(digest => {
          if (digest.feedback_score === 1.0) {
            feedbackMap[digest.id] = 'up';
          } else if (digest.feedback_score === 0.0) {
            feedbackMap[digest.id] = 'down';
          }
        });
        setFeedbackSubmitted(prev => ({ ...prev, ...feedbackMap }));
      } else {
        console.warn('⚠️ Не удалось загрузить активные дайджесты:', activeData.message);
        setDigests([]);
      }
      
      if (archivedData.status === 'success') {
        const archivedHistoryDigests = processDigests(archivedData.data.digests);
        console.log('📦 Loaded ARCHIVED digests:', archivedHistoryDigests.length, archivedHistoryDigests.map(d => d.id.substring(0, 8)));
        setArchivedDigests(archivedHistoryDigests);
        
        // Добавить отзывы из архивированных дайджестов
        const archivedFeedbackMap: Record<string, 'up' | 'down'> = {};
        archivedHistoryDigests.forEach(digest => {
          if (digest.feedback_score === 1.0) {
            archivedFeedbackMap[digest.id] = 'up';
          } else if (digest.feedback_score === 0.0) {
            archivedFeedbackMap[digest.id] = 'down';
          }
        });
        setFeedbackSubmitted(prev => ({ ...prev, ...archivedFeedbackMap }));
      } else {
        console.warn('⚠️ Не удалось загрузить архивированные дайджесты:', archivedData.message);
        setArchivedDigests([]);
      }
      
      if (deletedData.status === 'success') {
        const deletedHistoryDigests = processDigests(deletedData.data.digests);
        console.log('🗑️  Loaded DELETED digests:', deletedHistoryDigests.length, deletedHistoryDigests.map(d => d.id.substring(0, 8)));
        setDeletedDigests(deletedHistoryDigests);
        
        // Добавить отзывы из удаленных дайджестов
        const deletedFeedbackMap: Record<string, 'up' | 'down'> = {};
        deletedHistoryDigests.forEach(digest => {
          if (digest.feedback_score === 1.0) {
            deletedFeedbackMap[digest.id] = 'up';
          } else if (digest.feedback_score === 0.0) {
            deletedFeedbackMap[digest.id] = 'down';
          }
        });
        setFeedbackSubmitted(prev => ({ ...prev, ...deletedFeedbackMap }));
      } else {
        console.warn('⚠️ Не удалось загрузить удаленные дайджесты:', deletedData.message);
        setDeletedDigests([]);
      }
      
    } catch (error) {
      console.error('❌ Ошибка загрузки истории дайджестов:', error);
      // Устанавливаем пустые массивы при ошибке
      setDigests([]);
      setArchivedDigests([]);
      setDeletedDigests([]);
    }
  };

  // Load digest history on component mount
  // Load digest history when userId is available
  useEffect(() => {
    if (userId) {
      loadDigestHistory();
    }
  }, [userId]);

  // Scroll detection for "scroll to top" button
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      setShowScrollTop(scrollTop > 300);
    };

    let timeoutId: NodeJS.Timeout;
    const throttledHandleScroll = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(handleScroll, 100);
    };

    window.addEventListener('scroll', throttledHandleScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', throttledHandleScroll);
      clearTimeout(timeoutId);
    };
  }, []);

  // Scroll to top function
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Soft delete digest function
  const softDeleteDigest = async (digestId: string) => {
    if (!userId) {
      console.error('❌ User ID not available for delete operation');
      return;
    }
    
    try {
      const response = await fetch(`/api/digests/${digestId}?user_id=${userId}`, {
        method: 'DELETE',
        headers: authHeaders
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        // Обновляем списки
        setDigests(prev => prev.filter(d => d.id !== digestId));
        setArchivedDigests(prev => prev.filter(d => d.id !== digestId));
        // Показываем уведомление
        showNotification('success', 'Дайджест удален');
        // Перезагружаем историю для обновления удаленных
        setTimeout(() => loadDigestHistory(), 500);
      } else {
        console.error('Failed to delete digest:', data.message);
        showNotification('error', `Ошибка удаления: ${data.message}`);
      }
    } catch (error) {
      console.error('Error deleting digest:', error);
    }
  };

  // Restore digest function
  const restoreDigest = async (digestId: string) => {
    if (!userId) {
      console.error('❌ User ID not available for restore operation');
      return;
    }
    
    try {
      const response = await fetch(`/api/digests/${digestId}/restore?user_id=${userId}`, {
        method: 'POST',
        headers: authHeaders
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        // Показываем уведомление
        showNotification('success', 'Дайджест восстановлен');
        // Перезагружаем историю (без локального обновления)
        setTimeout(() => loadDigestHistory(), 500);
      } else {
        console.error('Failed to restore digest:', data.message);
        showNotification('error', `Ошибка восстановления: ${data.message}`);
      }
    } catch (error) {
      console.error('Error restoring digest:', error);
    }
  };

  // Archive digest function
  const archiveDigest = async (digestId: string) => {
    if (!userId) {
      console.error('❌ User ID not available for archive operation');
      return;
    }
    
    try {
      const response = await fetch(`/api/digests/${digestId}/archive?user_id=${userId}`, {
        method: 'POST',
        headers: authHeaders
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        // Обновляем списки
        setDigests(prev => prev.filter(d => d.id !== digestId));
        // Показываем уведомление
        showNotification('success', 'Дайджест скрыт в архив');
        // Перезагружаем историю для обновления архивированных
        setTimeout(() => loadDigestHistory(), 500);
      } else {
        console.error('Failed to archive digest:', data.message);
        showNotification('error', `Ошибка архивирования: ${data.message}`);
      }
    } catch (error) {
      console.error('Error archiving digest:', error);
    }
  };

  // Unarchive digest function
  const unarchiveDigest = async (digestId: string) => {
    if (!userId) {
      console.error('❌ User ID not available for unarchive operation');
      return;
    }
    
    try {
      const response = await fetch(`/api/digests/${digestId}/unarchive?user_id=${userId}`, {
        method: 'POST',
        headers: authHeaders
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        // Обновляем списки
        setArchivedDigests(prev => prev.filter(d => d.id !== digestId));
        // Показываем уведомление
        showNotification('success', 'Дайджест восстановлен из архива');
        // Перезагружаем историю
        setTimeout(() => loadDigestHistory(), 500);
      } else {
        console.error('Failed to unarchive digest:', data.message);
        showNotification('error', `Ошибка восстановления: ${data.message}`);
      }
    } catch (error) {
      console.error('Error unarchiving digest:', error);
    }
  };

  // Generate digest function
  const generateDigest = async (category: string, style: string, period: string, length: string, subcategory?: string | null): Promise<string> => {
    try {
      // Устанавливаем состояние загрузки
      console.log('🔄 Starting digest generation, setting isLoading=true');
      setIsGeneratingDigest(true);
      setGeneratingStyle(style as 'analytical' | 'business' | 'meme' | 'newsroom' | 'magazine' | 'casual' | 'explanatory' | 'technical');
      
      // 🚀 Используем автоматически полученный user_id из Telegram WebApp
      if (!userId) {
        throw new Error('User ID not available. Please ensure you are logged in.');
      }
      
      console.log('🔍 Generating digest with userId:', userId);
      
      // Генерация дайджеста
      
      const response = await fetch('/api/digests/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...authHeaders,
        },
        body: JSON.stringify({
          category,
          subcategory,
          style,
          period,
          length,
          limit: 10,
          user_id: userId,
          save: true,
          use_user_preferences: true,  // Использовать предпочтения пользователя для фильтрации
          // Новые AI возможности
          use_multistage: false,  // Multi-stage генерация (пока отключено для UI по умолчанию)
          use_rag: true,  // RAG система с примерами (включено)
          use_personalization: true,  // Персонализация (включена)
          audience: "general"  // Тип аудитории
        })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.message || errorMessage;
        } catch {
          // Если не удалось парсить JSON, используем заголовок
        }
        
        throw new Error(errorMessage);
      }
      
      const data = await response.json();
      console.log('🔍 API Response:', data);
      
      if (data.status === 'success') {
        
        // Показываем уведомление об успешной генерации
        showNotification('success', 'Дайджест успешно создан');
        
        // Перезагружаем историю для обновления списка (без дублирования)
        console.log('🔍 Checking if digest was saved:', {
          saved: data.data.saved,
          digest_id: data.data.digest_id,
          user_id: userId
        });
        
        if (data.data.saved) {
          console.log('📄 Digest saved, reloading history...');
          // Убеждаемся, что модалка просмотра закрыта перед обновлением списка
          setSelectedDigest(null);
          // Убираем задержку для более быстрого обновления UI
          setTimeout(() => loadDigestHistory(), 500);
        } else {
          console.log('⚠️ Digest not saved, but trying to reload history anyway', {
            reason: 'data.data.saved is false',
            digest_id: data.data.digest_id
          });
          // Попробуем перезагрузить историю даже если saved=false
          // Возможно, дайджест сохранился, но флаг не установился корректно
          setSelectedDigest(null);
          setTimeout(() => loadDigestHistory(), 1000);
        }
        
        return data.data.digest;
      } else {
        const errorMessage = data.message || 'Failed to generate digest';
        showNotification('error', `Ошибка генерации: ${errorMessage}`);
        throw new Error(errorMessage);
      }
    } catch (error) {
      console.error('Error generating digest:', error);
      showNotification('error', `Ошибка генерации: ${error instanceof Error ? error.message : 'Неизвестная ошибка'}`);
      throw error;
    } finally {
      // Сбрасываем состояние загрузки
      console.log('✅ Digest generation completed, setting isLoading=false');
      setIsGeneratingDigest(false);
    }
  };

  useEffect(() => {
    // Load any existing digests from localStorage or API
      setLoading(false);
  }, []);

  // Get current digests based on active tab
  // Show loading state while user is being authenticated

  const getCurrentDigests = () => {
    switch (activeTab) {
      case 'active':
        console.log('📋 Showing ACTIVE digests:', digests.length);
        return digests;
      case 'archived':
        console.log('📦 Showing ARCHIVED digests:', archivedDigests.length);
        return archivedDigests;
      case 'deleted':
        console.log('🗑️  Showing DELETED digests:', deletedDigests.length);
        return deletedDigests;
      default:
        return digests;
    }
  };

  const currentDigests = getCurrentDigests();
  const filteredDigests = currentDigests.filter(item => 
    selectedCategory === 'all' || item.category === selectedCategory
  );

  // Утилиты для отображения
  const truncateText = (text: string, maxLength: number = 200): string => {
    if (text.length <= maxLength) {
      return text;
    }
    return text.substring(0, maxLength).trim() + '...';
  };



  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
      opacity: 1,
      y: 0,
      transition: {
        duration: 0.5,
        ease: "easeOut" as const,
      },
    },
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-bg">
        <Header 
          title="AI Дайджест" 
          subtitle="Загрузка..." 
          icon={<Sparkles className="w-6 h-6 text-primary" />}
        />
        <main className="container-main">
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <Card key={i} className="animate-pulse">
                <CardHeader>
                  <div className="h-4 bg-surface-alt rounded w-3/4"></div>
                  <div className="h-3 bg-surface-alt rounded w-1/2"></div>
                </CardHeader>
                <CardContent>
                  <div className="h-3 bg-surface-alt rounded w-full mb-2"></div>
                  <div className="h-3 bg-surface-alt rounded w-2/3"></div>
                </CardContent>
              </Card>
            ))}
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-bg">
      {/* Уведомления */}
      {notification && (
        <div className={`fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg ${
          notification.type === 'success' 
            ? 'bg-green-500 dark:bg-green-600 text-white' 
            : 'bg-red-500 dark:bg-red-600 text-white'
        }`}>
          {notification.message}
        </div>
      )}
      
      <Header 
        title="AI Дайджест" 
        subtitle="Ваши персональные дайджесты"
        icon={<Sparkles className="w-6 h-6 text-primary" />}
        actions={
          activeTab === 'active' && (
            <motion.button
              whileTap={{ scale: 0.95 }}
              onClick={() => {
                setSelectedDigest(null);
                setIsGeneratorOpen(true);
              }}
              className="px-3 py-1.5 rounded-lg font-medium text-xs text-white
                         bg-ai-flow hover:shadow-[0_0_8px_rgba(0,166,200,0.3)] 
                         active:scale-95 transition-all duration-200 flex items-center gap-1.5"
            >
              <Sparkles className="w-3.5 h-3.5" />
              Создать
            </motion.button>
          )
        }
      />
      
      <main className="container-main pb-32">
        {/* Фильтры и вкладки */}
        <div className="flex space-x-1 mb-6 bg-surface-alt/50 rounded-xl p-1">
          <motion.button
            layout
            whileTap={{ scale: 0.97 }}
            transition={{ type: "spring", stiffness: 250, damping: 20 }}
            onClick={() => setActiveTab('active')}
            className={`flex-1 px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
              activeTab === 'active'
                ? "bg-ai-flow text-white shadow-[0_0_12px_rgba(0,166,200,0.3)]"
                : "text-muted hover:bg-surface-alt/50"
            }`}
          >
            <Eye className="w-4 h-4 inline mr-2" />
            Активные
          </motion.button>
          <motion.button
            layout
            whileTap={{ scale: 0.97 }}
            transition={{ type: "spring", stiffness: 250, damping: 20 }}
            onClick={() => setActiveTab('archived')}
            className={`flex-1 px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
              activeTab === 'archived'
                ? "bg-ai-flow text-white shadow-[0_0_12px_rgba(0,166,200,0.3)]"
                : "text-muted hover:bg-surface-alt/50"
            }`}
          >
            <Archive className="w-4 h-4 inline mr-2" />
            Архив
          </motion.button>
          <motion.button
            layout
            whileTap={{ scale: 0.97 }}
            transition={{ type: "spring", stiffness: 250, damping: 20 }}
            onClick={() => setActiveTab('deleted')}
            className={`flex-1 px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
              activeTab === 'deleted'
                ? "bg-ai-flow text-white shadow-[0_0_12px_rgba(0,166,200,0.3)]"
                : "text-muted hover:bg-surface-alt/50"
            }`}
          >
            <Trash2 className="w-4 h-4 inline mr-2" />
            Корзина
          </motion.button>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {/* Категории */}
          <motion.section variants={itemVariants}>
            <div className="flex flex-wrap justify-center gap-x-2 gap-y-3 mt-4">
              {Object.entries(categories).map(([key, label]) => {
                const getIcon = (categoryKey: string) => {
                  switch (categoryKey) {
                    case 'all': return <Filter className="w-4 h-4" />;
                    case 'crypto': return <Bitcoin className="w-4 h-4" />;
                    case 'markets': return <LineChart className="w-4 h-4" />;
                    case 'sports': return <Trophy className="w-4 h-4" />;
                    case 'tech': return <Cpu className="w-4 h-4" />;
                    case 'world': return <Globe2 className="w-4 h-4" />;
                    default: return <Filter className="w-4 h-4" />;
                  }
                };
                
                return (
                  <motion.button
                    key={key}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => setSelectedCategory(key)}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 flex items-center gap-2 ${
                      selectedCategory === key
                        ? "bg-ai-flow text-white shadow-[0_0_12px_rgba(0,166,200,0.3)]"
                        : "bg-surface-alt text-muted hover:bg-surfaceAlt"
                    }`}
                  >
                    {getIcon(key)}
                    {label}
                  </motion.button>
                );
              })}
                </div>
          </motion.section>

          {/* Digest List */}
          <motion.section variants={itemVariants}>
            <div className="space-y-4">
              {filteredDigests.map((digest, index) => (
                <motion.div
                  key={digest.id}
                  variants={itemVariants}
                  transition={{ delay: index * 0.1 }}
                >
                  <motion.div
                    className="card backdrop-blur-md border border-border 
                               rounded-3xl p-5 pb-6 shadow-[0_6px_20px_rgba(0,0,0,0.05)] 
                               hover:scale-[1.02] transition-transform duration-300 ease-out mt-4"
                    whileHover={{ scale: 1.02 }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  >
                    {/* Заголовок - извлекаем заголовок из HTML или используем первые слова */}
                    <h3 className="text-[15px] font-semibold text-text leading-snug">
                      {(() => {
                        // Пытаемся извлечь заголовок из HTML (например, <h1>, <h2>, <b>)
                        const htmlText = digest.summary;
                        const titleMatch = htmlText.match(/<(h[1-6]|b|strong)>(.*?)<\/(h[1-6]|b|strong)>/i);
                        if (titleMatch && titleMatch[2]) {
                          return truncateText(titleMatch[2].replace(/<[^>]*>/g, ''), 80);
                        }
                        // Если нет HTML тегов, берем первые слова до точки
                        const firstSentence = htmlText.split('.')[0];
                        return truncateText(firstSentence.replace(/<[^>]*>/g, ''), 80);
                      })()}
                    </h3>

                    {/* Бейджи в одну строку */}
                    <div className="flex items-center gap-2 flex-wrap mt-2">
                      <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400">
                        {categories[digest.category] || digest.category}
                      </span>
                      <span className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400">
                        {styles[digest.style || ''] || digest.metadata?.style_name || digest.style}
                      </span>
                      <span className="text-xs text-muted">
                        {new Date(digest.createdAt).toLocaleDateString('ru-RU')}
                      </span>
                    </div>

                    {/* Preview с HTML-рендерингом */}
                    <div 
                      className="mt-3 text-[14px] text-text leading-relaxed line-clamp-3"
                      dangerouslySetInnerHTML={{ 
                        __html: truncateText(digest.summary, 200) 
                      }}
                    />

                    <div className="mt-4 flex justify-between items-center text-sm">
                      <span className="text-muted">{digest.sources?.join(', ') || 'AI Generated'}</span>
                      <div className="flex items-center gap-2">
                        {/* Feedback buttons - only for active tab */}
                        {activeTab === 'active' && (
                          <>
                            <button 
                              className={`p-1.5 rounded-lg transition-colors ${
                                feedbackSubmitted[digest.id] === 'up'
                                  ? 'text-green-600 bg-green-50 dark:bg-green-900/20'
                                  : feedbackSubmitted[digest.id] === 'down'
                                  ? 'text-muted cursor-not-allowed'
                                  : 'text-muted hover:text-success hover:bg-green-50 dark:hover:bg-green-900/20'
                              }`}
                              onClick={() => handleFeedback(digest.id, 1.0)}
                              title={feedbackSubmitted[digest.id] ? "Отзыв уже отправлен" : "Понравилось"}
                              disabled={!!feedbackSubmitted[digest.id]}
                            >
                              <ThumbsUp className="w-4 h-4" />
                            </button>
                            <button 
                              className={`p-1.5 rounded-lg transition-colors ${
                                feedbackSubmitted[digest.id] === 'down'
                                  ? 'text-red-600 bg-red-50 dark:bg-red-900/20'
                                  : feedbackSubmitted[digest.id] === 'up'
                                  ? 'text-muted cursor-not-allowed'
                                  : 'text-muted hover:text-error hover:bg-red-50 dark:hover:bg-red-900/20'
                              }`}
                              onClick={() => handleFeedback(digest.id, 0.0)}
                              title={feedbackSubmitted[digest.id] ? "Отзыв уже отправлен" : "Не понравилось"}
                              disabled={!!feedbackSubmitted[digest.id]}
                            >
                              <ThumbsDown className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        
                        {activeTab === 'active' && (
                          <>
                            <button 
                              className="p-1.5 text-muted hover:text-warning hover:bg-amber-50 dark:hover:bg-amber-900/20 rounded-lg transition-colors"
                              onClick={() => archiveDigest(digest.id)}
                              title="В архив"
                            >
                              <Archive className="w-4 h-4" />
                            </button>
                            <button 
                              className="p-1.5 text-muted hover:text-error hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                              onClick={() => softDeleteDigest(digest.id)}
                              title="Удалить"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        {activeTab === 'archived' && (
                          <button 
                            className="p-1.5 text-muted hover:text-success hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors"
                            onClick={() => unarchiveDigest(digest.id)}
                            title="Восстановить"
                          >
                            <RotateCcw className="w-4 h-4" />
                          </button>
                        )}
                        {activeTab === 'deleted' && (
                          <button 
                            className="p-1.5 text-muted hover:text-success hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors"
                            onClick={() => restoreDigest(digest.id)}
                            title="Восстановить"
                          >
                            <RotateCcw className="w-4 h-4" />
                          </button>
                        )}
                        <button 
                          className="text-primary hover:text-primary-700 font-medium flex items-center gap-1 transition-colors"
                          onClick={() => setSelectedDigest(digest)}
                        >
                          Подробнее
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                      </div>
                  </motion.div>
                </motion.div>
              ))}
            </div>
          </motion.section>


          {/* Пустое состояние */}
          {filteredDigests.length === 0 && (
            <motion.div
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="flex flex-col items-center justify-center p-8 rounded-3xl card mt-6"
            >
              <Bot className="w-10 h-10 text-primary mb-3" />
              <p className="text-muted text-sm">
                {activeTab === 'active' && "Пока пусто — но AI уже готов собрать первый дайджест."}
                {activeTab === 'archived' && "В архиве пока ничего нет."}
                {activeTab === 'deleted' && "Корзина пуста."}
              </p>
            </motion.div>
          )}
        </motion.div>
      </main>

      {/* Digest Generator Modal */}
      <DigestGenerator
        isOpen={isGeneratorOpen}
        onClose={() => {
          setSelectedDigest(null); // Убеждаемся, что модалка просмотра дайджеста закрыта
          setIsGeneratorOpen(false);
        }}
        onGenerate={generateDigest}
      />

      {/* Magic Progress Overlay - показывается даже после закрытия модалки */}
      <AnimatePresence>
        {isGeneratingDigest && (
          <DigestMagicProgress 
            style={generatingStyle}
          />
        )}
      </AnimatePresence>

      {/* Digest Detail Modal */}
      {selectedDigest && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.5 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          className="fixed inset-0 bg-black/40 backdrop-blur-sm z-40"
        />
      )}
      
      {selectedDigest && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="w-full max-w-2xl max-h-[75vh] 
                       glass rounded-3xl 
                       shadow-card-hover
                       p-6 
                       overflow-hidden flex flex-col"
          >
            {/* Close button */}
            <button 
              className="absolute top-4 right-4 p-2 rounded-full hover:bg-surfaceAlt transition-colors"
              onClick={() => setSelectedDigest(null)}
            >
              <X className="w-5 h-5 text-muted" />
            </button>

            {/* Header with badges only */}
            <div className="mb-4">
              {/* Category, style and date badges */}
              <div className="flex items-center gap-2 mb-3 flex-wrap">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
                  <Sparkles className="w-3 h-3 mr-1" />
                  {selectedDigest.metadata?.category_name || selectedDigest.category}
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400">
                  {(() => {
                    const styleIcons = {
                      analytical: <Bot className="w-3 h-3 mr-1" />,
                      business: <Bot className="w-3 h-3 mr-1" />,
                      meme: <Bot className="w-3 h-3 mr-1" />,
                      newsroom: <Newspaper className="w-3 h-3 mr-1" />,
                      magazine: <BookOpen className="w-3 h-3 mr-1" />,
                      casual: <MessageCircle className="w-3 h-3 mr-1" />,
                      explanatory: <FileText className="w-3 h-3 mr-1" />,
                      technical: <Settings className="w-3 h-3 mr-1" />
                    };
                    return styleIcons[selectedDigest.style as keyof typeof styleIcons] || <Bot className="w-3 h-3 mr-1" />;
                  })()}
                  {styles[selectedDigest.style || ''] || selectedDigest.metadata?.style_name || selectedDigest.style}
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-surface-alt text-muted">
                  <CalendarDays className="w-3 h-3 mr-1" />
                  {new Date(selectedDigest.createdAt).toLocaleDateString('ru-RU', { 
                    day: 'numeric', 
                    month: 'short' 
                  })} в {new Date(selectedDigest.createdAt).toLocaleTimeString('ru-RU', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
              </div>
            </div>

            {/* Content - scrollable */}
            <div className="flex-1 overflow-y-auto mb-5">
              <div className="text-[15px] leading-relaxed text-text whitespace-pre-wrap">
                {selectedDigest.content ? (
                  <div 
                    className="prose prose-sm max-w-none dark:prose-invert"
                    dangerouslySetInnerHTML={{ __html: selectedDigest.content }}
                  />
                ) : (
                  <p className="text-[15px] leading-relaxed whitespace-pre-wrap">
                    {selectedDigest.summary}
                  </p>
                )}
              </div>
            </div>

            {/* Footer - simplified */}
            <div className="pt-6 mt-6 flex items-center justify-between text-xs text-muted">
              {/* Feedback buttons - only for active tab */}
              {activeTab === 'active' && (
                <div className="flex gap-2">
                  <button 
                    className={`p-2 rounded-lg transition-colors ${
                      feedbackSubmitted[selectedDigest.id] === 'up'
                        ? 'text-green-600 bg-green-50 dark:bg-green-900/20'
                        : feedbackSubmitted[selectedDigest.id] === 'down'
                        ? 'text-muted cursor-not-allowed'
                        : 'text-muted hover:text-success hover:bg-green-50 dark:hover:bg-green-900/20'
                    }`}
                    onClick={() => handleFeedback(selectedDigest.id, 1.0)}
                    title={feedbackSubmitted[selectedDigest.id] ? "Отзыв уже отправлен" : "Понравилось"}
                    disabled={!!feedbackSubmitted[selectedDigest.id]}
                  >
                    <ThumbsUp className="w-4 h-4" />
                  </button>
                  <button 
                    className={`p-2 rounded-lg transition-colors ${
                      feedbackSubmitted[selectedDigest.id] === 'down'
                        ? 'text-red-600 bg-red-50 dark:bg-red-900/20'
                        : feedbackSubmitted[selectedDigest.id] === 'up'
                        ? 'text-muted cursor-not-allowed'
                        : 'text-muted hover:text-error hover:bg-red-50 dark:hover:bg-red-900/20'
                    }`}
                    onClick={() => handleFeedback(selectedDigest.id, 0.0)}
                    title={feedbackSubmitted[selectedDigest.id] ? "Отзыв уже отправлен" : "Не понравилось"}
                    disabled={!!feedbackSubmitted[selectedDigest.id]}
                  >
                    <ThumbsDown className="w-4 h-4" />
                  </button>
                </div>
              )}
              
              <div className="flex gap-2">
                {activeTab === 'active' && (
                  <>
                    <button 
                      className="px-3 py-1 bg-amber-50 text-amber-700 hover:bg-amber-100 dark:bg-amber-900/20 dark:text-amber-400 dark:hover:bg-amber-900/30 rounded-lg text-xs font-medium transition-all"
                      onClick={() => {
                        archiveDigest(selectedDigest.id);
                        setSelectedDigest(null);
                      }}
                    >
                      В архив
                    </button>
                    <button 
                      className="px-3 py-1 bg-rose-50 text-rose-700 hover:bg-rose-100 dark:bg-rose-900/20 dark:text-rose-400 dark:hover:bg-rose-900/30 rounded-lg text-xs font-medium transition-all"
                      onClick={() => {
                        softDeleteDigest(selectedDigest.id);
                        setSelectedDigest(null);
                      }}
                    >
                      Удалить
                    </button>
                  </>
                )}
                {activeTab === 'archived' && (
                  <button 
                    className="px-3 py-1 bg-green-50 text-green-700 hover:bg-green-100 dark:bg-green-900/20 dark:text-green-400 dark:hover:bg-green-900/30 rounded-lg text-xs font-medium transition-all"
                    onClick={() => {
                      unarchiveDigest(selectedDigest.id);
                      setSelectedDigest(null);
                    }}
                  >
                    Восстановить
                  </button>
                )}
                {activeTab === 'deleted' && (
                  <button 
                    className="px-3 py-1 bg-green-50 text-green-700 hover:bg-green-100 dark:bg-green-900/20 dark:text-green-400 dark:hover:bg-green-900/30 rounded-lg text-xs font-medium transition-all"
                    onClick={() => {
                      restoreDigest(selectedDigest.id);
                      setSelectedDigest(null);
                    }}
                  >
                    Восстановить
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      )}

      {/* Scroll to Top Button */}
      {showScrollTop && (
        <motion.button
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.8 }}
          onClick={scrollToTop}
          className="fixed bottom-20 right-4 z-40 
                     bg-primary hover:bg-primary/90 
                     text-white 
                     rounded-full p-3 
                     shadow-lg hover:shadow-xl 
                     transition-all duration-300"
          aria-label="Прокрутить вверх"
        >
          <ArrowUp className="w-6 h-6" />
        </motion.button>
      )}
    </div>
  );
};

export default DigestPage;
