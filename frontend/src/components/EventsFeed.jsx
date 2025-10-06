import React from 'react'
import { motion } from 'framer-motion'

export default function EventsFeed({ events }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      className="card"
    >
      <h3 className="text-xl font-semibold mb-4 flex items-center">
        <span className="mr-2">📡</span>
        Лента событий
      </h3>
      
      <div className="max-h-96 overflow-y-auto space-y-3">
        {events.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <p>События загружаются...</p>
          </div>
        ) : (
          events.map((event, index) => (
            <motion.div
              key={`${event.id}-${index}`}
              initial={{ opacity: 0, x: 100 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`p-4 rounded-lg border-l-4 ${
                event.event === 'ai_metrics_updated' ? 'border-green-500 bg-green-50 dark:bg-green-900/20' :
                event.event === 'news_processed' ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20' :
                event.event === 'digest_created' ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20' :
                'border-gray-500 bg-gray-50 dark:bg-gray-900/20'
              }`}
            >
              <div className="font-medium text-gray-900 dark:text-white">
                {event.event.replace(/_/g, ' ').toUpperCase()}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {new Date(event.timestamp).toLocaleTimeString()}
              </div>
              {event.data && (
                <div className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                  {JSON.stringify(event.data, null, 2)}
                </div>
              )}
            </motion.div>
          ))
        )}
      </div>
    </motion.div>
  )
}
