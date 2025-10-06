import React from 'react'
import { motion } from 'framer-motion'
import { useReactor } from '../components/ReactorProvider'
import MetricsCard from '../components/MetricsCard'
import EventsFeed from '../components/EventsFeed'
import StatusIndicator from '../components/StatusIndicator'

export default function LiveDashboard() {
  const { connected, metrics, events, emitEvent } = useReactor()

  return (
    <div className="space-y-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center"
      >
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          ⚡ PulseAI Live Dashboard
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-300">
          Реактивная система в реальном времени
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
            <span className="mr-2">💚</span>
            Состояние системы
          </h3>
          <div className={`text-3xl font-bold ${connected ? 'text-green-500' : 'text-red-500'}`}>
            {connected ? 'OK' : 'OFFLINE'}
          </div>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Статус подключения
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <span className="mr-2">📡</span>
            События
          </h3>
          <div className="text-3xl font-bold text-blue-500">
            {events.length}
          </div>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Событий получено
          </p>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EventsFeed events={events} />
        
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="card"
        >
          <h3 className="text-xl font-semibold mb-4 flex items-center">
            <span className="mr-2">🎯</span>
            Управление
          </h3>
          <div className="space-y-4">
            <button
              onClick={() => emitEvent('test_event', { message: 'Тестовое событие' })}
              className="btn-primary w-full"
            >
              🎯 Тест событие
            </button>
            <button
              onClick={() => emitEvent('ping', {})}
              className="btn-secondary w-full"
            >
              📡 Ping Reactor
            </button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
