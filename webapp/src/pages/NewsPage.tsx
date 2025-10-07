import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { MobileHeader } from '../components/ui/Header';

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

const NewsPage: React.FC<NewsPageProps> = ({ onNavigate: _onNavigate }) => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMoreNews, setHasMoreNews] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const categories = [
    { id: 'all', label: 'Все', icon: '📰' },
    { id: 'crypto', label: 'Криптовалюты', icon: '₿' },
    { id: 'tech', label: 'Технологии', icon: '🤖' },
    { id: 'sports', label: 'Спорт', icon: '⚽' },
    { id: 'world', label: 'Мир', icon: '🌍' },
    { id: 'markets', label: 'Рынки', icon: '📈' },
  ];


  const fetchNews = async (page: number = 1, isRefresh: boolean = false) => {
    try {
      if (isRefresh) {
        setIsRefreshing(true);
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
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchNews(1);
  }, []);

  const loadMoreNews = async () => {
    if (!hasMoreNews || loadingMore) return;
    
    const nextPage = currentPage + 1;
    await fetchNews(nextPage);
  };

  const handleRefresh = async () => {
    await fetchNews(1, true);
  };

  // Pull-to-refresh and infinite scroll functionality
  const [pullDistance, setPullDistance] = useState(0);
  const [isPulling, setIsPulling] = useState(false);
  const [startY, setStartY] = useState(0);

  const handleTouchStart = (e: React.TouchEvent) => {
    setStartY(e.touches[0].clientY);
    setIsPulling(false);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    const currentY = e.touches[0].clientY;
    const distance = currentY - startY; // Исправлено: нормальная логика для свайпа снизу
    
    // Проверяем что мы внизу страницы (scrollY близко к максимальному значению)
    const isAtBottom = window.innerHeight + window.scrollY >= document.body.offsetHeight - 10;
    
    if (distance > 0 && isAtBottom) {
      setIsPulling(true);
      setPullDistance(Math.min(distance, 100)); // Max pull distance
    }
  };

  const handleTouchEnd = () => {
    if (pullDistance > 50 && !isRefreshing) {
      handleRefresh();
    }
    setPullDistance(0);
    setIsPulling(false);
  };

  // Infinite scroll functionality
  useEffect(() => {
    const handleScroll = () => {
      // Проверяем что мы близко к низу страницы
      const isAtBottom = window.innerHeight + window.scrollY >= document.body.offsetHeight - 100;
      
      // Загружаем следующую страницу если есть еще новости и не идет загрузка
      if (isAtBottom && hasMoreNews && !loadingMore && !loading) {
        loadMoreNews();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [hasMoreNews, loadingMore, loading]);

  const filteredNews = news.filter(item => {
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    return matchesCategory;
  });

  const getCredibilityColor = (credibility: number) => {
    if (credibility >= 0.9) return 'text-success';
    if (credibility >= 0.7) return 'text-warning';
    return 'text-error';
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
        subtitle={`${filteredNews.length} новостей`}
      />
      
      <main 
        className="container-main"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Pull-to-refresh indicator - positioned at bottom */}
        {isPulling && (
          <div 
            className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-center bg-primary/10 backdrop-blur-sm"
            style={{ height: `${Math.max(pullDistance, 60)}px` }}
          >
            <div className="flex items-center space-x-2 text-primary">
              {isRefreshing ? (
                <>
                  <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span>Обновление...</span>
                </>
              ) : (
                <>
                  <svg className={`h-5 w-5 transition-transform ${pullDistance > 50 ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                  <span>{pullDistance > 50 ? 'Отпустите для обновления' : 'Потяните вверх для обновления'}</span>
                </>
              )}
            </div>
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
                <div className="flex flex-wrap gap-2">
                  {categories.map((category) => (
                    <Button
                      key={category.id}
                      variant={selectedCategory === category.id ? 'primary' : 'secondary'}
                      size="sm"
                      onClick={() => setSelectedCategory(category.id)}
                    >
                      <span className="mr-1">{category.icon}</span>
                      {category.label}
                    </Button>
                  ))}
                </div>
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
                  <Card className="hover-lift">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <CardTitle className="text-lg leading-tight mb-2">
                            {item.title}
                          </CardTitle>
                          <CardDescription>
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
                          </CardDescription>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <div className={`text-xs ${getCredibilityColor(item.credibility)}`}>
                            {Math.round(item.credibility * 100)}%
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent>
                      <p className="text-text text-sm leading-relaxed mb-4">
                        {item.content}
                      </p>
                      
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="text-xs text-muted-strong">
                            Важность: {getImportanceStars(item.importance)}
                          </div>
                          <div className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                            {categories.find(c => c.id === item.category)?.label}
                          </div>
                        </div>
                        
                        <Button 
                          variant="ghost" 
                          size="sm"
                          onClick={() => setSelectedNews(item)}
                        >
                          Читать далее
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
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
              <p className="text-sm mt-1">Потяните вверх для обновления</p>
            </div>
          </motion.section>
        )}

                {/* Empty State */}
                {filteredNews.length === 0 && (
                  <motion.section variants={itemVariants} className="text-center py-20">
                    <div className="text-6xl mb-4">📰</div>
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
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="bg-surface rounded-xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <span className="text-sm bg-primary/10 text-primary px-2 py-1 rounded-full">
                    {categories.find(c => c.id === selectedNews.category)?.label}
                  </span>
                  <span className="text-sm text-muted-strong">
                    {selectedNews.url ? (
                      <a 
                        href={selectedNews.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-primary hover:text-primary/80 underline"
                      >
                        {selectedNews.source}
                      </a>
                    ) : (
                      selectedNews.source
                    )}
                  </span>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedNews(null)}
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </Button>
              </div>
              
              <h2 className="text-xl font-semibold text-text mb-4">
                {selectedNews.title}
              </h2>
              
              <div className="prose prose-sm max-w-none text-text mb-6">
                <p className="leading-relaxed">
                  {selectedNews.content}
                </p>
              </div>
              
              <div className="flex items-center justify-between pt-4 border-t border-border">
                <div className="flex items-center space-x-4">
                  <div className="text-xs text-muted-strong">
                    Достоверность: {Math.round(selectedNews.credibility * 100)}%
                  </div>
                  <div className="text-xs text-muted-strong">
                    Важность: {'⭐'.repeat(Math.round(selectedNews.importance * 5))}
                  </div>
                </div>
                <div className="text-xs text-muted-strong">
                  {new Date(selectedNews.publishedAt).toLocaleDateString('ru-RU', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

export default NewsPage;
