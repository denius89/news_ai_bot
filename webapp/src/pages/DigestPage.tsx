import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { MobileHeader } from '../components/ui/Header';
import { DigestGenerator } from '../components/digest/DigestGenerator';
import { Bot, Sparkles, Plus, Filter, Trash2, Archive, RotateCcw, Eye, Loader2, ExternalLink, X } from 'lucide-react';
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
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [notification, setNotification] = useState<{type: 'success' | 'error', message: string} | null>(null);
  const [selectedDigest, setSelectedDigest] = useState<DigestItem | null>(null);
  
  // 🚀 Автоматическое получение user_id из Telegram WebApp
  const { userId, telegramUser, userData, loading: userLoading, error: userError, isTelegramWebApp, isAuthenticated } = useTelegramUser();

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
          setCategories({ all: '🌐 Все категории', ...data.data.categories });
        }
      } catch (error) {
        console.warn('Failed to load categories, using defaults:', error);
        setCategories({
          all: '🌐 Все категории',
          crypto: '₿ Криптовалюты',
          sports: '⚽ Спорт',
          markets: '📈 Рынки',
          tech: '🤖 Технологии',
          world: '🌍 Мир'
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

  // Mock data
  const mockDigests: DigestItem[] = [
    {
      id: '1',
      title: 'Еженедельный дайджест: Криптовалютный рынок',
      summary: 'Обзор ключевых событий на криптовалютном рынке за последнюю неделю: рост Bitcoin, новые регуляторные инициативы и институциональные инвестиции.',
      category: 'crypto',
      sources: ['CoinDesk', 'CoinTelegraph', 'Decrypt'],
      createdAt: '2025-01-06T08:00:00Z',
      readTime: 5,
      keyPoints: [
        'Bitcoin достиг новых максимумов',
        'Институциональные инвестиции выросли на 25%',
        'Новые регуляторные инициативы в ЕС',
      ],
    },
    {
      id: '2',
      title: 'Технологический дайджест: ИИ и машинное обучение',
      summary: 'Последние достижения в области искусственного интеллекта, включая новые модели языковых моделей и применение ИИ в различных отраслях.',
      category: 'tech',
      sources: ['TechCrunch', 'The Verge', 'Wired'],
      createdAt: '2025-01-05T10:30:00Z',
      readTime: 7,
      keyPoints: [
        'Новая архитектура нейронных сетей',
        'ИИ в медицине: прорыв в диагностике',
        'Этические вопросы развития ИИ',
      ],
    },
    {
      id: '3',
      title: 'Спортивный дайджест: Главные события',
      summary: 'Обзор ключевых спортивных событий: результаты матчей, трансферы и важные турниры.',
      category: 'sports',
      sources: ['ESPN', 'BBC Sport', 'Sky Sports'],
      createdAt: '2025-01-05T07:15:00Z',
      readTime: 4,
      keyPoints: [
        'Чемпионат мира: полуфиналы завершены',
        'Зимние Олимпийские игры: подготовка',
        'Футбольные трансферы: крупные сделки',
      ],
    },
  ];

  // Soft delete digest function
  const softDeleteDigest = async (digestId: string) => {
    if (!userId) {
      console.error('❌ User ID not available for delete operation');
      return;
    }
    
    setActionLoading(digestId);
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
        showNotification('success', 'Дайджест перемещен в корзину');
        // Перезагружаем историю для обновления удаленных
        setTimeout(() => loadDigestHistory(), 500);
      } else {
        console.error('Failed to delete digest:', data.message);
        showNotification('error', `Ошибка удаления: ${data.message}`);
      }
    } catch (error) {
      console.error('Error deleting digest:', error);
    } finally {
      setActionLoading(null);
    }
  };

  // Restore digest function
  const restoreDigest = async (digestId: string) => {
    if (!userId) {
      console.error('❌ User ID not available for restore operation');
      return;
    }
    
    setActionLoading(digestId);
    try {
      const response = await fetch(`/api/digests/${digestId}/restore?user_id=${userId}`, {
        method: 'POST'
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        // Показываем уведомление
        showNotification('success', 'Дайджест восстановлен из корзины');
        // Перезагружаем историю (без локального обновления)
        setTimeout(() => loadDigestHistory(), 500);
      } else {
        console.error('Failed to restore digest:', data.message);
        showNotification('error', `Ошибка восстановления: ${data.message}`);
      }
    } catch (error) {
      console.error('Error restoring digest:', error);
    } finally {
      setActionLoading(null);
    }
  };

  // Archive digest function
  const archiveDigest = async (digestId: string) => {
    if (!userId) {
      console.error('❌ User ID not available for archive operation');
      return;
    }
    
    setActionLoading(digestId);
    try {
      const response = await fetch(`/api/digests/${digestId}/archive?user_id=${userId}`, {
        method: 'POST'
      });
      
      const data = await response.json();
      if (data.status === 'success') {
        // Обновляем списки
        setDigests(prev => prev.filter(d => d.id !== digestId));
        // Показываем уведомление
        showNotification('success', 'Дайджест архивирован');
        // Перезагружаем историю для обновления архивированных
        setTimeout(() => loadDigestHistory(), 500);
      } else {
        console.error('Failed to archive digest:', data.message);
        showNotification('error', `Ошибка архивирования: ${data.message}`);
      }
    } catch (error) {
      console.error('Error archiving digest:', error);
    } finally {
      setActionLoading(null);
    }
  };

  // Unarchive digest function
  const unarchiveDigest = async (digestId: string) => {
    if (!userId) {
      console.error('❌ User ID not available for unarchive operation');
      return;
    }
    
    setActionLoading(digestId);
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
    } finally {
      setActionLoading(null);
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
        // Add to digests list
        const newDigest: DigestItem = {
          id: data.data.digest_id || Date.now().toString(),
          title: `AI-дайджест: ${data.data.metadata.category_name}`,
          summary: `Стиль: ${data.data.metadata.style_name} • Период: ${period}`,
          category: category,
          sources: ['AI Generated'],
          createdAt: new Date().toISOString(),
          readTime: Math.ceil(data.data.digest.length / 1000),
          keyPoints: [],
          content: data.data.digest,
          style: style,
          period: period,
          limit: 10,
          metadata: data.data.metadata
        };
        
        // Показываем уведомление об успешной генерации
        showNotification('success', `Дайджест "${data.data.metadata.category_name}" успешно создан!`);
        
        // Перезагружаем историю для обновления списка (без дублирования)
        if (data.data.saved) {
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


  // Generate subtitle with user info
  const getSubtitle = () => {
    const count = filteredDigests.length;
    const tabName = activeTab === 'active' ? 'активных' : activeTab === 'archived' ? 'архивированных' : 'удаленных';
    
    let userInfo = '';
    if (isTelegramWebApp && telegramUser) {
      userInfo = ` • ${telegramUser.first_name}`;
    } else if (userData?.username) {
      userInfo = ` • ${userData.username}`;
    }
    
    return `${count} ${tabName} дайджестов${userInfo}`;
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
        ease: "easeOut",
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
            ? 'bg-green-500 text-white' 
            : 'bg-red-500 text-white'
        }`}>
          {notification.message}
        </div>
      )}
      
      <MobileHeader 
        title="AI Дайджест" 
        subtitle={getSubtitle()}
        actions={
          <Button 
            variant="ghost" 
            size="sm"
            onClick={() => setIsGeneratorOpen(true)}
            className="bg-primary/10 hover:bg-primary/20 text-primary"
          >
            <Plus className="w-5 h-5" />
          </Button>
        }
      />
      
      <main className="container-main">
        {/* Tabs Navigation - простые кнопки с видимым текстом */}
        <div className="flex space-x-1 mb-6 bg-surface-alt rounded-xl p-1">
          <button
            onClick={() => setActiveTab('active')}
            className={`flex-1 px-2 py-2 rounded-lg text-xs font-medium transition-colors ${
              activeTab === 'active'
                ? 'bg-primary text-white shadow-sm'
                : 'text-text dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <Eye className="w-3 h-3 inline mr-1" />
            Активные
          </button>
          <button
            onClick={() => setActiveTab('archived')}
            className={`flex-1 px-2 py-2 rounded-lg text-xs font-medium transition-colors ${
              activeTab === 'archived'
                ? 'bg-primary text-white shadow-sm'
                : 'text-text dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <Archive className="w-3 h-3 inline mr-1" />
            Архив
          </button>
          <button
            onClick={() => setActiveTab('deleted')}
            className={`flex-1 px-2 py-2 rounded-lg text-xs font-medium transition-colors ${
              activeTab === 'deleted'
                ? 'bg-primary text-white shadow-sm'
                : 'text-text dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            <Trash2 className="w-3 h-3 inline mr-1" />
            Корзина
          </button>
        </div>

        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {/* Category Filters */}
          <motion.section variants={itemVariants}>
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-wrap gap-2">
                  {Object.entries(categories).map(([key, label]) => (
                    <Button
                      key={key}
                      variant={selectedCategory === key ? 'primary' : 'secondary'}
                      size="sm"
                      onClick={() => setSelectedCategory(key)}
                    >
                      <Filter className="w-4 h-4 mr-1" />
                      {label}
                    </Button>
                  ))}
                </div>
              </CardContent>
            </Card>
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
                  <div className="bg-white dark:bg-surface-alt rounded-3xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] hover:shadow-[0_6px_20px_rgba(0,0,0,0.06)] transition-all duration-300 hover:scale-[1.01] p-5">
                    <div className="flex justify-between items-start">
                      <h3 className="text-lg font-semibold text-text dark:text-white leading-snug">
                        {truncateText(digest.title || digest.summary, 100)}
                      </h3>
                    </div>

                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      {digest.sources?.join(', ') || 'AI Generated'} • {new Date(digest.createdAt).toLocaleDateString('ru-RU')}
                    </p>

                    <p className="mt-2 text-[15px] text-text/90 leading-relaxed line-clamp-3">
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
                          className="text-primary font-medium hover:underline flex items-center gap-1"
                          onClick={() => setSelectedDigest(digest)}
                        >
                          Подробнее
                          <ExternalLink className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Generate New Digest */}
          <motion.section variants={itemVariants}>
            <Card className="bg-gradient-to-br from-primary/5 to-primary/10 border-primary/20">
              <CardContent className="pt-6">
                <div className="text-center">
                  <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Bot className="w-8 h-8 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold text-text mb-2">
                    Создать AI-дайджест
                  </h3>
                  <p className="text-muted-strong mb-6 max-w-md mx-auto">
                    Выберите категорию, стиль и получите персональный дайджест с анализом от ИИ
                  </p>
                  <Button 
                    variant="primary" 
                    size="lg"
                    onClick={() => setIsGeneratorOpen(true)}
                    className="bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70"
                  >
                    <Sparkles className="w-5 h-5 mr-2" />
                    Создать дайджест
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.section>

          {/* Empty State */}
          {filteredDigests.length === 0 && (
            <motion.section variants={itemVariants} className="text-center py-20">
              <div className="text-6xl mb-4">📝</div>
              <h3 className="text-xl font-semibold text-text mb-2">
                Дайджесты не найдены
              </h3>
              <p className="text-muted-strong mb-6">
                Попробуйте выбрать другую категорию или создайте новый дайджест
              </p>
              <Button 
                variant="secondary" 
                onClick={() => setSelectedCategory('all')}
              >
                Показать все
              </Button>
            </motion.section>
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
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="relative w-full max-w-2xl max-h-[75vh] 
                       bg-white/95 dark:bg-surface-alt/95 
                       backdrop-blur-lg rounded-3xl 
                       shadow-[0_8px_32px_rgba(0,0,0,0.12)] 
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

            {/* Category and source */}
            <div className="flex gap-2 text-sm mb-3">
              <span className="text-primary font-medium">
                {categories[selectedDigest.category] || selectedDigest.category}
              </span>
              <span className="text-gray-400 dark:text-gray-500">•</span>
              <span className="text-gray-500 dark:text-gray-400">
                {selectedDigest.sources?.join(', ') || 'AI Generated'}
              </span>
            </div>

            {/* Title */}
            <h2 className="text-xl md:text-2xl font-semibold text-text dark:text-white tracking-tight leading-snug mb-3">
              {selectedDigest.title || selectedDigest.summary}
            </h2>

            {/* Content - scrollable */}
            <div className="flex-1 overflow-y-auto mb-5">
              {selectedDigest.content ? (
                <div 
                  className="prose prose-sm max-w-none dark:prose-invert"
                  dangerouslySetInnerHTML={{ __html: selectedDigest.content }}
                />
              ) : (
                <p className="text-[15px] leading-relaxed text-text/90 dark:text-gray-300 whitespace-pre-wrap">
                  {selectedDigest.summary}
                </p>
              )}
            </div>

            {/* Footer - simplified */}
            <div className="border-t border-gray-100 dark:border-gray-700 pt-4 mt-4">
              <div className="flex items-center justify-between text-xs text-gray-400 dark:text-gray-500 mb-3">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <Bot className="w-3 h-3 text-blue-500" />
                    <span>AI Generated</span>
                  </div>
                </div>
                <div className="text-gray-400 dark:text-gray-500">
                  {new Date(selectedDigest.createdAt).toLocaleDateString('ru-RU')}
                </div>
              </div>
              
              {/* Action buttons in modal */}
              <div className="flex gap-2">
                {activeTab === 'active' && (
                  <>
                    <button 
                      className="flex-1 px-3 py-2 text-xs font-medium text-amber-600 bg-amber-50 dark:bg-amber-900/20 dark:text-amber-400 rounded-lg hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors flex items-center justify-center gap-1"
                      onClick={() => {
                        archiveDigest(selectedDigest.id);
                        setSelectedDigest(null);
                      }}
                    >
                      <Archive className="w-3 h-3" />
                      В архив
                    </button>
                    <button 
                      className="flex-1 px-3 py-2 text-xs font-medium text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400 rounded-lg hover:bg-red-100 dark:hover:bg-red-900/30 transition-colors flex items-center justify-center gap-1"
                      onClick={() => {
                        softDeleteDigest(selectedDigest.id);
                        setSelectedDigest(null);
                      }}
                    >
                      <Trash2 className="w-3 h-3" />
                      Удалить
                    </button>
                  </>
                )}
                {activeTab === 'archived' && (
                  <button 
                    className="flex-1 px-3 py-2 text-xs font-medium text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors flex items-center justify-center gap-1"
                    onClick={() => {
                      unarchiveDigest(selectedDigest.id);
                      setSelectedDigest(null);
                    }}
                  >
                    <RotateCcw className="w-3 h-3" />
                    Восстановить
                  </button>
                )}
                {activeTab === 'deleted' && (
                  <button 
                    className="flex-1 px-3 py-2 text-xs font-medium text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400 rounded-lg hover:bg-green-100 dark:hover:bg-green-900/30 transition-colors flex items-center justify-center gap-1"
                    onClick={() => {
                      restoreDigest(selectedDigest.id);
                      setSelectedDigest(null);
                    }}
                  >
                    <RotateCcw className="w-3 h-3" />
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
