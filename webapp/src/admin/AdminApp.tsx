/**
 * Отдельное приложение для Admin панели с реальными данными
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AdminDashboard } from './pages/AdminDashboard';
import { AdminMetricsEnhanced } from './pages/AdminMetricsEnhanced';
import { AdminLogs } from './pages/AdminLogs';
import { AdminConfig } from './pages/AdminConfig';

// Создаем QueryClient для TanStack Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30000, // 30 секунд
    },
  },
});

type AdminPage = 'dashboard' | 'metrics' | 'logs' | 'config';

interface AdminAppProps {
  activePage: AdminPage;
}

function AdminAppContent({ activePage }: AdminAppProps) {
  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <AdminDashboard />;
      case 'metrics':
        return <AdminMetricsEnhanced />;
      case 'logs':
        return <AdminLogs />;
      case 'config':
        return <AdminConfig />;
      default:
        return <AdminDashboard />;
    }
  };

  return renderPage();
}

export function AdminApp({ activePage }: AdminAppProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <AdminAppContent activePage={activePage} />
    </QueryClientProvider>
  );
}