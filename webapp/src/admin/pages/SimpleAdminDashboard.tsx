/**
 * Простая версия Dashboard без API
 */

import { Users, FileText, Brain, TrendingUp, Activity, Database } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { motion } from 'framer-motion';

export function SimpleAdminDashboard() {
  // Mock данные для демонстрации
  const mockStats = {
    total_users: 42,
    news_today: 156,
    digests_today: 23,
    avg_importance: 0.72,
    avg_credibility: 0.68
  };

  const statCards = [
    {
      icon: Users,
      label: 'Total Users',
      value: mockStats.total_users,
      color: 'text-blue-500'
    },
    {
      icon: FileText,
      label: 'News Today',
      value: mockStats.news_today,
      color: 'text-green-500'
    },
    {
      icon: Brain,
      label: 'Digests Today',
      value: mockStats.digests_today,
      color: 'text-purple-500'
    },
    {
      icon: TrendingUp,
      label: 'Avg Importance',
      value: mockStats.avg_importance.toFixed(2),
      color: 'text-orange-500'
    },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          System overview and statistics
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1, duration: 0.3 }}
          >
            <Card className="hover:shadow-lg transition-all hover:scale-105">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
                <div className={`p-2 rounded-lg bg-gradient-to-br ${
                  stat.color === 'text-blue-500' ? 'from-blue-500/10 to-blue-600/10' :
                  stat.color === 'text-green-500' ? 'from-green-500/10 to-emerald-600/10' :
                  stat.color === 'text-purple-500' ? 'from-purple-500/10 to-violet-600/10' :
                  'from-orange-500/10 to-red-600/10'
                }`}>
                  <stat.icon className={`h-4 w-4 ${stat.color}`} />
                </div>
              </CardHeader>
              <CardContent>
                <motion.div 
                  className="text-2xl font-bold"
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: i * 0.1 + 0.2, type: 'spring', stiffness: 200 }}
                >
                  {stat.value}
                </motion.div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* AI Quality Metrics */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>AI Quality (7 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Average Importance</span>
                  <span className="text-sm font-medium">{mockStats.avg_importance.toFixed(2)}</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-600 transition-all"
                    style={{ width: `${mockStats.avg_importance * 100}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Average Credibility</span>
                  <span className="text-sm font-medium">{mockStats.avg_credibility.toFixed(2)}</span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-cyan-600 transition-all"
                    style={{ width: `${mockStats.avg_credibility * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-green-500/5 to-emerald-600/5 border-green-500/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-500" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium flex items-center gap-2">
                  <Database className="h-4 w-4 text-muted-foreground" />
                  API Status
                </span>
                <span className="flex items-center gap-2 text-sm font-medium">
                  <motion.span 
                    className="h-2 w-2 rounded-full bg-green-500"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 2 }}
                  />
                  Online
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium flex items-center gap-2">
                  <Database className="h-4 w-4 text-muted-foreground" />
                  Database
                </span>
                <span className="flex items-center gap-2 text-sm font-medium">
                  <motion.span 
                    className="h-2 w-2 rounded-full bg-green-500"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ repeat: Infinity, duration: 2, delay: 0.5 }}
                  />
                  Connected
                </span>
              </div>
              <div className="flex items-center justify-between pt-2 border-t">
                <span className="text-sm text-muted-foreground">Last Update</span>
                <span className="text-sm font-mono">
                  {new Date().toLocaleTimeString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
