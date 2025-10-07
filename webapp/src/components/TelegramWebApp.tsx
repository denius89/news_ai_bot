import React, { useEffect, useState } from 'react';

interface TelegramWebAppProps {
  children: React.ReactNode;
}

export const TelegramWebApp: React.FC<TelegramWebAppProps> = ({ children }) => {
  const [isTelegramWebApp, setIsTelegramWebApp] = useState(false);
  const [debugInfo, setDebugInfo] = useState<any>(null);
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    const logMessage = `[${timestamp}] ${message}`;
    console.log(logMessage);
    setLogs(prev => [...prev.slice(-15), logMessage]); // Keep last 15 logs
  };

  useEffect(() => {
    addLog('🚀 TelegramWebApp component mounted');
    addLog(`📍 Current URL: ${window.location.href}`);
    addLog(`🌐 User Agent: ${navigator.userAgent}`);
    addLog(`🔍 window.Telegram exists: ${!!window.Telegram}`);
    addLog(`🔍 window.Telegram.WebApp exists: ${!!window.Telegram?.WebApp}`);

    // Check if running in Telegram WebApp
    const checkTelegramWebApp = () => {
      if (window.Telegram?.WebApp) {
        addLog('✅ Telegram WebApp detected!');
        setIsTelegramWebApp(true);
        
        try {
          // Collect debug info
          const info = {
            version: window.Telegram.WebApp.version,
            platform: window.Telegram.WebApp.platform,
            colorScheme: window.Telegram.WebApp.colorScheme,
            themeParams: window.Telegram.WebApp.themeParams,
            isExpanded: window.Telegram.WebApp.isExpanded,
            viewportHeight: window.Telegram.WebApp.viewportHeight,
            viewportStableHeight: window.Telegram.WebApp.viewportStableHeight,
            headerColor: window.Telegram.WebApp.headerColor,
            backgroundColor: window.Telegram.WebApp.backgroundColor,
          };
          
          setDebugInfo(info);
          addLog(`📊 WebApp Info: ${JSON.stringify(info, null, 2)}`);
          
          // Initialize WebApp
          window.Telegram.WebApp.ready();
          addLog('✅ Telegram WebApp.ready() called');
          
          window.Telegram.WebApp.expand();
          addLog('✅ Telegram WebApp.expand() called');
          
          // Hide MainButton initially
          window.Telegram.WebApp.MainButton.hide();
          addLog('✅ MainButton hidden');
          
          // Test API connectivity
          testAPIConnectivity();
          
        } catch (error) {
          addLog(`❌ Error initializing Telegram WebApp: ${error}`);
        }
        
      } else {
        addLog('❌ Not running in Telegram WebApp - regular browser');
        setIsTelegramWebApp(false);
        setDebugInfo({
          error: 'Not in Telegram WebApp',
          url: window.location.href,
          userAgent: navigator.userAgent
        });
        
        // Test API connectivity anyway
        testAPIConnectivity();
      }
    };

    const testAPIConnectivity = async () => {
      try {
        addLog('🔗 Testing API connectivity...');
        
        // Test multiple endpoints
        const endpoints = ['/api/health', '/api/categories', '/api/user_notifications'];
        
        for (const endpoint of endpoints) {
          try {
            const response = await fetch(endpoint);
            addLog(`${response.ok ? '✅' : '❌'} ${endpoint}: ${response.status}`);
          } catch (error) {
            addLog(`❌ ${endpoint}: ${error}`);
          }
        }
        
      } catch (error) {
        addLog(`❌ API connectivity test failed: ${error}`);
      }
    };

    // Check immediately and after a delay
    checkTelegramWebApp();
    setTimeout(checkTelegramWebApp, 1000);
  }, []);

  // If not in Telegram WebApp, render children normally
  if (!isTelegramWebApp) {
    return <>{children}</>;
  }

  // In Telegram WebApp, render children without debug overlay
  return <>{children}</>;
};
