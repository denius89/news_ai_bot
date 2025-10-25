import { getAvailableLocales, getCategoryName, getSubcategoryName, isLocaleSupported } from './translations';

/**
 * Хук для работы с переводами
 * Пока использует фиксированный русский язык, в будущем можно добавить контекст для выбора языка
 */
export function useTranslation() {
    const locale = 'ru'; // Пока фиксированный, потом можно из контекста

    return {
        /**
         * Получить переведённое название категории
         */
        getCategoryName: (id: string) => getCategoryName(id, locale),

        /**
         * Получить переведённое название подкатегории
         */
        getSubcategoryName: (id: string) => getSubcategoryName(id, locale),

        /**
         * Текущий язык
         */
        locale,

        /**
         * Все доступные языки
         */
        availableLocales: getAvailableLocales(),

        /**
         * Проверить поддержку языка
         */
        isLocaleSupported: (lang: string) => isLocaleSupported(lang)
    };
}

/**
 * Утилитарная функция для перевода категории (без хука)
 * Полезно для использования вне React компонентов
 */
export function translateCategory(id: string, locale: string = 'ru'): string {
    return getCategoryName(id, locale);
}

/**
 * Утилитарная функция для перевода подкатегории (без хука)
 */
export function translateSubcategory(id: string, locale: string = 'ru'): string {
    return getSubcategoryName(id, locale);
}
