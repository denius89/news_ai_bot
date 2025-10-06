import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
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
}

const NewsPage: React.FC = () => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', label: 'Все', icon: '📰' },
    { id: 'crypto', label: 'Криптовалюты', icon: '₿' },
    { id: 'tech', label: 'Технологии', icon: '🤖' },
    { id: 'sports', label: 'Спорт', icon: '⚽' },
    { id: 'world', label: 'Мир', icon: '🌍' },
    { id: 'markets', label: 'Рынки', icon: '📈' },
  ];

  // Mock data
  const mockNews: NewsItem[] = [
    {
      id: '1',
      title: 'Bitcoin достигает новых максимумов на фоне институционального интереса',
      content: 'Криптовалюта Bitcoin показала значительный рост в последние дни, достигнув новых максимумов...',
      source: 'CoinDesk',
      category: 'crypto',
      publishedAt: '2025-01-06T10:00:00Z',
      credibility: 0.92,
      importance: 0.88,
    },
    {
      id: '2',
      title: 'ИИ-революция: новые достижения в области машинного обучения',
      content: 'Исследователи представили новую архитектуру нейронных сетей, которая может...',
      source: 'TechCrunch',
      category: 'tech',
      publishedAt: '2025-01-06T09:30:00Z',
      credibility: 0.89,
      importance: 0.85,
    },
    {
      id: '3',
      title: 'Чемпионат мира по футболу: обновления и результаты',
      content: 'Вчера состоялись ключевые матчи чемпионата мира по футболу...',
      source: 'ESPN',
      category: 'sports',
      publishedAt: '2025-01-06T08:15:00Z',
      credibility: 0.95,
      importance: 0.72,
    },
  ];

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setNews(mockNews);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredNews = news.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.content.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory;
    return matchesSearch && matchesCategory;
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
      transition: {
        duration: 0.5,
        ease: 'easeOut',
      },
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
        actions={
          <Button variant="ghost" size="sm">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
            </svg>
          </Button>
        }
      />
      
      <main className="container-main">
        <motion.div
          variants={containerVariants}
          initial="hidden"
          animate="visible"
          className="space-y-6"
        >
          {/* Search and Filters */}
          <motion.section variants={itemVariants}>
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  <Input
                    placeholder="Поиск новостей..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    icon={
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    }
                  />
                  
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
                            {item.source} • {new Date(item.publishedAt).toLocaleDateString('ru-RU')}
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
                          <div className="text-xs text-muted">
                            Важность: {getImportanceStars(item.importance)}
                          </div>
                          <div className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                            {categories.find(c => c.id === item.category)?.label}
                          </div>
                        </div>
                        
                        <Button variant="ghost" size="sm">
                          Читать далее
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Load More */}
          {filteredNews.length > 0 && (
            <motion.section variants={itemVariants} className="text-center">
              <Button variant="secondary" size="lg" className="btn-full md:w-auto">
                Загрузить еще
              </Button>
            </motion.section>
          )}

          {/* Empty State */}
          {filteredNews.length === 0 && (
            <motion.section variants={itemVariants} className="text-center py-20">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold text-text mb-2">
                Новости не найдены
              </h3>
              <p className="text-muted mb-6">
                Попробуйте изменить поисковый запрос или выберите другую категорию
              </p>
              <Button 
                variant="secondary" 
                onClick={() => {
                  setSearchQuery('');
                  setSelectedCategory('all');
                }}
              >
                Сбросить фильтры
              </Button>
            </motion.section>
          )}
        </motion.div>
      </main>
    </div>
  );
};

export default NewsPage;
