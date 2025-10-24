/**
 * Утилиты для форматирования текста и чисел
 */

/**
 * Склонение числительных в русском языке
 * @param count - количество
 * @param forms - формы слова [1, 2-4, 5+] например ["новость", "новости", "новостей"]
 * @returns правильная форма слова
 */
export function pluralizeRu(count: number, forms: [string, string, string]): string {
    const mod10 = count % 10;
    const mod100 = count % 100;

    if (mod10 === 1 && mod100 !== 11) {
        return forms[0]; // 1 новость
    } else if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) {
        return forms[1]; // 2-4 новости
    } else {
        return forms[2]; // 5-0 новостей
    }
}

/**
 * Форматирование счётчика с правильным склонением
 * @param count - количество
 * @param forms - формы слова
 * @returns отформатированная строка
 */
export function formatCount(count: number, forms: [string, string, string]): string {
    if (count === 0) {
        return `Нет ${forms[2]}`;
    }

    if (count >= 100) {
        return `${count}+ ${pluralizeRu(count, forms)}`;
    }

    return `${count} ${pluralizeRu(count, forms)}`;
}

/**
 * Предустановленные формы для основных сущностей
 */
export const PLURAL_FORMS = {
    NEWS: ["новость", "новости", "новостей"] as [string, string, string],
    EVENTS: ["событие", "события", "событий"] as [string, string, string],
    DIGESTS: ["дайджест", "дайджеста", "дайджестов"] as [string, string, string],
} as const;
