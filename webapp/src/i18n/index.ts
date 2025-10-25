/**
 * Экспорт всех функций локализации
 */

export {
    getAvailableLocales, getCategoryName,
    getSubcategoryName, isLocaleSupported, translations
} from './translations';

export {
    translateCategory,
    translateSubcategory, useTranslation
} from './useTranslation';
