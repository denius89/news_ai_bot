import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { MobileHeader } from '../components/ui/Header';
import { DigestGenerator } from '../components/digest/DigestGenerator';
import { Bot, Sparkles, Filter, Trash2, Archive, RotateCcw, Eye, Loader2, ExternalLink, X, Bitcoin, LineChart, Trophy, Cpu, Globe2, CalendarDays } from 'lucide-react';
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
  const [activeTab, setActiveTab] = useState<'active' | 'archived' | 'deleted'>('active');
  const [deletedDigests, setDeletedDigests] = useState<DigestItem[]>([]);
  const [archivedDigests, setArchivedDigests] = useState<DigestItem[]>([]);
  const [notification, setNotification] = useState<{type: 'success' | 'error', message: string} | null>(null);
  const [selectedDigest, setSelectedDigest] = useState<DigestItem | null>(null);
  
  // 🚀 Автоматическое получение user_id из Telegram WebApp
  const { userId, loading: userLoading, error: userError, isAuthenticated } = useTelegramUser();

  // Функция для показа уведомлений
  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    setTimeout(() => setNotification(null), 3000);
  };

  // Load categories from API
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
    
    loadCategories();
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
      
      // Загружаем активные дайджесты (не удаленные и не архивированные)
      const activeResponse = await fetch(`/api/digests/history?user_id=${userId}&limit=10&include_deleted=false&include_archived=false`);
      const activeData = await activeResponse.json();
      
      // Загружаем архивированные дайджесты
      const archivedResponse = await fetch(`/api/digests/history?user_id=${userId}&limit=10&include_deleted=false&include_archived=true`);
      const archivedData = await archivedResponse.json();
      
      // Загружаем удаленные дайджесты
      const deletedResponse = await fetch(`/api/digests/history?user_id=${userId}&limit=10&include_deleted=true&include_archived=false`);
      const deletedData = await deletedResponse.json();
      
      const processDigests = (digestsData: any[]) => digestsData.map((digest: any) => ({
        id: digest.id,
        title: `${digest.category} • ${digest.style}`,
        summary: digest.summary,
        category: digest.category,
        createdAt: digest.created_at,
        style: digest.style,
        period: digest.period,
        limit: digest.limit,
        preview: digest.preview,
        content: digest.summary,
        readTime: Math.ceil(digest.summary.length / 1000), // Примерное время чтения
        sources: ['AI Generated'],
        keyPoints: []
      }));
      
      if (activeData.status === 'success') {
        const historyDigests = processDigests(activeData.data.digests);
        setDigests(historyDigests); // Используем только реальные данные
        console.log('✅ Загружено активных дайджестов:', historyDigests.length);
      } else {
        console.warn('⚠️ Не удалось загрузить активные дайджесты:', activeData.message);
        setDigests([]);
      }
      
      if (archivedData.status === 'success') {
        const archivedHistoryDigests = processDigests(archivedData.data.digests);
        setArchivedDigests(archivedHistoryDigests);
        console.log('✅ Загружено архивированных дайджестов:', archivedHistoryDigests.length);
      } else {
        console.warn('⚠️ Не удалось загрузить архивированные дайджесты:', archivedData.message);
        setArchivedDigests([]);
      }
      
      if (deletedData.status === 'success') {
        const deletedHistoryDigests = processDigests(deletedData.data.digests);
        setDeletedDigests(deletedHistoryDigests);
        console.log('✅ Загружено удаленных дайджестов:', deletedHistoryDigests.length);
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
    if (userId && !userLoading) {
      loadDigestHistory();
    }
  }, [userId, userLoading]);


  // Soft delete digest function
  const softDeleteDigest = async (digestId: string) => {
    if (!userId) {
      console.error('❌ User ID not available for delete operation');
      return;
    }
    
    try {
      const response = await fetch(`/api/digests/${digestId}?user_id=${userId}`, {
        method: 'DELETE'
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
        method: 'POST'
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
        method: 'POST'
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
        method: 'POST'
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
  const generateDigest = async (category: string, style: string, period: string): Promise<string> => {
    try {
      // 🚀 Используем автоматически полученный user_id из Telegram WebApp
      if (!userId) {
        throw new Error('User ID not available. Please ensure you are logged in.');
      }
      
      console.log('🔄 Generating digest for user:', userId);
      
      const response = await fetch('/api/digests/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category,
          style,
          period,
          limit: 10,
          user_id: userId,
          save: true
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        
        // Показываем уведомление об успешной генерации
        showNotification('success', 'Дайджест успешно создан');
        
        // Перезагружаем историю для обновления списка (без дублирования)
        if (data.data.saved) {
          // Убеждаемся, что модалка просмотра закрыта перед обновлением списка
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
    }
  };

  useEffect(() => {
    // Load any existing digests from localStorage or API
      setLoading(false);
  }, []);

  // Get current digests based on active tab
  // Show loading state while user is being authenticated
  if (userLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted">Загрузка пользователя...</p>
        </div>
      </div>
    );
  }

  // Show error state if user authentication failed
  if (userError && !isAuthenticated) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <Bot className="w-12 h-12 mx-auto mb-4 text-muted" />
          <h2 className="text-xl font-semibold mb-2">Ошибка аутентификации</h2>
          <p className="text-muted mb-4">{userError}</p>
          <Button onClick={() => window.location.reload()}>
            Попробовать снова
          </Button>
        </div>
      </div>
    );
  }

  const getCurrentDigests = () => {
    switch (activeTab) {
      case 'active':
        return digests;
      case 'archived':
        return archivedDigests;
      case 'deleted':
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
        <MobileHeader title="AI Дайджест" subtitle="Загрузка..." />
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
      
      <main className="pb-32 pt-2 px-4 max-w-md mx-auto">
        {/* Заголовок */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
              AI Дайджест
            </h1>
            {/* Кнопка создания дайджеста - только для активной вкладки */}
            {activeTab === 'active' && (
              <motion.button
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsGeneratorOpen(true)}
                className="px-4 py-2 rounded-full font-medium text-sm text-white
                           bg-gradient-to-r from-teal-400 via-emerald-400 to-teal-500
                           hover:shadow-[0_0_12px_rgba(16,185,129,0.4)] 
                           active:scale-95 transition-all duration-300 flex items-center gap-2"
              >
                <Sparkles className="w-4 h-4" />
                Создать
              </motion.button>
            )}
          </div>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            PulseAI анализирует новости и создаёт короткие дайджесты в вашем стиле.
          </p>
        </div>
        {/* Фильтры и вкладки */}
        <div className="flex space-x-1 mb-6 bg-gray-100/50 dark:bg-gray-800/40 rounded-xl p-1">
          <motion.button
            layout
            whileTap={{ scale: 0.97 }}
            transition={{ type: "spring", stiffness: 250, damping: 20 }}
            onClick={() => setActiveTab('active')}
            className={`flex-1 px-4 py-2 rounded-full text-sm font-medium transition-all duration-300 ${
              activeTab === 'active'
                ? "bg-gradient-to-r from-teal-400 to-emerald-400 text-white shadow-[0_0_12px_rgba(16,185,129,0.3)]"
                : "text-gray-600 dark:text-gray-400 hover:bg-gray-50/50 dark:hover:bg-gray-800/40"
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
                ? "bg-gradient-to-r from-teal-400 to-emerald-400 text-white shadow-[0_0_12px_rgba(16,185,129,0.3)]"
                : "text-gray-600 dark:text-gray-400 hover:bg-gray-50/50 dark:hover:bg-gray-800/40"
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
                ? "bg-gradient-to-r from-teal-400 to-emerald-400 text-white shadow-[0_0_12px_rgba(16,185,129,0.3)]"
                : "text-gray-600 dark:text-gray-400 hover:bg-gray-50/50 dark:hover:bg-gray-800/40"
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
                        ? "bg-gradient-to-r from-teal-400 to-emerald-400 text-white shadow-[0_0_12px_rgba(16,185,129,0.3)]"
                        : "bg-white/80 dark:bg-[#161616]/80 text-gray-600 dark:text-gray-400 hover:bg-gray-50/50 dark:hover:bg-gray-800/40"
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
                    className="bg-white/80 dark:bg-[#161616]/80 backdrop-blur-md border border-white/10 
                               rounded-3xl p-5 pb-6 shadow-[0_6px_20px_rgba(0,0,0,0.05)] 
                               hover:scale-[1.02] transition-transform duration-300 ease-out mt-4"
                    whileHover={{ scale: 1.02 }}
                    transition={{ type: "spring", stiffness: 300, damping: 30 }}
                  >
                    <div className="flex justify-between items-start">
                      <h3 className="text-[15px] font-semibold text-gray-900 dark:text-white leading-snug">
                        {truncateText(digest.title || digest.summary, 100)}
                      </h3>
                      </div>

                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {digest.sources?.join(', ') || 'AI Generated'} • {new Date(digest.createdAt).toLocaleDateString('ru-RU')}
                    </p>

                    <p className="mt-2 text-[14px] text-gray-700 dark:text-gray-300 leading-relaxed line-clamp-3">
                      {truncateText(digest.summary, 200)}
                    </p>

                    <div className="mt-4 flex justify-between items-center text-sm">
                      <span className="text-gray-500 dark:text-gray-400">{categories[digest.category] || digest.category}</span>
                      <div className="flex items-center gap-2">
                        {activeTab === 'active' && (
                          <>
                            <button 
                              className="p-1.5 text-gray-400 hover:text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-900/20 rounded-lg transition-colors"
                              onClick={() => archiveDigest(digest.id)}
                              title="В архив"
                            >
                              <Archive className="w-4 h-4" />
                            </button>
                            <button 
                              className="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                              onClick={() => softDeleteDigest(digest.id)}
                              title="Удалить"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        {activeTab === 'archived' && (
                          <button 
                            className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors"
                            onClick={() => unarchiveDigest(digest.id)}
                            title="Восстановить"
                          >
                            <RotateCcw className="w-4 h-4" />
                          </button>
                        )}
                        {activeTab === 'deleted' && (
                          <button 
                            className="p-1.5 text-gray-400 hover:text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 rounded-lg transition-colors"
                            onClick={() => restoreDigest(digest.id)}
                            title="Восстановить"
                          >
                            <RotateCcw className="w-4 h-4" />
                          </button>
                        )}
                        <button 
                          className="text-emerald-500 hover:text-emerald-400 font-medium flex items-center gap-1 transition-colors"
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
              className="flex flex-col items-center justify-center p-8 rounded-3xl bg-white/80 dark:bg-[#161616]/80 mt-6"
            >
              <Bot className="w-10 h-10 text-emerald-400 mb-3" />
              <p className="text-gray-600 dark:text-gray-400 text-sm">
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
        onClose={() => setIsGeneratorOpen(false)}
        onGenerate={generateDigest}
      />

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
                       bg-white dark:bg-surface-alt 
                       backdrop-blur-lg rounded-3xl 
                       shadow-[0_8px_32px_rgba(0,0,0,0.12)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)]
                       p-6 
                       overflow-hidden flex flex-col"
          >
            {/* Close button */}
            <button 
              className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              onClick={() => setSelectedDigest(null)}
            >
              <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
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
                  <Bot className="w-3 h-3 mr-1" />
                  {selectedDigest.metadata?.style_name || selectedDigest.style}
                </span>
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-800/50 dark:text-gray-400">
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
              <div className="text-[15px] leading-relaxed text-text/90 dark:text-gray-300 whitespace-pre-wrap">
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
            <div className="border-t border-gray-200 dark:border-gray-600 pt-4 mt-4 flex items-center justify-end text-xs text-gray-400 dark:text-gray-500">
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
    </div>
  );
};

export default DigestPage;
