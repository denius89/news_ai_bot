/**
 * PulseAI Theme Management Utility
 * Handles theme switching with priority: user preference > Telegram > system
 */

export type Theme = 'light' | 'dark';

const THEME_STORAGE_KEY = 'pulseai-theme';

/**
 * Get current theme preference with priority:
 * 1. User localStorage preference
 * 2. Telegram WebApp colorScheme
 * 3. System preference
 */
export const getThemePreference = (): Theme => {
  // 1. Check user preference
  const storedTheme = localStorage.getItem(THEME_STORAGE_KEY) as Theme;
  if (storedTheme === 'light' || storedTheme === 'dark') {
    return storedTheme;
  }

  // 2. Check Telegram WebApp (if available)
  if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp?.colorScheme) {
    const telegramTheme = (window as any).Telegram.WebApp.colorScheme;
    return telegramTheme === 'dark' ? 'dark' : 'light';
  }

  // 3. Check system preference
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  // Default to light
  return 'light';
};

/**
 * Apply theme to document
 */
export const applyTheme = (theme: Theme): void => {
  const root = document.documentElement;
  
  if (theme === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
  
  // Update meta theme-color for mobile browsers
  const metaThemeColor = document.querySelector('meta[name="theme-color"]');
  if (metaThemeColor) {
    metaThemeColor.setAttribute('content', theme === 'dark' ? '#0F1115' : '#00BFA6');
  }
};

/**
 * Set theme preference and apply it
 */
export const setTheme = (theme: Theme): void => {
  localStorage.setItem(THEME_STORAGE_KEY, theme);
  applyTheme(theme);
};

/**
 * Toggle between light and dark theme
 */
export const toggleTheme = (): Theme => {
  const currentTheme = getThemePreference();
  const newTheme = currentTheme === 'light' ? 'dark' : 'light';
  setTheme(newTheme);
  return newTheme;
};

/**
 * Initialize theme system
 * Should be called once on app startup
 */
export const initializeTheme = (): Theme => {
  const theme = getThemePreference();
  applyTheme(theme);
  
  // Listen for system theme changes
  if (typeof window !== 'undefined' && window.matchMedia) {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleSystemThemeChange = (e: MediaQueryListEvent) => {
      // Only update if user hasn't set a preference
      const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
      if (!storedTheme) {
        const systemTheme = e.matches ? 'dark' : 'light';
        applyTheme(systemTheme);
      }
    };
    
    mediaQuery.addEventListener('change', handleSystemThemeChange);
    
    // Cleanup function
    return () => {
      mediaQuery.removeEventListener('change', handleSystemThemeChange);
    };
  }
  
  return () => {
    mediaQuery.removeEventListener('change', handleSystemThemeChange);
  };
};

/**
 * Check if Telegram WebApp is available
 */
export const isTelegramWebApp = (): boolean => {
  return typeof window !== 'undefined' && !!(window as any).Telegram?.WebApp;
};

/**
 * Get Telegram theme if available
 */
export const getTelegramTheme = (): Theme | null => {
  if (isTelegramWebApp()) {
    const colorScheme = (window as any).Telegram.WebApp.colorScheme;
    return colorScheme === 'dark' ? 'dark' : 'light';
  }
  return null;
};
