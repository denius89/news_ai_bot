import React, { useEffect } from 'react';

interface TelegramWebAppProps {
  children: React.ReactNode;
}

export const TelegramWebApp: React.FC<TelegramWebAppProps> = ({ children }) => {
  useEffect(() => {
    console.log('🚀 TelegramWebApp component mounted');
    console.log(`📍 Current URL: ${window.location.href}`);
    console.log(`🌐 User Agent: ${navigator.userAgent}`);
    console.log(`🔍 window.Telegram exists: ${!!window.Telegram}`);
    console.log(`🔍 window.Telegram.WebApp exists: ${!!window.Telegram?.WebApp}`);

    // Check if running in Telegram WebApp
    const checkTelegramWebApp = () => {
      if (window.Telegram?.WebApp) {
        console.log('✅ Telegram WebApp detected!');
        
        // Log user information
        const user = window.Telegram.WebApp.user || window.Telegram.WebApp.initDataUnsafe?.user;
        if (user) {
          console.log('👤 Telegram User:', {
            id: user.id,
            first_name: user.first_name,
            username: user.username,
            language_code: user.language_code
          });
        }
        
        try {
          // Initialize WebApp
          window.Telegram.WebApp.ready();
          console.log('✅ Telegram WebApp.ready() called');
          
          window.Telegram.WebApp.expand();
          console.log('✅ Telegram WebApp.expand() called');
          
          // Hide MainButton initially
          window.Telegram.WebApp.MainButton.hide();
          console.log('✅ MainButton hidden');
          
          // Test API connectivity
          testAPIConnectivity();
          
        } catch (error) {
          console.error(`❌ Error initializing Telegram WebApp:`, error);
        }
        
      } else {
        console.log('🌐 Not running in Telegram WebApp - using fallback mode');
        console.log('📝 Fallback mode: Using demo user for development');
        
        // Test API connectivity anyway
        testAPIConnectivity();
      }
    };

    const testAPIConnectivity = async () => {
      try {
        console.log('🔗 Testing API connectivity...');
        
        // Test multiple endpoints
        const endpoints = ['/api/health', '/api/categories'];
        
        for (const endpoint of endpoints) {
          try {
            const response = await fetch(endpoint);
            console.log(`${response.ok ? '✅' : '❌'} ${endpoint}: ${response.status}`);
          } catch (error) {
            console.error(`❌ ${endpoint}:`, error);
          }
        }
        
      } catch (error) {
        console.error(`❌ API connectivity test failed:`, error);
      }
    };

    // Check immediately and after a delay
    checkTelegramWebApp();
    setTimeout(checkTelegramWebApp, 1000);
  }, []);

  // Always render children
  return <>{children}</>;
};
