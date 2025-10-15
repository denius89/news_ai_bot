/**
 * Простая страница Metrics без API
 */

import { TrendingUp, Users, FileText, Brain, Activity, Zap } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { motion } from 'framer-motion';

export function SimpleAdminMetrics() {
  // Mock данные для графиков
  const mockData = {
    newsByDay: [
      { day: 'Mon', count: 45 },
      { day: 'Tue', count: 52 },
      { day: 'Wed', count: 38 },
      { day: 'Thu', count: 61 },
      { day: 'Fri', count: 48 },
      { day: 'Sat', count: 32 },
      { day: 'Sun', count: 28 }
    ],
    usersByDay: [
      { day: 'Mon', count: 12 },
      { day: 'Tue', count: 18 },
      { day: 'Wed', count: 15 },
      { day: 'Thu', count: 22 },
      { day: 'Fri', count: 19 },
      { day: 'Sat', count: 8 },
      { day: 'Sun', count: 6 }
    ],
    aiMetrics: {
      importance: 0.72,
      credibility: 0.68,
      processingTime: 1.2
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Metrics</h1>
        <p className="text-muted-foreground mt-1">
          AI performance and system analytics
        </p>
      </div>

      {/* AI Metrics Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-gradient-to-br from-orange-500/5 to-red-500/5 border-orange-500/20 hover:shadow-lg transition-all">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Importance Score</CardTitle>
              <div className="p-2 rounded-lg bg-gradient-to-br from-orange-500/10 to-red-500/10">
                <TrendingUp className="h-4 w-4 text-orange-500" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-500">{mockData.aiMetrics.importance}</div>
              <div className="h-2 bg-muted rounded-full overflow-hidden mt-3">
                <motion.div
                  className="h-full bg-gradient-to-r from-orange-500 to-red-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${mockData.aiMetrics.importance * 100}%` }}
                  transition={{ delay: 0.3, duration: 0.8 }}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="bg-gradient-to-br from-blue-500/5 to-cyan-500/5 border-blue-500/20 hover:shadow-lg transition-all">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Credibility Score</CardTitle>
              <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500/10 to-cyan-500/10">
                <Brain className="h-4 w-4 text-blue-500" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-500">{mockData.aiMetrics.credibility}</div>
              <div className="h-2 bg-muted rounded-full overflow-hidden mt-3">
                <motion.div
                  className="h-full bg-gradient-to-r from-blue-500 to-cyan-500"
                  initial={{ width: 0 }}
                  animate={{ width: `${mockData.aiMetrics.credibility * 100}%` }}
                  transition={{ delay: 0.4, duration: 0.8 }}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="bg-gradient-to-br from-green-500/5 to-emerald-500/5 border-green-500/20 hover:shadow-lg transition-all">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Processing Time</CardTitle>
              <div className="p-2 rounded-lg bg-gradient-to-br from-green-500/10 to-emerald-500/10">
                <Zap className="h-4 w-4 text-green-500" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-500">{mockData.aiMetrics.processingTime}s</div>
              <p className="text-xs text-muted-foreground mt-1">Average per digest</p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* News by Day */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="bg-gradient-to-br from-green-500/5 to-emerald-500/5 border-green-500/10">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-green-500" />
                News Processing (7 days)
              </CardTitle>
            </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {mockData.newsByDay.map((item) => (
                <div key={item.day} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{item.day}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-green-500 to-emerald-600 transition-all"
                        style={{ width: `${(item.count / 61) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-muted-foreground w-8 text-right">{item.count}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        </motion.div>

        {/* Users by Day */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="bg-gradient-to-br from-blue-500/5 to-cyan-500/5 border-blue-500/10">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5 text-blue-500" />
                User Activity (7 days)
              </CardTitle>
            </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {mockData.usersByDay.map((item) => (
                <div key={item.day} className="flex items-center justify-between">
                  <span className="text-sm font-medium">{item.day}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-blue-500 to-cyan-600 transition-all"
                        style={{ width: `${(item.count / 22) * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-muted-foreground w-8 text-right">{item.count}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        </motion.div>
      </div>

      {/* Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Card className="bg-gradient-to-br from-purple-500/5 to-pink-500/5 border-purple-500/10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-purple-500" />
              Performance Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-6 md:grid-cols-3">
              <div className="text-center">
                <motion.div 
                  className="text-3xl font-bold text-green-500"
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.7, type: 'spring', stiffness: 200 }}
                >
                  98.5%
                </motion.div>
                <div className="text-sm text-muted-foreground mt-1">Uptime</div>
              </div>
              <div className="text-center">
                <motion.div 
                  className="text-3xl font-bold text-blue-500"
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.8, type: 'spring', stiffness: 200 }}
                >
                  1.2s
                </motion.div>
                <div className="text-sm text-muted-foreground mt-1">Avg Response</div>
              </div>
              <div className="text-center">
                <motion.div 
                  className="text-3xl font-bold text-purple-500"
                  initial={{ scale: 0.5 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.9, type: 'spring', stiffness: 200 }}
                >
                  0.72
                </motion.div>
                <div className="text-sm text-muted-foreground mt-1">Quality Score</div>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

