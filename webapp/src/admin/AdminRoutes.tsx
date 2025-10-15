/**
 * React Router routes для Admin панели
 */

import { Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AdminLayout } from './components/AdminLayout';
import { AdminDashboard } from './pages/AdminDashboard';
import { AdminMetrics } from './pages/AdminMetrics';
import { AdminLogs } from './pages/AdminLogs';
import { AdminConfig } from './pages/AdminConfig';

// Создаем QueryClient для TanStack Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export function AdminRoutes() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        <Route path="/admin" element={<AdminLayout />}>
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<AdminDashboard />} />
          <Route path="metrics" element={<AdminMetrics />} />
          <Route path="logs" element={<AdminLogs />} />
          <Route path="config" element={<AdminConfig />} />
        </Route>
      </Routes>
    </QueryClientProvider>
  );
}

