/**
 * Централизованные переводы для PulseAI
 * Гибридный подход: API возвращает только ID, frontend переводит
 */

export const translations = {
    ru: {
        categories: {
            crypto: "Криптовалюты",
            sports: "Спорт и киберспорт",
            markets: "Финансы",
            tech: "Технологии",
            world: "Мир",
            all: "Все"
        },
        subcategories: {
            // Sports (21)
            american_football: "Американский футбол",
            football: "Футбол",
            basketball: "Баскетбол",
            tennis: "Теннис",
            hockey: "Хоккей",
            cricket: "Крикет",
            rugby: "Регби",
            volleyball: "Волейбол",
            handball: "Гандбол",
            badminton: "Бадминтон",
            table_tennis: "Настольный теннис",
            mma: "MMA/UFC",
            boxing: "Бокс",
            formula1: "Формула 1",
            baseball: "Бейсбол",
            ufc_mma: "MMA/UFC",
            r6siege: "Rainbow Six Siege",
            dota2: "Dota 2",
            csgo: "CS:GO",
            lol: "League of Legends",
            valorant: "Valorant",
            overwatch: "Overwatch",
            esports: "Киберспорт",
            esports_general: "Киберспорт общий",
            fifa_esports: "FIFA киберспорт",
            pubg: "PUBG",
            rocket_league: "Rocket League",
            starcraft: "StarCraft",
            other: "Другое",
            general: "Общее",

            // Crypto (16)
            bitcoin: "Bitcoin",
            ethereum: "Ethereum",
            defi: "DEX",
            nft: "NFT",
            altcoins: "Альткоины",
            exchanges: "Биржи",
            regulation: "Регулирование",
            security: "Безопасность",
            layer2: "Layer 2",
            dao: "DAO",
            token_unlock: "Разблокировки токенов",
            listing: "Листинги",
            airdrop: "Airdrop",
            mainnet: "Запуск Mainnet",
            hard_fork: "Хардфорки",
            protocol_upgrade: "Обновления протокола",
            gamefi: "GameFi",
            market_trends: "Рыночные тренды",

            // Markets (15)
            stocks: "Акции",
            forex: "Валюты",
            commodities: "Сырьё",
            bonds: "Облигации",
            earnings: "Отчёты",
            dividends: "Дивиденды",
            ipo: "IPO",
            ipos: "IPO",
            economic_data: "Экономика",
            central_banks: "Центробанки",
            monetary_policy: "Денежная политика",
            employment: "Занятость",
            inflation: "Инфляция",
            gdp: "ВВП",
            manufacturing: "Производство (PMI)",
            retail_sales: "Розничные продажи",
            economic_calendar: "Экономический календарь",
            funds_etfs: "Фонды и ETF",
            rates: "Процентные ставки",
            splits: "Сплиты акций",

            // Tech (12)
            ai: "ИИ",
            software_release: "Релизы ПО",
            hardware: "Железо",
            startup: "Стартапы",
            conference: "Конференции",
            cybersecurity: "Кибербезопасность",
            blockchain_tech: "Блокчейн-технологии",
            open_source: "Open Source",
            cloud: "Облако",
            mobile: "Мобильное",
            bigtech: "Большие компании",
            software: "Программное обеспечение",
            startups: "Стартапы",
            conferences: "Конференции",

            // World (11)
            elections: "Выборы",
            politics: "Политика",
            climate: "Климат",
            un_meetings: "Встречи ООН",
            sanctions: "Санкции",
            g7_g20: "G7/G20",
            eu_council: "Совет ЕС",
            trade_agreements: "Торговые соглашения",
            environment: "Экология",
            conflicts: "Конфликты",
            diplomacy: "Дипломатия",
            energy: "Энергетика",
            geopolitics: "Геополитика",
            global_risks: "Глобальные риски",
            migration: "Миграция",
            organizations: "Международные организации",
        }
    },
    en: {
        categories: {
            crypto: "Cryptocurrency",
            sports: "Sports & Esports",
            markets: "Financial Markets",
            tech: "Technology",
            world: "World Events",
            all: "All"
        },
        subcategories: {
            // Для будущего расширения
            american_football: "American Football",
            football: "Football",
            basketball: "Basketball",
            tennis: "Tennis",
            hockey: "Hockey",
            dota2: "Dota 2",
            csgo: "CS:GO",
            lol: "League of Legends",
            overwatch: "Overwatch",
            esports: "Esports",
            bitcoin: "Bitcoin",
            ethereum: "Ethereum",
            defi: "DEX",
            nft: "NFT",
            general: "General",
            other: "Other"
        }
    }
};

/**
 * Получить переведённое название категории
 * @param id - ID категории
 * @param locale - Язык (по умолчанию 'ru')
 * @returns Переведённое название или ID если перевод не найден
 */
export function getCategoryName(id: string, locale: string = 'ru'): string {
    return (translations as any)[locale]?.categories[id] || id;
}

/**
 * Получить переведённое название подкатегории
 * @param id - ID подкатегории
 * @param locale - Язык (по умолчанию 'ru')
 * @returns Переведённое название или ID если перевод не найден
 */
export function getSubcategoryName(id: string, locale: string = 'ru'): string {
    return (translations as any)[locale]?.subcategories[id] || id;
}

/**
 * Получить все доступные языки
 */
export function getAvailableLocales(): string[] {
    return Object.keys(translations);
}

/**
 * Проверить, поддерживается ли язык
 */
export function isLocaleSupported(locale: string): boolean {
    return locale in translations;
}
