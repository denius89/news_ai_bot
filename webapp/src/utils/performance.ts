/**
 * Performance utilities для оптимизации на слабых устройствах
 */

/**
 * Определяет, является ли устройство слабым (требует оптимизации)
 */
export function isLowPerformanceDevice(): boolean {
  // Проверяем memory (если доступно)
  const memory = (performance as any).memory;
  if (memory && memory.jsHeapSizeLimit) {
    // Если меньше 1GB JS heap - считаем слабым устройством
    if (memory.jsHeapSizeLimit < 1000000000) {
      return true;
    }
  }

  // Проверяем количество ядер
  if (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 2) {
    return true;
  }

  // Проверяем connection (если доступно)
  const connection = (navigator as any).connection;
  if (connection) {
    // Если медленное соединение или save-data режим
    if (connection.saveData || connection.effectiveType === 'slow-2g' || connection.effectiveType === '2g') {
      return true;
    }
  }

  // Проверяем user agent для старых устройств
  const ua = navigator.userAgent.toLowerCase();
  const oldDevicePatterns = [
    /android [1-6]\./,  // Android 6 и ниже
    /cpu os [1-9]_/,     // iOS 9 и ниже
    /cpu os 1[0-1]_/,    // iOS 10-11
  ];
  
  if (oldDevicePatterns.some(pattern => pattern.test(ua))) {
    return true;
  }

  return false;
}

/**
 * Определяет, нужно ли отключить анимации
 */
export function shouldReduceMotion(): boolean {
  // Проверяем системные настройки
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return true;
  }

  // Отключаем анимации на слабых устройствах
  return isLowPerformanceDevice();
}

/**
 * Возвращает упрощенные варианты анимаций для слабых устройств
 */
export function getOptimizedAnimationVariants(defaultVariants: any) {
  if (shouldReduceMotion()) {
    // Возвращаем вариант без анимаций (instant)
    return {
      hidden: { opacity: 1 },
      visible: { opacity: 1 },
      initial: { opacity: 1 },
      in: { opacity: 1 },
      out: { opacity: 1 },
    };
  }
  
  return defaultVariants;
}

/**
 * Throttle функция для оптимизации частых вызовов
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;
  let lastRan: number = 0;

  return function (this: any, ...args: Parameters<T>) {
    const now = Date.now();

    if (lastRan && now - lastRan < wait) {
      if (timeout) clearTimeout(timeout);
      timeout = setTimeout(() => {
        lastRan = now;
        func.apply(this, args);
      }, wait - (now - lastRan));
    } else {
      lastRan = now;
      func.apply(this, args);
    }
  };
}

/**
 * Debounce функция для отложенного выполнения
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function (this: any, ...args: Parameters<T>) {
    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(() => func.apply(this, args), wait);
  };
}

/**
 * Возвращает оптимальный throttle delay на основе производительности устройства
 */
export function getOptimalThrottleDelay(defaultDelay: number = 200): number {
  if (isLowPerformanceDevice()) {
    // На слабых устройствах увеличиваем delay вдвое
    return defaultDelay * 2;
  }
  return defaultDelay;
}

/**
 * Кэш для предотвращения повторных вычислений
 */
let _performanceLevel: 'low' | 'medium' | 'high' | null = null;

export function getPerformanceLevel(): 'low' | 'medium' | 'high' {
  if (_performanceLevel) return _performanceLevel;

  if (isLowPerformanceDevice()) {
    _performanceLevel = 'low';
  } else if (navigator.hardwareConcurrency && navigator.hardwareConcurrency >= 8) {
    _performanceLevel = 'high';
  } else {
    _performanceLevel = 'medium';
  }

  console.log(`[Performance] Detected performance level: ${_performanceLevel}`);
  return _performanceLevel;
}

/**
 * Логирует информацию о производительности устройства
 */
export function logDevicePerformanceInfo() {
  const info: any = {
    performanceLevel: getPerformanceLevel(),
    shouldReduceMotion: shouldReduceMotion(),
    hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
    deviceMemory: (navigator as any).deviceMemory || 'unknown',
    connection: (navigator as any).connection?.effectiveType || 'unknown',
    saveData: (navigator as any).connection?.saveData || false,
  };

  const memory = (performance as any).memory;
  if (memory) {
    info.jsHeapSizeLimit = `${(memory.jsHeapSizeLimit / 1024 / 1024).toFixed(0)}MB`;
    info.jsHeapSize = `${(memory.usedJSHeapSize / 1024 / 1024).toFixed(0)}MB`;
  }

  console.log('[Performance] Device info:', info);
  return info;
}

