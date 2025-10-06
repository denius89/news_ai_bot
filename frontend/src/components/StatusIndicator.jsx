import React from 'react'
import { motion } from 'framer-motion'

export default function StatusIndicator({ connected }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="card text-center"
    >
      <div className="flex items-center justify-center space-x-3">
        <motion.div
          animate={connected ? { scale: [1, 1.2, 1] } : {}}
          transition={{ duration: 2, repeat: Infinity }}
          className={`w-4 h-4 rounded-full ${
            connected ? 'bg-green-500' : 'bg-red-500'
          }`}
        />
        <div>
          <div className="font-semibold text-gray-900 dark:text-white">
            Reactor Status
          </div>
          <div className={`text-sm ${
            connected ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          }`}>
            {connected ? 'Подключен' : 'Отключен'}
          </div>
        </div>
      </div>
    </motion.div>
  )
}
