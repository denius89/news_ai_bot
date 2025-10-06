/* ============================================================================
   PulseAI Progress System JavaScript
   Обработка прогресс-баров и метрик
   ============================================================================ */

class ProgressManager {
  constructor() {
    this.observers = new Map();
    this.init();
  }

  init() {
    // Обработка существующих элементов с data-width
    this.processDataWidthElements();
    
    // Наблюдение за изменениями DOM
    this.observeDOM();
    
    // Автоматическое обновление каждые 5 секунд
    setInterval(() => {
      this.updateProgressBars();
    }, 5000);
  }

  processDataWidthElements() {
    const elements = document.querySelectorAll('[data-width]');
    elements.forEach(element => {
      this.setProgressWidth(element);
    });
  }

  setProgressWidth(element) {
    const width = element.getAttribute('data-width');
    if (width) {
      element.style.width = `${width}%`;
    }
  }

  updateProgressWidth(element, width) {
    element.setAttribute('data-width', width);
    this.setProgressWidth(element);
  }

  observeDOM() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            // Обработка новых элементов с data-width
            const dataWidthElements = node.querySelectorAll ? 
              node.querySelectorAll('[data-width]') : [];
            
            if (node.hasAttribute && node.hasAttribute('data-width')) {
              dataWidthElements.push(node);
            }
            
            dataWidthElements.forEach(element => {
              this.setProgressWidth(element);
            });
          }
        });
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true
    });
  }

  // Обновление прогресс-баров с анимацией
  updateProgressBars() {
    const progressBars = document.querySelectorAll('[data-width]');
    progressBars.forEach(bar => {
      const currentWidth = bar.style.width;
      const targetWidth = bar.getAttribute('data-width');
      
      if (currentWidth !== `${targetWidth}%`) {
        this.animateProgressBar(bar, targetWidth);
      }
    });
  }

  animateProgressBar(element, targetWidth) {
    element.style.transition = 'width 0.5s ease-out';
    element.style.width = `${targetWidth}%`;
    
    // Удаляем transition после анимации
    setTimeout(() => {
      element.style.transition = '';
    }, 500);
  }

  // Создание нового прогресс-бара
  createProgressBar(options = {}) {
    const {
      width = 0,
      color = 'primary',
      animated = false,
      size = 'md',
      className = ''
    } = options;

    const progressBar = document.createElement('div');
    progressBar.className = `progress-bar ${size === 'sm' ? 'progress-bar-sm' : ''} ${size === 'lg' ? 'progress-bar-lg' : ''} ${className}`;
    
    const progressFill = document.createElement('div');
    progressFill.className = `progress-fill progress-fill-${color}`;
    progressFill.setAttribute('data-width', width);
    
    if (animated) {
      progressBar.classList.add('progress-animated');
    }
    
    progressBar.appendChild(progressFill);
    
    // Устанавливаем ширину
    this.setProgressWidth(progressFill);
    
    return progressBar;
  }

  // Создание метрики
  createMetricCard(options = {}) {
    const {
      value = '--',
      label = 'Metric',
      change = null,
      className = ''
    } = options;

    const card = document.createElement('div');
    card.className = `metric-card ${className}`;
    
    const valueElement = document.createElement('div');
    valueElement.className = 'metric-value';
    valueElement.textContent = value;
    
    const labelElement = document.createElement('div');
    labelElement.className = 'metric-label';
    labelElement.textContent = label;
    
    card.appendChild(valueElement);
    card.appendChild(labelElement);
    
    if (change !== null) {
      const changeElement = document.createElement('div');
      changeElement.className = `metric-change ${change > 0 ? 'positive' : change < 0 ? 'negative' : 'neutral'}`;
      changeElement.textContent = `${change > 0 ? '+' : ''}${change}%`;
      card.appendChild(changeElement);
    }
    
    return card;
  }

  // Создание статусного индикатора
  createStatusIndicator(options = {}) {
    const {
      status = 'connected',
      text = 'Status',
      className = ''
    } = options;

    const indicator = document.createElement('span');
    indicator.className = `status-indicator status-${status} ${className}`;
    indicator.textContent = text;
    
    return indicator;
  }
}

// Инициализация при загрузке DOM
document.addEventListener('DOMContentLoaded', () => {
  window.progressManager = new ProgressManager();
});

// Экспорт для использования в других модулях
window.PulseAI = window.PulseAI || {};
window.PulseAI.ProgressManager = ProgressManager;

// Утилитарные функции
window.PulseAI.Progress = {
  setWidth: (selector, width) => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
      if (window.progressManager) {
        window.progressManager.updateProgressWidth(element, width);
      }
    });
  },

  animateTo: (selector, width, duration = 500) => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
      element.style.transition = `width ${duration}ms ease-out`;
      element.style.width = `${width}%`;
      
      setTimeout(() => {
        element.style.transition = '';
      }, duration);
    });
  },

  createBar: (options) => {
    if (window.progressManager) {
      return window.progressManager.createProgressBar(options);
    }
  },

  createMetric: (options) => {
    if (window.progressManager) {
      return window.progressManager.createMetricCard(options);
    }
  },

  createStatus: (options) => {
    if (window.progressManager) {
      return window.progressManager.createStatusIndicator(options);
    }
  }
};
