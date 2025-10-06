import React from 'react'
import { motion } from 'framer-motion'

export default function MetricsCard({ title, icon, metrics }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="card"
    >
      <h3 className="text-xl font-semibold mb-4 flex items-center">
        <span className="mr-2">{icon}</span>
        {title}
      </h3>
      
      <div className="grid grid-cols-2 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-green-500">
            {metrics.credibility ? `${Math.round(metrics.credibility * 100)}%` : '--%'}
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">Достоверность</p>
        </div>
        
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-500">
            {metrics.importance ? `${Math.round(metrics.importance * 100)}%` : '--%'}
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400">Важность</p>
        </div>
      </div>
      
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500 dark:text-gray-500">
          {metrics.timestamp ? new Date(metrics.timestamp).toLocaleTimeString() : 'Не обновлено'}
        </p>
      </div>
    </motion.div>
  )
}
