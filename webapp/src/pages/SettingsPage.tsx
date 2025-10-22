import { motion } from 'framer-motion';
import { Settings } from 'lucide-react';
import React, { useMemo } from 'react';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/Card';
import { Header } from '../components/ui/Header';
import { useAuth } from '../context/AuthContext';
import { useTelegramUser } from '../hooks/useTelegramUser';
import { useUserPreferences } from '../hooks/useUserPreferences';

interface Category {
    id: string;
    name: string;
    icon: string;
    enabled: boolean;
    subcategories: {
        id: string;
        name: string;
        enabled: boolean;
    }[];
}

interface SettingsPageProps {
    theme: 'light' | 'dark';
    onThemeToggle: () => void;
}

const SettingsPage: React.FC<SettingsPageProps> = () => {
    // Get user data from Telegram WebApp
    const { userData } = useTelegramUser();
    const { authHeaders } = useAuth();
    const userId = userData?.user_id || '';

    // Use preferences hook with userId and authHeaders
    const {
        preferences: userPreferences,
        categoriesStructure,
        loading: preferencesLoading,
        error: preferencesError,
        updatePreferences
    } = useUserPreferences(userId, authHeaders);

    // Map preferences to UI format with useMemo for performance
    const categories = useMemo(() => {
        if (!categoriesStructure) return [];

        return Object.entries(categoriesStructure).map(([catId, catData]: [string, any]) => {
            const userCatPref = userPreferences ? userPreferences[catId] : undefined;

            // Default behavior: if no preferences set, enable all categories
            // Category enabled if: no preference (undefined), null (all), or array with items
            const categoryEnabled = userCatPref === undefined || userCatPref === null || (Array.isArray(userCatPref) && userCatPref.length > 0);

            // Map subcategories
            const subcategories = Object.entries(catData.subcategories || {}).map(([subId, subData]: [string, any]) => {
                let subEnabled = false;

                if (userCatPref === undefined || userCatPref === null) {
                    // If no preference or category is "all", all subcategories enabled
                    subEnabled = true;
                } else if (Array.isArray(userCatPref)) {
                    // If specific subcategories selected
                    subEnabled = userCatPref.includes(subId);
                }

                return {
                    id: subId,
                    name: subData.name || subId,
                    enabled: subEnabled
                };
            });

            return {
                id: catId,
                name: catData.name || catId,
                icon: catData.emoji || '📁',
                enabled: categoryEnabled,
                subcategories
            };
        });
    }, [categoriesStructure, userPreferences]);


    const savePreferences = async (updatedCategories: Category[]) => {
        try {
            // Convert UI format to API format (JSONB)
            const preferences: Record<string, string[] | null> = {};

            updatedCategories.forEach(cat => {
                if (!cat.enabled) {
                    // Category disabled = empty array
                    preferences[cat.id] = [];
                } else {
                    // Check if all subcategories enabled
                    const enabledSubs = cat.subcategories.filter(sub => sub.enabled);
                    const allEnabled = enabledSubs.length === cat.subcategories.length;

                    if (allEnabled) {
                        // All subcategories = null (entire category)
                        preferences[cat.id] = null;
                    } else if (enabledSubs.length > 0) {
                        // Specific subcategories
                        preferences[cat.id] = enabledSubs.map(sub => sub.id);
                    } else {
                        // No subcategories enabled = disabled
                        preferences[cat.id] = [];
                    }
                }
            });

            // Use the hook's updatePreferences method
            await updatePreferences(preferences);
        } catch (error) {
            console.error('Error saving preferences:', error);
        }
    };

    const toggleCategory = (categoryId: string) => {
        const updated = categories.map(cat => {
            if (cat.id === categoryId) {
                const newEnabled = !cat.enabled;
                // If category is disabled, disable all subcategories
                const updatedSubcategories = cat.subcategories.map(sub => ({
                    ...sub,
                    enabled: newEnabled,
                }));
                return { ...cat, enabled: newEnabled, subcategories: updatedSubcategories };
            }
            return cat;
        });
        // Save preferences (will trigger useMemo recalculation)
        savePreferences(updated);
    };

    const toggleSubcategory = (categoryId: string, subcategoryId: string) => {
        const updated = categories.map(cat => {
            if (cat.id === categoryId) {
                const updatedSubcategories = cat.subcategories.map(sub => {
                    if (sub.id === subcategoryId) {
                        return { ...sub, enabled: !sub.enabled };
                    }
                    return sub;
                });

                // If all subcategories are disabled, disable the parent category
                const allSubcategoriesDisabled = updatedSubcategories.every(sub => !sub.enabled);
                const newCategoryEnabled = !allSubcategoriesDisabled;

                return { ...cat, enabled: newCategoryEnabled, subcategories: updatedSubcategories };
            }
            return cat;
        });
        // Save preferences (will trigger useMemo recalculation)
        savePreferences(updated);
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
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: {
                type: 'spring' as const,
                stiffness: 100,
                damping: 10,
            },
        },
    };

    if (preferencesLoading) {
        return (
            <div className="min-h-screen bg-bg">
                <Header
                    title="Настройки"
                    subtitle="Персонализация категорий"
                    icon={<Settings className="w-6 h-6 text-primary" />}
                />
                <main className="container-main">
                    <div className="space-y-4">
                        {[1, 2, 3].map((i) => (
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

    // Show error state
    if (preferencesError) {
        return (
            <div className="min-h-screen bg-bg">
                <Header
                    title="Настройки"
                    subtitle="Настрой под себя"
                    icon={<Settings className="w-6 h-6 text-primary" />}
                />
                <main className="container-main">
                    <Card>
                        <CardContent className="text-center py-8">
                            <p className="text-red-500 mb-4">Не удалось загрузить настройки</p>
                            <p className="text-sm text-gray-500 mb-4">{preferencesError}</p>
                            <Button
                                onClick={() => window.location.reload()}
                                variant="outline"
                            >
                                Обновить
                            </Button>
                        </CardContent>
                    </Card>
                </main>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-bg">
            <Header
                title="Настройки"
                subtitle="Настрой под себя"
                icon={<Settings className="w-6 h-6 text-primary" />}
            />

            <main className="container-main">
                <motion.div
                    variants={containerVariants}
                    initial="hidden"
                    animate="visible"
                    className="space-y-6"
                >
                    {/* Info Block */}
                    <motion.section variants={itemVariants}>
                        <div className="bg-primary/10 border border-primary/20 rounded-lg p-4">
                            <p className="text-sm text-text">
                                ✨ Выбери категории, которые тебе интересны. Всё сохраняется автоматически
                            </p>
                        </div>
                    </motion.section>

                    {/* Categories */}
                    <motion.section variants={itemVariants}>
                        <Card>
                            <CardHeader>
                                <CardTitle className="text-lg">Твои темы</CardTitle>
                                <CardDescription>
                                    Выбери, что хочешь видеть в новостях и событиях
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="space-y-4">
                                    {categories.map((category) => (
                                        <div key={category.id} className="border border-border rounded-lg p-4">
                                            <div className="flex items-center justify-between mb-3">
                                                <div className="flex items-center space-x-3">
                                                    <span className="text-2xl">{category.icon}</span>
                                                    <div>
                                                        <h4 className="font-medium text-text">{category.name}</h4>
                                                        <p className="text-sm text-muted-strong">
                                                            {category.subcategories.filter(sub => sub.enabled).length} из {category.subcategories.length} подкатегорий
                                                        </p>
                                                    </div>
                                                </div>
                                                <Button
                                                    variant={category.enabled ? 'primary' : 'secondary'}
                                                    size="sm"
                                                    onClick={() => toggleCategory(category.id)}
                                                >
                                                    {category.enabled ? 'Включено' : 'Выключено'}
                                                </Button>
                                            </div>

                                            {category.enabled && (
                                                <div className="space-y-2">
                                                    <p className="text-xs text-muted-strong mb-2">Подкатегории:</p>
                                                    <div className="grid grid-cols-2 gap-2">
                                                        {category.subcategories.map((subcategory) => (
                                                            <Button
                                                                key={subcategory.id}
                                                                variant={subcategory.enabled ? 'primary' : 'outline'}
                                                                size="sm"
                                                                onClick={() => toggleSubcategory(category.id, subcategory.id)}
                                                                className="justify-start text-sm"
                                                            >
                                                                {subcategory.name}
                                                            </Button>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </CardContent>
                        </Card>
                    </motion.section>

                    {/* Coming Soon: Notifications */}
                    <motion.section variants={itemVariants}>
                        <Card className="opacity-60 pointer-events-none">
                            <CardHeader>
                                <CardTitle className="text-lg flex items-center justify-between">
                                    Уведомления
                                    <span className="text-sm text-primary font-normal">Скоро</span>
                                </CardTitle>
                                <CardDescription>
                                    Push-уведомления, email-дайджесты и настройка частоты
                                </CardDescription>
                            </CardHeader>
                        </Card>
                    </motion.section>

                    {/* Coming Soon: Profile */}
                    <motion.section variants={itemVariants}>
                        <Card className="opacity-60 pointer-events-none">
                            <CardHeader>
                                <CardTitle className="text-lg flex items-center justify-between">
                                    Профиль
                                    <span className="text-sm text-primary font-normal">Скоро</span>
                                </CardTitle>
                                <CardDescription>
                                    Имя, email, часовой пояс и другие настройки
                                </CardDescription>
                            </CardHeader>
                        </Card>
                    </motion.section>
                </motion.div>
            </main>
        </div>
    );
};

export default SettingsPage;
