import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { MobileHeader } from '../components/ui/Header';
import { 
  Newspaper, 
  Cpu, 
  Globe, 
  TrendingUp, 
  Coins, 
  Trophy, 
  ExternalLink,
  X,
  Star
} from 'lucide-react';

interface NewsItem {
  id: string;
  title: string;
  content: string;
  source: string;
  category: string;
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

const NewsPage: React.FC<NewsPageProps> = ({ onNavigate: _onNavigate }) => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMoreNews, setHasMoreNews] = useState(true);

  const categories = [
    { id: 'all', label: 'Все', icon: <Newspaper className="w-4 h-4" /> },
    { id: 'crypto', label: 'Криптовалюты', icon: <Coins className="w-4 h-4" /> },
    { id: 'tech', label: 'AI и технологии', icon: <Cpu className="w-4 h-4" /> },
    { id: 'sports', label: 'Спорт и события', icon: <Trophy className="w-4 h-4" /> },
    { id: 'world', label: 'Новости мира', icon: <Globe className="w-4 h-4" /> },
    { id: 'markets', label: 'Финансы', icon: <TrendingUp className="w-4 h-4" /> },
  ];


  const fetchNews = async (page: number = 1, isRefresh: boolean = false) => {
    try {
      if (isRefresh) {
        // setIsRefreshing удален
      } else if (page === 1) {
        setLoading(true);
      } else {
        setLoadingMore(true);
      }

      console.log(`🔍 Fetching news: /api/latest?page=${page}&limit=20`);
      const response = await fetch(`/api/latest?page=${page}&limit=20`);
      
      console.log(`📡 Response status: ${response.status}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`📊 API response:`, data);
      
      if (data.status === 'success') {
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
      
             // Fallback to mock data if API fails
                    const now = new Date();
                    const fallbackNews: NewsItem[] = [
                      {
                        id: '1',
                        title: 'Bitcoin достигает новых максимумов на фоне институционального интереса',
                        content: 'Криптовалюта Bitcoin показала значительный рост в последние дни, достигнув новых максимумов...',
                        source: 'CoinDesk',
                        category: 'crypto',
                        publishedAt: new Date(now.getTime() - 2 * 60 * 60 * 1000).toISOString(), // 2 часа назад
                        credibility: 0.92,
                        importance: 0.88,
                        url: 'https://example.com/bitcoin-news',
                      },
                      {
                        id: '2',
                        title: 'ИИ-революция: новые достижения в области машинного обучения',
                        content: 'Исследователи представили новую архитектуру нейронных сетей, которая может...',
                        source: 'TechCrunch',
                        category: 'tech',
                        publishedAt: new Date(now.getTime() - 4 * 60 * 60 * 1000).toISOString(), // 4 часа назад
                        credibility: 0.89,
                        importance: 0.85,
                        url: 'https://example.com/ai-news',
                      },
                      {
                        id: '3',
                        title: 'Чемпионат мира по футболу: обновления и результаты',
                        content: 'Вчера состоялись ключевые матчи чемпионата мира по футболу...',
                        source: 'ESPN',
                        category: 'sports',
                        publishedAt: new Date(now.getTime() - 6 * 60 * 60 * 1000).toISOString(), // 6 часов назад
                        credibility: 0.95,
                        importance: 0.72,
                        url: 'https://example.com/sports-news',
                      },
                    ];
      
      setNews(fallbackNews);
      setHasMoreNews(false);
    } finally {
      setLoading(false);
      setLoadingMore(false);
      // setIsRefreshing удален
    }
  };

  useEffect(() => {
    fetchNews(1);
  }, []);

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

  // Infinite scroll functionality
  useEffect(() => {
    const handleScroll = () => {
      // Более точная проверка достижения низа
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      const scrollHeight = document.documentElement.scrollHeight;
      const clientHeight = window.innerHeight;
      
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

    // Добавляем throttling для производительности
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
  }, [hasMoreNews, loadingMore, loading]);

  const filteredNews = news.filter(item => {
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    return matchesCategory;
  });

  const truncateText = (text: string, maxLength: number = 200): string => {
    if (text.length <= maxLength) {
      return text;
    }
    return text.substring(0, maxLength).trim() + '...';
  };

  const getImportanceStars = (importance: number) => {
    const stars = Math.round(importance * 5);
    return '⭐'.repeat(stars) + '☆'.repeat(5 - stars);
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
    },
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-bg">
        <MobileHeader title="Новости" subtitle="Загрузка..." />
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
      <MobileHeader 
        title="Новости" 
        subtitle={`${filteredNews.length} ${getNewsLabel(filteredNews.length)}`}
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
          {/* Category Filters */}
          <motion.section variants={itemVariants}>
            <Card>
              <CardContent className="pt-6">
                <div className="flex flex-wrap gap-2 overflow-x-auto">
                  {categories.map((category) => (
                    <button
                      key={category.id}
                      className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 flex items-center ${
                        selectedCategory === category.id
                          ? "bg-gradient-to-r from-[#00BFA6]/10 to-[#00E3BE]/10 text-primary shadow-[0_0_6px_rgba(0,191,166,0.2)]"
                          : "border border-border text-gray-600 dark:text-gray-300 hover:text-primary hover:border-primary/50"
                      }`}
                      onClick={() => setSelectedCategory(category.id)}
                    >
                      <span className="mr-2">{category.icon}</span>
                      {category.label}
                    </button>
                  ))}
                </div>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-3 text-center">
                  PulseAI отбирает новости с наибольшей вероятностью интереса.
                </p>
              </CardContent>
            </Card>
          </motion.section>

          {/* News List */}
          <motion.section variants={itemVariants}>
            <div className="space-y-4">
              {filteredNews.map((item, index) => (
                <motion.div
                  key={item.id}
                  variants={itemVariants}
                  transition={{ delay: index * 0.1 }}
                >
                  <div className="bg-white dark:bg-surface-alt rounded-3xl shadow-[0_2px_12px_rgba(0,0,0,0.04)] hover:shadow-[0_6px_20px_rgba(0,0,0,0.06)] transition-all duration-300 hover:scale-[1.01] p-5">
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
                </motion.div>
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

                {/* Empty State */}
                {filteredNews.length === 0 && (
                  <motion.section variants={itemVariants} className="text-center py-20">
                    <div className="flex justify-center mb-4">
                      <Newspaper className="w-16 h-16 text-muted" />
                    </div>
                    <h3 className="text-xl font-semibold text-text mb-2">
                      Новости не найдены
                    </h3>
                    <p className="text-muted-strong mb-6">
                      Выберите другую категорию для просмотра новостей
                    </p>
                    <Button 
                      variant="secondary" 
                      onClick={() => setSelectedCategory('all')}
                    >
                      Показать все новости
                    </Button>
                  </motion.section>
                )}
        </motion.div>
      </main>

      {/* News Modal */}
      {selectedNews && (
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
