import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { MobileHeader } from '../components/ui/Header';

interface DigestItem {
  id: string;
  title: string;
  summary: string;
  category: string;
  sources: string[];
  createdAt: string;
  readTime: number;
  keyPoints: string[];
}

const DigestPage: React.FC = () => {
  const [digests, setDigests] = useState<DigestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');

  const categories = [
    { id: 'all', label: 'Все', icon: '📰' },
    { id: 'crypto', label: 'Криптовалюты', icon: '₿' },
    { id: 'tech', label: 'Технологии', icon: '🤖' },
    { id: 'sports', label: 'Спорт', icon: '⚽' },
    { id: 'world', label: 'Мир', icon: '🌍' },
  ];

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

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setDigests(mockDigests);
      setLoading(false);
    }, 1000);
  }, []);

  const filteredDigests = digests.filter(item => 
    selectedCategory === 'all' || item.category === selectedCategory
  );

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
      <MobileHeader 
        title="AI Дайджест" 
        subtitle={`${filteredDigests.length} дайджестов`}
        actions={
          <Button variant="ghost" size="sm">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
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

          {/* Digest List */}
          <motion.section variants={itemVariants}>
            <div className="space-y-6">
              {filteredDigests.map((digest, index) => (
                <motion.div
                  key={digest.id}
                  variants={itemVariants}
                  transition={{ delay: index * 0.1 }}
                >
                  <Card className="hover-lift">
                    <CardHeader>
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <CardTitle className="text-xl leading-tight mb-2">
                            {digest.title}
                          </CardTitle>
                          <CardDescription>
                            {new Date(digest.createdAt).toLocaleDateString('ru-RU', {
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </CardDescription>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <div className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                            {categories.find(c => c.id === digest.category)?.icon} {categories.find(c => c.id === digest.category)?.label}
                          </div>
                          <div className="text-xs text-muted">
                            {digest.readTime} мин
                          </div>
                        </div>
                      </div>
                    </CardHeader>
                    
                    <CardContent>
                      <p className="text-text text-base leading-relaxed mb-4">
                        {digest.summary}
                      </p>
                      
                      {/* Key Points */}
                      <div className="mb-4">
                        <h4 className="text-sm font-semibold text-text mb-2">Ключевые моменты:</h4>
                        <ul className="space-y-1">
                          {digest.keyPoints.map((point, idx) => (
                            <li key={idx} className="flex items-start space-x-2 text-sm text-text">
                              <span className="text-primary mt-1">•</span>
                              <span>{point}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      {/* Sources */}
                      <div className="mb-4">
                        <h4 className="text-sm font-semibold text-text mb-2">Источники:</h4>
                        <div className="flex flex-wrap gap-2">
                          {digest.sources.map((source, idx) => (
                            <span 
                              key={idx}
                              className="text-xs bg-surface-alt text-muted px-2 py-1 rounded-full"
                            >
                              {source}
                            </span>
                          ))}
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between pt-4 border-t border-border">
                        <Button variant="secondary" size="sm">
                          Поделиться
                        </Button>
                        <Button variant="primary" size="sm">
                          Читать полностью
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.section>

          {/* Generate New Digest */}
          <motion.section variants={itemVariants} className="text-center">
            <Card className="border-dashed border-2 border-border">
              <CardContent className="pt-8 pb-8">
                <div className="text-4xl mb-4">🤖</div>
                <h3 className="text-xl font-semibold text-text mb-2">
                  Создать новый дайджест
                </h3>
                <p className="text-muted mb-6 max-w-md mx-auto">
                  Сгенерируйте персональный дайджест на основе ваших интересов и предпочтений
                </p>
                <Button variant="primary" size="lg">
                  Создать дайджест
                </Button>
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
              <p className="text-muted mb-6">
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
    </div>
  );
};

export default DigestPage;
