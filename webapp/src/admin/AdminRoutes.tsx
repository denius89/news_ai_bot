/**
 * React Router routes для Admin панели
 */

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Navigate, Route, Routes } from 'react-router-dom';
import { AdminLayout } from './components/AdminLayout';
import { AdminConfig } from './pages/AdminConfig';
import { AdminContentControl } from './pages/AdminContentControl';
import { AdminDashboard } from './pages/AdminDashboard';
import { AdminLogs } from './pages/AdminLogs';
import { AdminMetrics } from './pages/AdminMetrics';

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
                    <Route path="content" element={<AdminContentControl />} />
                    <Route path="logs" element={<AdminLogs />} />
                    <Route path="config" element={<AdminConfig />} />
                </Route>
            </Routes>
        </QueryClientProvider>
    );
}
