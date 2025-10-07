import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Initialize Telegram WebApp
declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        ready: () => void;
        expand: () => void;
        close: () => void;
        MainButton: {
          text: string;
          color: string;
          textColor: string;
          isVisible: boolean;
          isActive: boolean;
          show: () => void;
          hide: () => void;
          enable: () => void;
          disable: () => void;
          onClick: (callback: () => void) => void;
        };
        themeParams: {
          bg_color?: string;
          text_color?: string;
          hint_color?: string;
          link_color?: string;
          button_color?: string;
          button_text_color?: string;
        };
      };
    };
  }
}

// Initialize Telegram WebApp if available
console.log('🚀 main.tsx loaded');
console.log('🔍 window.Telegram exists:', !!window.Telegram);
console.log('🔍 window.Telegram.WebApp exists:', !!window.Telegram?.WebApp);

if (window.Telegram?.WebApp) {
  console.log('✅ Initializing Telegram WebApp');
  window.Telegram.WebApp.ready();
  window.Telegram.WebApp.expand();
  console.log('✅ Telegram WebApp initialized');
} else {
  console.log('❌ Telegram WebApp not available');
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
