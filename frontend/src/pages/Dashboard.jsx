import React from 'react'
import { motion } from 'framer-motion'
import { useReactor } from '../components/ReactorProvider'
import MetricsCard from '../components/MetricsCard'
import EventsFeed from '../components/EventsFeed'
import StatusIndicator from '../components/StatusIndicator'

export default function Dashboard() {
  const { connected, metrics, events } = useReactor()

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          Добро пожаловать в PulseAI
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300">
          AI-платформа для персонализированных дайджестов новостей
        </p>
      </motion.div>

      <StatusIndicator connected={connected} />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <MetricsCard
          title="AI Метрики"
          icon="🧠"
          metrics={metrics}
        />
        
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <span className="mr-2">📰</span>
            Обработка новостей
          </h3>
          <div className="text-3xl font-bold text-pulseai-primary">
            {metrics.news_processed || 0}
          </div>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Новостей обработано
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <span className="mr-2">⚡</span>
            События Reactor
          </h3>
          <div className="text-3xl font-bold text-green-500">
            {events.length}
          </div>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Событий получено
          </p>
        </motion.div>
      </div>

      <EventsFeed events={events} />
    </div>
  )
}
