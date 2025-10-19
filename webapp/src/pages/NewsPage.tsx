import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Header } from '../components/ui/Header';
import { ChipsCarousel } from '../components/ui/ChipsCarousel';
import { useTelegramUser } from '../hooks/useTelegramUser';
import { useAuth } from '../context/AuthContext';
import { shouldReduceMotion } from '../utils/performance';
import { 
  Newspaper, 
  ExternalLink,
  X,
  Star,
  ArrowUp
} from 'lucide-react';

interface NewsItem {
  id: string;
  title: string;
  content: string;
  source: string;
  category: string;
  subcategory?: string; // ДОБАВЛЕНО: поддержка подкатегорий
  publishedAt: string;
  credibility: number;
  importance: number;
  url?: string;
}

interface NewsPageProps {
  theme: 'light' | 'dark';
  onThemeToggle: () => void;
  onNavigate?: (page: string) => void;
}

// Утилита для склонения чисел
function getNewsLabel(count: number) {
  const mod10 = count % 10;
  const mod100 = count % 100;
  if (mod10 === 1 && mod100 !== 11) return "новость";
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20))
    return "новости";
  return "новостей";
}

// Маппинг icon codes в emoji
function getEmojiFromIconCode(iconCode: string): string {
  const iconMap: Record<string, string> = {
    // Crypto
    'btc': '₿',
    'bitcoin': '₿',
    'eth': 'Ξ',
    'ethereum': 'Ξ',
    'altcoin': '🪙',
    'altcoins': '🪙',
    'defi': '🏦',
    'nft': '🖼️',
    'gamefi': '🎮',
    'exchange': '💱',
    'exchanges': '💱',
    'regulation': '⚖️',
    'security': '🔒',
    'market_trends': '📊',
    
    // Sports - Football leagues
    'football': '⚽',
    'champions_league': '⚽',
    'europa_league': '⚽',
    'conference_league': '⚽',
    'premier_league': '⚽',
    'bundesliga': '⚽',
    'la_liga': '⚽',
    'serie_a': '⚽',
    'ligue_1': '⚽',
    'world_cup': '⚽',
    // Sports - Other sports
    'basketball': '🏀',
    'tennis': '🎾',
    'hockey': '🏒',
    'ufc': '🥊',
    'ufc_mma': '🥊',
    'cricket': '🏏',
    'baseball': '⚾',
    'american_football': '🏈',
    'rugby': '🏉',
    'volleyball': '🏐',
    'handball': '🤾',
    'badminton': '🏸',
    'table_tennis': '🏓',
    // Sports - Esports
    'esports': '🎮',
    'dota2': '🎮',
    'csgo': '🔫',
    'lol': '🎮',
    'valorant': '🎮',
    'overwatch': '🎮',
    'r6siege': '🎮',
    'other': '🏆',
    'formula1': '🏎️',
    
    // Markets
    'stocks': '📈',
    'forex': '💱',
    'commodities': '🛢️',
    'bonds': '📊',
    'indices': '📉',
    'ipos': '📋',
    'earnings': '💰',
    'dividends': '💸',
    'splits': '✂️',
    'rates': '📊',
    'etf': '📊',
    'funds_etfs': '📊',
    'economic_data': '📊',
    'central_banks': '🏛️',
    
    // Tech
    'ai': '🤖',
    'software': '💻',
    'hardware': '🔧',
    'startups': '🚀',
    'cybersecurity': '🛡️',
    'cloud': '☁️',
    'bigtech': '💻',
    'blockchain': '⛓️',
    'blockchain_tech': '⛓️',
    'conferences': '🎤',
    
    // World
    'politics': '🏛️',
    'economy': '💼',
    'science': '🔬',
    'health': '🏥',
    'climate': '🌡️',
    'society': '👥',
    'conflicts': '⚠️',
    'elections': '🗳️',
    'energy': '⚡',
    'geopolitics': '🌍',
    'diplomacy': '🤝',
    'sanctions': '🚫',
    'organizations': '🏛️',
    'migration': '👥',
    'global_risks': '⚠️',
  };
  
  return iconMap[iconCode] || '📄';
}

const NewsPage: React.FC<NewsPageProps> = ({ onNavigate: _onNavigate }) => {
  // Feature flags для быстрого отката
  const ENABLE_SUBCATEGORY_FILTER = true;
  const ENABLE_DYNAMIC_CATEGORIES = true;

  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedSubcategory, setSelectedSubcategory] = useState<string | null>(null);
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMoreNews, setHasMoreNews] = useState(true);
  const [isFilteredBySubscriptions, setIsFilteredBySubscriptions] = useState(false);
  const [isInitialized, setIsInitialized] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);

  // Динамические категории
  const [categoriesData, setCategoriesData] = useState<any>(null);
  const [categories, setCategories] = useState<Array<{id: string, label: string, icon: string}>>([]);
  const [availableSubcategories, setAvailableSubcategories] = useState<Array<{id: string, label: string, icon: string}>>([]);

  // Get user data from authentication context
  const { userData } = useTelegramUser();
  const { authHeaders } = useAuth();
  const userId = userData?.user_id;


  // Функция загрузки категорий
  const loadCategories = useCallback(async () => {
    try {
      console.log('[NewsPage] Loading categories...');
      const response = await fetch('/api/categories', {
        headers: authHeaders
      });
      const data = await response.json();
      
      if (data.status === 'success' && data.data) {
        // Кэшируем полную структуру
        setCategoriesData(data.data);
        
        // Формируем список основных категорий
        const cats: Array<{id: string, label: string, icon: string}> = [
          { id: 'all', label: 'Все', icon: '📰' }
        ];
        
        Object.entries(data.data).forEach(([catId, catData]: [string, any]) => {
          cats.push({
            id: catId,
            label: catData.name || catId,
            icon: catData.emoji || '📁'
          });
        });
        
        setCategories(cats);
        console.log('[NewsPage] ✅ Categories loaded:', cats.length);
      }
    } catch (error) {
      console.error('[NewsPage] ❌ Error loading categories:', error);
      // Fallback на hardcoded категории при ошибке
      setCategories([
        { id: 'all', label: 'Все', icon: '📰' },
        { id: 'crypto', label: 'Криптовалюты', icon: '₿' },
        { id: 'tech', label: 'AI и технологии', icon: '🤖' },
        { id: 'sports', label: 'Спорт', icon: '⚽' },
        { id: 'world', label: 'Мир', icon: '🌍' },
        { id: 'markets', label: 'Финансы', icon: '📈' },
      ]);
    }
  }, [authHeaders]);

  // Функция загрузки подкатегорий с кэшированием
  const loadSubcategories = useCallback((categoryId: string) => {
    console.log('[NewsPage] Loading subcategories for:', categoryId);
    
    if (!categoriesData || !categoriesData[categoryId]) {
      setAvailableSubcategories([]);
      return;
    }
    
    const categoryData = categoriesData[categoryId];
    
    if (categoryData.subcategories) {
      const subcats: Array<{id: string, label: string, icon: string}> = [
        { id: '', label: `Все ${categoryData.name}`, icon: '📰' }
      ];
      
      Object.entries(categoryData.subcategories).forEach(([subId, subData]: [string, any]) => {
        subcats.push({
          id: subId,
          label: subData.name || subId,
          icon: getEmojiFromIconCode(subData.icon || '')
        });
      });
      
      setAvailableSubcategories(subcats);
      console.log('[NewsPage] ✅ Subcategories loaded:', subcats.length);
    } else {
      setAvailableSubcategories([]);
    }
  }, [categoriesData]);

  const fetchNews = useCallback(async (page: number = 1, isRefresh: boolean = false) => {
    try {
      if (isRefresh) {
        // setIsRefreshing удален
      } else if (page === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }

      // Build API URL with filtering
      let apiUrl = `/api/news/latest?page=${page}&limit=20`;
      
      if (userId) {
        apiUrl += `&filter_by_subscriptions=true`;
      }

      if (selectedCategory !== 'all') {
        apiUrl += `&category=${selectedCategory}`;
      }

      if (ENABLE_SUBCATEGORY_FILTER && selectedSubcategory) {
        apiUrl += `&subcategory=${selectedSubcategory}`;
      }

      console.log(`[NewsPage] Fetching news:`, {
        page,
        selectedCategory,
        selectedSubcategory,
        userId,
        apiUrl
      });
      
      const response = await fetch(apiUrl, {
        headers: authHeaders
      });
      
      console.log(`📡 Response status: ${response.status}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`📊 API response:`, data);
      
      if (data.status === 'success') {
        // Set filter indicator
        setIsFilteredBySubscriptions(data.filtered_by_subscriptions || false);
        
        // Transform API data to match our interface
        const transformedNews: NewsItem[] = data.data.map((item: any) => ({
          id: item.id || Math.random().toString(),
          title: item.title || 'Без заголовка',
          content: item.content || 'Содержимое недоступно',
          source: item.source || 'Неизвестный источник',
          category: item.category || 'general',
          publishedAt: item.published_at || new Date().toISOString(),
          credibility: item.credibility || 0.5,
          importance: item.importance || 0.5,
          url: item.url,
        }));

        if (page === 1 || isRefresh) {
          setNews(transformedNews);
          setCurrentPage(1);
        } else {
          setNews(prevNews => [...prevNews, ...transformedNews]);
          setCurrentPage(page);
        }

        // Update pagination info
        if (data.pagination) {
          setHasMoreNews(data.pagination.has_next);
        }
      } else {
        throw new Error(data.message || 'Ошибка получения данных');
      }
    } catch (error) {
      console.error('❌ Error fetching news:', error);
      console.error('📍 Error details:', {
        message: error instanceof Error ? error.message : 'Unknown error',
        page,
        timestamp: new Date().toISOString()
      });
      
      // Показываем пустой список при ошибке
      if (page === 1) {
        setNews([]);
      }
      setHasMoreNews(false);
    } finally {
      setLoading(false);
      setLoadingMore(false);
      // setIsRefreshing удален
    }
  }, [userId, authHeaders, selectedCategory, selectedSubcategory, ENABLE_SUBCATEGORY_FILTER]);

  // Обработчик выбора категории
  const handleCategorySelect = useCallback((categoryId: string) => {
    console.log('[NewsPage] Category selected:', {
      categoryId,
      previousCategory: selectedCategory,
      timestamp: new Date().toISOString()
    });
    
    setSelectedCategory(categoryId);
    setSelectedSubcategory(null);
    setNews([]);
    setCurrentPage(1);
    setHasMoreNews(true); // ВАЖНО: сбросить флаг пагинации
    
    if (categoryId !== 'all') {
      loadSubcategories(categoryId);
    } else {
      setAvailableSubcategories([]);
    }
    
    // Скролл в начало страницы
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [selectedCategory, loadSubcategories]);

  // Обработчик выбора подкатегории
  const handleSubcategorySelect = useCallback((subcategoryId: string) => {
    console.log('[NewsPage] Subcategory selected:', {
      subcategoryId,
      category: selectedCategory,
      timestamp: new Date().toISOString()
    });
    
    setSelectedSubcategory(subcategoryId || null);
    setNews([]);
    setCurrentPage(1);
    setHasMoreNews(true);
    
    // Скролл в начало
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [selectedCategory]);

  // Загрузка категорий при монтировании
  useEffect(() => {
    if (ENABLE_DYNAMIC_CATEGORIES) {
      loadCategories();
    }
  }, [loadCategories, ENABLE_DYNAMIC_CATEGORIES]);

  // Первичная загрузка новостей
  useEffect(() => {
    if (userId !== undefined && !isInitialized) {
      setIsInitialized(true);
      fetchNews(1);
    }
    // fetchNews убран из зависимостей чтобы избежать бесконечных циклов
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [userId, isInitialized]);

  // Автоматическая перезагрузка при изменении фильтров (ТОЛЬКО после инициализации)
  useEffect(() => {
    if (isInitialized && categories.length > 0) {
      fetchNews(1);
    }
    // fetchNews убран из зависимостей чтобы избежать бесконечных циклов
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedCategory, selectedSubcategory, isInitialized, categories.length]);

  const loadMoreNews = async () => {
    if (!hasMoreNews || loadingMore) {
      console.log('🚫 Load more blocked:', { hasMoreNews, loadingMore });
      return;
    }
    
    console.log('📰 Loading more news, current page:', currentPage);
    const nextPage = currentPage + 1;
    await fetchNews(nextPage);
  };

  // Убрали свайп - оставляем только infinite scroll вниз

  // Infinite scroll functionality + показ кнопки "вверх"
  useEffect(() => {
    const handleScroll = () => {
      // Более точная проверка достижения низа
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight;
      const clientHeight = window.innerHeight;
      
      // Показываем кнопку "вверх" если проскроллили больше 300px
      setShowScrollTop(scrollTop > 300);
      
      // Загружаем когда дошли до 200px от низа
      const isNearBottom = scrollTop + clientHeight >= scrollHeight - 200;
      
      console.log('📜 Scroll check:', { 
        scrollTop, 
        clientHeight, 
        scrollHeight,
        isNearBottom,
        hasMoreNews,
        loadingMore,
        loading 
      });
      
      if (isNearBottom && hasMoreNews && !loadingMore && !loading) {
        console.log('🔄 Triggering load more via infinite scroll');
        loadMoreNews();
      }
    };

    // Добавляем throttling для производительности (увеличен до 300ms для экономии батареи)
    let timeoutId: NodeJS.Timeout;
    const throttledHandleScroll = () => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(handleScroll, 300);
    };

    window.addEventListener('scroll', throttledHandleScroll, { passive: true });
    return () => {
      window.removeEventListener('scroll', throttledHandleScroll);
      clearTimeout(timeoutId);
    };
  }, [hasMoreNews, loadingMore, loading]);

  // Функция прокрутки вверх
  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // УБРАНО: клиентская фильтрация - теперь все фильтры на бэкенде
  const filteredNews = news;

  const truncateText = (text: string, maxLength: number = 200): string => {
    if (text.length <= maxLength) {
      return text;
    }
    return text.substring(0, maxLength).trim() + '...';
  };

  const getImportanceStars = (importance: number) => {
    // Защита от NaN, undefined, null и отрицательных значений
    const safeImportance = Math.max(0, Math.min(1, importance || 0));
    const stars = Math.round(safeImportance * 5);
    return '⭐'.repeat(stars) + '☆'.repeat(5 - stars);
  };

  // Определяем, нужно ли отключить анимации
  const reduceMotion = useMemo(() => shouldReduceMotion(), []);

  const containerVariants = useMemo(() => {
    if (reduceMotion) {
      return {
        hidden: { opacity: 1 },
        visible: { opacity: 1 },
      };
    }
    return {
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          duration: 0.2,
          // Убрали staggerChildren - экономит много ресурсов
        },
      },
    };
  }, [reduceMotion]);

  const itemVariants = useMemo(() => {
    if (reduceMotion) {
      return {
        hidden: { opacity: 1 },
        visible: { opacity: 1 },
      };
    }
    return {
      hidden: { opacity: 0 },
      visible: {
        opacity: 1,
        transition: {
          duration: 0.2,
        },
      },
    };
  }, [reduceMotion]);

  if (loading) {
    return (
      <div className="min-h-screen bg-bg">
        <Header 
          title="Новости" 
          subtitle="Загрузка новостей..."
          icon={<Newspaper className="w-6 h-6 text-primary" />}
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
      <Header 
        title="Новости" 
        subtitle={`${filteredNews.length} ${getNewsLabel(filteredNews.length)}`}
        icon={<Newspaper className="w-6 h-6 text-primary" />}
      />
      
      <main className="container-main">
        {/* Убрали индикатор свайпа - теперь только infinite scroll */}

        {/* Debug info - показываем состояние загрузки */}
        {process.env.NODE_ENV === 'development' && (
          <div className="fixed top-4 right-4 bg-black/80 text-white text-xs p-2 rounded-lg z-50">
            <div>Новостей: {news.length}</div>
            <div>Страница: {currentPage}</div>
            <div>Есть еще: {hasMoreNews ? 'Да' : 'Нет'}</div>
            <div>Загрузка: {loadingMore ? 'Да' : 'Нет'}</div>
            <div>Режим: Infinite Scroll</div>
          </div>
        )}
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {/* Category Filters - Двухуровневый с ChipsCarousel */}
          <motion.section variants={itemVariants}>
            <Card>
              <CardContent className="pt-6 space-y-3">
                {/* Уровень 1: Основные категории */}
                <ChipsCarousel
                  chips={categories}
                  selectedId={selectedCategory}
                  onSelect={handleCategorySelect}
                  label="Категории"
                />
                
                {/* Уровень 2: Подкатегории (показывается только если категория выбрана) */}
                {selectedCategory !== 'all' && availableSubcategories.length > 0 && (
                  <ChipsCarousel
                    chips={availableSubcategories}
                    selectedId={selectedSubcategory || ''}
                    onSelect={handleSubcategorySelect}
                    label="Подкатегории"
                  />
                )}
                
                {/* Hints и индикаторы */}
                <div className="mt-3 text-center space-y-1">
                  {isFilteredBySubscriptions && selectedCategory !== 'all' && (
                    <p className="text-xs text-primary font-medium">
                      💡 Показаны новости категории "{categories.find(c => c.id === selectedCategory)?.label}" (независимо от подписки)
                    </p>
                  )}
                  {isFilteredBySubscriptions && selectedCategory === 'all' && (
                    <p className="text-xs text-primary font-medium">
                      ✨ Показаны новости по вашим подпискам
                    </p>
                  )}
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    PulseAI отбирает новости с наибольшей вероятностью интереса.
                  </p>
                </div>
              </CardContent>
            </Card>
          </motion.section>

          {/* News List */}
          <motion.section variants={itemVariants}>
            <div className="space-y-4">
              {filteredNews.map((item) => (
                <div
                  key={item.id}
                  className={`card p-5 transition-all duration-300 ${!reduceMotion ? 'hover:scale-[1.01]' : ''}`}
                >
                  <div>
                    <div className="flex justify-between items-start">
                      <h3 className="text-lg font-semibold text-text dark:text-white leading-snug">
                        {truncateText(item.title, 100)}
                      </h3>
                      <span className="ml-2 text-xs bg-green-50 text-green-600 px-2 py-0.5 rounded-full font-medium">
                        {Math.round(item.importance * 100)}%
                      </span>
                    </div>

                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                      {item.url ? (
                        <a 
                          href={item.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-primary hover:text-primary/80 underline"
                        >
                          {item.source}
                        </a>
                      ) : (
                        item.source
                      )} • {new Date(item.publishedAt).toLocaleDateString('ru-RU')}
                    </p>

                    <p className="mt-2 text-[15px] text-text/90 leading-relaxed line-clamp-3">
                      {truncateText(item.content, 200)}
                    </p>

                    <div className="mt-4 flex justify-between items-center text-sm">
                      <div className="flex items-center gap-1">
                        {getImportanceStars(item.importance)}
                      </div>
                      <span className="text-gray-500 dark:text-gray-400">{categories.find(c => c.id === item.category)?.label}</span>
                      <button 
                        className="text-primary font-medium hover:underline flex items-center gap-1"
                        onClick={() => setSelectedNews(item)}
                      >
                        Читать
                        <ExternalLink className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.section>

        {/* Loading indicator for infinite scroll */}
        {filteredNews.length > 0 && hasMoreNews && loadingMore && (
          <motion.section variants={itemVariants} className="text-center py-8">
            <div className="flex items-center justify-center space-x-2 text-muted-strong">
              <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span>Загрузка новостей...</span>
            </div>
          </motion.section>
        )}

        {/* Load more hint */}
        {filteredNews.length > 0 && hasMoreNews && !loadingMore && (
          <motion.section variants={itemVariants} className="text-center py-4">
            <div className="text-muted-strong text-sm">
              <svg className="w-6 h-6 mx-auto mb-2 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
              </svg>
              <p>Прокрутите вниз для загрузки новых новостей</p>
            </div>
          </motion.section>
        )}

        {/* End of news indicator */}
        {filteredNews.length > 0 && !hasMoreNews && (
          <motion.section variants={itemVariants} className="text-center py-8">
            <div className="text-muted-strong">
              <svg className="w-8 h-8 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              <p>Все новости загружены</p>
              <p className="text-sm mt-1">Обновите страницу для получения новых новостей</p>
            </div>
          </motion.section>
        )}

                {/* Empty State с динамическими сообщениями */}
                {filteredNews.length === 0 && !loading && (
                  <motion.section variants={itemVariants} className="text-center py-20">
                    <div className="flex justify-center mb-4">
                      <Newspaper className="w-16 h-16 text-muted" />
                    </div>
                    <h3 className="text-xl font-semibold text-text mb-2">
                      {selectedCategory === 'all' 
                        ? 'Новости не найдены'
                        : `Нет новостей в категории "${categories.find(c => c.id === selectedCategory)?.label}"`
                      }
                    </h3>
                    <p className="text-muted-strong mb-6">
                      {selectedSubcategory 
                        ? 'Попробуйте выбрать другую подкатегорию'
                        : selectedCategory !== 'all'
                          ? 'Попробуйте выбрать другую категорию или посмотрите все новости'
                          : 'Попробуйте позже или измените фильтры'
                      }
                    </p>
                    {selectedCategory !== 'all' && (
                      <Button 
                        variant="secondary" 
                        onClick={() => handleCategorySelect('all')}
                      >
                        Показать все новости
                      </Button>
                    )}
                  </motion.section>
                )}

                {/* Индикатор при малом количестве новостей */}
                {filteredNews.length > 0 && filteredNews.length < 10 && !hasMoreNews && !loading && (
                  <motion.section variants={itemVariants}>
                    <div className="text-center py-4">
                      <p className="text-sm text-muted-strong">
                        💡 Найдено всего {filteredNews.length} {getNewsLabel(filteredNews.length)} по выбранным фильтрам.
                        {selectedCategory !== 'all' && ' Попробуйте расширить критерии поиска.'}
                      </p>
                    </div>
                  </motion.section>
                )}
        </motion.div>
      </main>

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

      {/* News Modal */}
      {selectedNews && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="w-full max-w-2xl max-h-[75vh] 
                       card backdrop-blur-lg rounded-3xl 
                       shadow-[0_8px_32px_rgba(0,0,0,0.12)] dark:shadow-[0_8px_32px_rgba(0,0,0,0.4)]
                       p-6 
                       overflow-hidden flex flex-col"
          >
            {/* Close button */}
            <button 
              className="absolute top-4 right-4 p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              onClick={() => setSelectedNews(null)}
            >
              <X className="w-5 h-5 text-gray-500 dark:text-gray-400" />
            </button>

            {/* Category and source */}
            <div className="flex gap-2 text-sm mb-3">
              <span className="text-primary font-medium">
                {categories.find(c => c.id === selectedNews.category)?.label}
              </span>
              <span className="text-gray-400 dark:text-gray-500">•</span>
              {selectedNews.url ? (
                <a 
                  href={selectedNews.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-primary/80 hover:text-primary font-medium underline-offset-2"
                >
                  {selectedNews.source}
                </a>
              ) : (
                <span className="text-gray-500 dark:text-gray-400">{selectedNews.source}</span>
              )}
            </div>

            {/* Title */}
            <h2 className="text-xl md:text-2xl font-semibold text-text dark:text-white tracking-tight leading-snug mb-3">
              {selectedNews.title}
            </h2>

            {/* Content - scrollable */}
            <div className="flex-1 overflow-y-auto mb-5">
              <p className="text-[15px] leading-relaxed text-text/90 dark:text-gray-300 whitespace-pre-wrap">
                {selectedNews.content}
              </p>
            </div>

            {/* Footer - simplified */}
            <div className="border-t border-gray-200 dark:border-gray-600 pt-4 mt-4 flex items-center justify-between text-xs text-gray-400 dark:text-gray-500">
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <span>{Math.round(selectedNews.credibility * 100)}%</span>
                </div>
                <div className="flex items-center gap-1">
                  <Star className="w-3 h-3 text-amber-400" />
                  <span>{Math.round(selectedNews.importance * 100)}%</span>
                </div>
              </div>
              <div className="text-gray-400 dark:text-gray-500">
                {new Date(selectedNews.publishedAt).toLocaleDateString('ru-RU')}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default NewsPage;
