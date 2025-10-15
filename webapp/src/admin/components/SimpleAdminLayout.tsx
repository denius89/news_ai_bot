/**
 * Простой layout для Admin панели с навигацией
 */

import { useState } from 'react';
import { LayoutDashboard, BarChart3, FileText, Settings, LogOut } from 'lucide-react';
import { AdminApp } from '../AdminApp';

type AdminPage = 'dashboard' | 'metrics' | 'logs' | 'config';

export function SimpleAdminLayout() {
  const [activePage, setActivePage] = useState<AdminPage>('dashboard');

  const handleLogout = () => {
    window.location.href = '/';
  };

  const navItems = [
    { id: 'dashboard' as AdminPage, icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'metrics' as AdminPage, icon: BarChart3, label: 'Metrics' },
    { id: 'logs' as AdminPage, icon: FileText, label: 'Logs' },
    { id: 'config' as AdminPage, icon: Settings, label: 'Config' },
  ];

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r bg-card flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-green-500 to-emerald-600 bg-clip-text text-transparent">
            PulseAI Admin
          </h1>
          <p className="text-sm text-muted-foreground mt-1">Control Panel</p>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors w-full text-left ${
                activePage === item.id
                  ? 'bg-primary text-primary-foreground'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
              }`}
            >
              <item.icon className="h-5 w-5" />
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

        {/* Logout Button */}
        <div className="p-3 border-t">
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2 rounded-lg transition-colors hover:bg-muted text-muted-foreground hover:text-foreground w-full"
          >
            <LogOut className="h-5 w-5" />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto p-8">
          <AdminApp activePage={activePage} />
        </div>
      </main>
    </div>
  );
}
