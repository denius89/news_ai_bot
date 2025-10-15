/**
 * Расширенная страница метрик с табами (Phase 1 + Phase 2)
 * News | Events | Users | AI | Digests | System
 */

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import { Newspaper, Calendar, Users, Bot, FileText, Activity, Star, CheckCircle, Hash, DollarSign, Tag, Globe, TrendingUp, Bell, Ruler, Monitor, Cpu, HardDrive, Database } from 'lucide-react';
import { 
  useNewsMetrics, 
  useEventsMetrics, 
  useUserEngagement,
  useDigestMetrics,
  useAIPerformanceDetailed,
  useSystemHealth 
} from '../hooks/useEnhancedMetrics';
import { useAIMetrics } from '../hooks/useMetrics';
import { MetricCard } from '../components/metrics/MetricCard';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export function AdminMetricsEnhanced() {
  const [days, setDays] = useState(7);
  
  // Phase 1 hooks
  const { data: newsMetrics, isLoading: newsLoading } = useNewsMetrics(days);
  const { data: eventsMetrics, isLoading: eventsLoading } = useEventsMetrics(days, 7);
  const { data: userEngagement, isLoading: userLoading } = useUserEngagement();
  const { data: aiMetrics, isLoading: aiLoading } = useAIMetrics(days);
  
  // Phase 2 hooks
  const { data: digestMetrics, isLoading: digestLoading } = useDigestMetrics(30);
  const { data: aiPerformance, isLoading: aiPerfLoading } = useAIPerformanceDetailed(days);
  const { data: systemHealth, isLoading: systemLoading } = useSystemHealth();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Enhanced Metrics</h1>
          <p className="text-muted-foreground mt-1">
            News, Events, Users, and AI Performance Analytics
          </p>
        </div>
        
        {/* Period Selector */}
        <div className="flex gap-2">
          {[7, 14, 30].map((d) => (
            <button
              key={d}
              onClick={() => setDays(d)}
              className={`px-4 py-2 rounded-lg transition-colors text-sm ${
                days === d
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted hover:bg-muted/80'
              }`}
            >
              {d} days
            </button>
          ))}
        </div>
      </div>

      {/* Tabbed Interface */}
      <Tabs defaultValue="news" className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="news" className="flex items-center gap-1">
            <Newspaper className="w-4 h-4" />
            News
          </TabsTrigger>
          <TabsTrigger value="events" className="flex items-center gap-1">
            <Calendar className="w-4 h-4" />
            Events
          </TabsTrigger>
          <TabsTrigger value="users" className="flex items-center gap-1">
            <Users className="w-4 h-4" />
            Users
          </TabsTrigger>
          <TabsTrigger value="ai" className="flex items-center gap-1">
            <Bot className="w-4 h-4" />
            AI
          </TabsTrigger>
          <TabsTrigger value="digests" className="flex items-center gap-1">
            <FileText className="w-4 h-4" />
            Digests
          </TabsTrigger>
          <TabsTrigger value="system" className="flex items-center gap-1">
            <Activity className="w-4 h-4" />
            System
          </TabsTrigger>
        </TabsList>

        {/* News Analytics Tab */}
        <TabsContent value="news" className="space-y-4">
          {newsLoading ? (
            <div className="text-center py-12">Loading news metrics...</div>
          ) : (
            <>
              {/* Summary Cards */}
              <div className="grid gap-4 md:grid-cols-3">
                <MetricCard
                  title="Total News"
                  value={newsMetrics?.total_news || 0}
                  icon={Newspaper}
                  subtitle={`Last ${days} days`}
                />
                <MetricCard
                  title="Categories"
                  value={newsMetrics?.by_category?.length || 0}
                  icon={Tag}
                  subtitle="Active categories"
                />
                <MetricCard
                  title="Sources"
                  value={newsMetrics?.by_source?.length || 0}
                  icon={Globe}
                  subtitle="RSS feeds"
                />
              </div>

              {/* Timeline Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>News Volume Timeline</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={newsMetrics?.timeline || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="count" stroke="#3b82f6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Category & Source Distribution */}
              <div className="grid gap-4 md:grid-cols-2">
                {/* By Category */}
                <Card>
                  <CardHeader>
                    <CardTitle>By Category</CardTitle>
                  </CardHeader>
                  <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={newsMetrics?.by_category || [] as any}
                        dataKey="count"
                        nameKey="category"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label
                      >
                        {(newsMetrics?.by_category || []).map((_entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* Top Sources */}
                <Card>
                  <CardHeader>
                    <CardTitle>Top 10 Sources</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={newsMetrics?.by_source || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="source" angle={-45} textAnchor="end" height={100} />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#3b82f6" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* Events Analytics Tab */}
        <TabsContent value="events" className="space-y-4">
          {eventsLoading ? (
            <div className="text-center py-12">Loading events metrics...</div>
          ) : (
            <>
              {/* Summary Cards */}
              <div className="grid gap-4 md:grid-cols-3">
                <MetricCard
                  title="Upcoming Events"
                  value={eventsMetrics?.total_upcoming || 0}
                  icon={Calendar}
                  subtitle="Next 7 days"
                />
                <MetricCard
                  title="Total Analyzed"
                  value={eventsMetrics?.total_analyzed || 0}
                  icon={TrendingUp}
                  subtitle={`Last ${days} days`}
                />
                <MetricCard
                  title="Categories"
                  value={eventsMetrics?.by_category?.length || 0}
                  icon={Tag}
                  subtitle="Event types"
                />
              </div>

              {/* Priority & Category Distribution */}
              <div className="grid gap-4 md:grid-cols-2">
                {/* By Priority */}
                <Card>
                  <CardHeader>
                    <CardTitle>By Priority</CardTitle>
                  </CardHeader>
                  <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={eventsMetrics?.by_priority || [] as any}
                        dataKey="count"
                        nameKey="priority"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label
                      >
                        {(eventsMetrics?.by_priority || []).map((_entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  </CardContent>
                </Card>

                {/* By Category */}
                <Card>
                  <CardHeader>
                    <CardTitle>By Category</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={eventsMetrics?.by_category || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="category" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#22c55e" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>

              {/* Upcoming Events Table */}
              <Card>
                <CardHeader>
                  <CardTitle>Next Events</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {(eventsMetrics?.upcoming || []).slice(0, 10).map((event, idx) => (
                      <div key={idx} className="flex justify-between items-center p-3 bg-muted rounded-lg">
                        <div>
                          <div className="font-medium">{event.title}</div>
                          <div className="text-xs text-muted-foreground">
                            {event.category} • {event.country}
                          </div>
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {new Date(event.event_time).toLocaleDateString()}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* User Engagement Tab */}
        <TabsContent value="users" className="space-y-4">
          {userLoading ? (
            <div className="text-center py-12">Loading user metrics...</div>
          ) : (
            <>
              {/* Summary Cards */}
              <div className="grid gap-4 md:grid-cols-4">
                <MetricCard
                  title="Total Users"
                  value={userEngagement?.total_users || 0}
                  icon={Users}
                  subtitle="All time"
                />
                <MetricCard
                  title="Monthly Active"
                  value={userEngagement?.active_users?.monthly || 0}
                  icon={Calendar}
                  subtitle="Last 30 days"
                />
                <MetricCard
                  title="Weekly Active"
                  value={userEngagement?.active_users?.weekly || 0}
                  icon={TrendingUp}
                  subtitle="Last 7 days"
                />
                <MetricCard
                  title="Subscriptions"
                  value={userEngagement?.total_subscriptions || 0}
                  icon={Bell}
                  subtitle="Active"
                />
              </div>

              {/* Growth Timeline */}
              <Card>
                <CardHeader>
                  <CardTitle>User Growth (Last 30 Days)</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={userEngagement?.growth_timeline || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="count" stroke="#22c55e" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {/* Subscriptions Distribution */}
              <Card>
                <CardHeader>
                  <CardTitle>Subscription Categories</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={userEngagement?.subscriptions_dist || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="category" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="count" fill="#8b5cf6" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* AI Performance Tab */}
        <TabsContent value="ai" className="space-y-4">
          {aiLoading || aiPerfLoading ? (
            <div className="text-center py-12">Loading AI metrics...</div>
          ) : (
            <>
              {/* Summary Cards */}
              <div className="grid gap-4 md:grid-cols-4">
                <MetricCard
                  title="Avg Importance"
                  value={aiMetrics?.avg_importance?.toFixed(2) || '0.00'}
                  icon={Star}
                  subtitle={`${aiMetrics?.total_items || 0} items analyzed`}
                />
                <MetricCard
                  title="Avg Credibility"
                  value={aiMetrics?.avg_credibility?.toFixed(2) || '0.00'}
                  icon={CheckCircle}
                  subtitle={`Last ${days} days`}
                />
                <MetricCard
                  title="Est. Tokens"
                  value={`${((aiPerformance?.estimated_tokens || 0) / 1000).toFixed(0)}K`}
                  icon={Hash}
                  subtitle={`${aiPerformance?.total_ai_calls || 0} API calls`}
                />
                <MetricCard
                  title="Est. Cost"
                  value={`$${aiPerformance?.estimated_cost_usd?.toFixed(3) || '0.000'}`}
                  icon={DollarSign}
                  subtitle={`gpt-4o-mini`}
                />
              </div>

              {/* Distribution Charts */}
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Importance Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={aiMetrics?.importance_distribution || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="range" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#f59e0b" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Credibility Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <BarChart data={aiMetrics?.credibility_distribution || []}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="range" />
                        <YAxis />
                        <Tooltip />
                        <Bar dataKey="count" fill="#22c55e" />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </>
          )}
        </TabsContent>

        {/* Digests Tab (Phase 2) */}
        <TabsContent value="digests" className="space-y-4">
          {digestLoading ? (
            <div className="text-center py-12">Loading digest metrics...</div>
          ) : (
            <>
              {/* Summary Cards */}
              <div className="grid gap-4 md:grid-cols-4">
                <MetricCard
                  title="Total Digests"
                  value={digestMetrics?.total_digests || 0}
                  icon={FileText}
                  subtitle="Last 30 days"
                />
                <MetricCard
                  title="Avg Length"
                  value={`${digestMetrics?.avg_length_words || 0} words`}
                  icon={Ruler}
                  subtitle="Per digest"
                />
                <MetricCard
                  title="Feedback Score"
                  value={digestMetrics?.feedback_stats?.avg_score?.toFixed(2) || '0.00'}
                  icon={Star}
                  subtitle={`${digestMetrics?.feedback_stats?.total_feedback || 0} ratings`}
                />
                <MetricCard
                  title="Generation Rate"
                  value={`${Math.round((digestMetrics?.total_digests || 0) / 30)} /day`}
                  icon={TrendingUp}
                  subtitle="Average"
                />
              </div>

              {/* Timeline */}
              <Card>
                <CardHeader>
                  <CardTitle>Digest Generation Timeline</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={digestMetrics?.timeline || []}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="count" stroke="#8b5cf6" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        {/* System Health Tab (Phase 2) */}
        <TabsContent value="system" className="space-y-4">
          {systemLoading ? (
            <div className="text-center py-12">Loading system health...</div>
          ) : (
            <>
              {/* Process Status */}
              <div>
                <h3 className="text-lg font-semibold mb-3">Process Status</h3>
                <div className="grid gap-4 md:grid-cols-3">
                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-sm text-muted-foreground">Flask WebApp</div>
                          <div className="text-2xl font-bold mt-1">
                            {systemHealth?.processes?.flask?.status || 'unknown'}
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            Uptime: {Math.floor((systemHealth?.processes?.flask?.uptime_seconds || 0) / 60)}m
                          </div>
                        </div>
                        <div className={`w-3 h-3 rounded-full ${
                          systemHealth?.processes?.flask?.status === 'running' ? 'bg-green-500' : 'bg-red-500'
                        }`} />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-sm text-muted-foreground">Telegram Bot</div>
                          <div className="text-2xl font-bold mt-1">
                            {systemHealth?.processes?.bot?.status || 'unknown'}
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            Uptime: {Math.floor((systemHealth?.processes?.bot?.uptime_seconds || 0) / 60)}m
                          </div>
                        </div>
                        <div className={`w-3 h-3 rounded-full ${
                          systemHealth?.processes?.bot?.status === 'running' ? 'bg-green-500' : 'bg-red-500'
                        }`} />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="pt-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="text-sm text-muted-foreground">Cloudflare Tunnel</div>
                          <div className="text-2xl font-bold mt-1">
                            {systemHealth?.processes?.cloudflare?.status || 'unknown'}
                          </div>
                          <div className="text-xs text-muted-foreground mt-1">
                            Proxy active
                          </div>
                        </div>
                        <div className={`w-3 h-3 rounded-full ${
                          systemHealth?.processes?.cloudflare?.status === 'running' ? 'bg-green-500' : 'bg-yellow-500'
                        }`} />
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>

              {/* Resource Usage */}
              <div>
                <h3 className="text-lg font-semibold mb-3">Resource Usage</h3>
                <div className="grid gap-4 md:grid-cols-4">
                  <MetricCard
                    title="CPU Usage"
                    value={`${systemHealth?.resources?.cpu_percent || 0}%`}
                    icon={Monitor}
                    trend={
                      (systemHealth?.resources?.cpu_percent || 0) > 80 ? 'down' :
                      (systemHealth?.resources?.cpu_percent || 0) > 50 ? 'neutral' : 'up'
                    }
                  />
                  <MetricCard
                    title="Memory Usage"
                    value={`${systemHealth?.resources?.memory_percent || 0}%`}
                    icon={Cpu}
                    subtitle={`${systemHealth?.resources?.memory_mb || 0} MB`}
                    trend={
                      (systemHealth?.resources?.memory_percent || 0) > 80 ? 'down' :
                      (systemHealth?.resources?.memory_percent || 0) > 50 ? 'neutral' : 'up'
                    }
                  />
                  <MetricCard
                    title="Disk Usage"
                    value={`${systemHealth?.resources?.disk_percent || 0}%`}
                    icon={HardDrive}
                    trend={
                      (systemHealth?.resources?.disk_percent || 0) > 80 ? 'down' :
                      (systemHealth?.resources?.disk_percent || 0) > 50 ? 'neutral' : 'up'
                    }
                  />
                  <MetricCard
                    title="DB Latency"
                    value={`${systemHealth?.api_health?.database_latency_ms || 0}ms`}
                    icon={Database}
                    trend={
                      (systemHealth?.api_health?.database_latency_ms || 0) > 100 ? 'down' :
                      (systemHealth?.api_health?.database_latency_ms || 0) > 50 ? 'neutral' : 'up'
                    }
                  />
                </div>
              </div>
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

