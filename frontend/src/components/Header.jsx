import React from 'react'
import { motion } from 'framer-motion'

export default function Header({ currentPage, setCurrentPage }) {
  const navItems = [
    { id: 'dashboard', label: 'Главная', icon: '🏠' },
    { id: 'live', label: 'Live Dashboard', icon: '⚡' }
  ]

  return (
    <motion.header
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50"
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-pulseai-primary to-pulseai-secondary bg-clip-text text-transparent">
              PulseAI
            </h1>
          </div>
          
          <nav className="flex space-x-1">
            {navItems.map((item) => (
              <motion.button
                key={item.id}
                onClick={() => setCurrentPage(item.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
                  currentPage === item.id
                    ? 'bg-pulseai-primary text-white shadow-lg'
                    : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <span className="mr-2">{item.icon}</span>
                {item.label}
              </motion.button>
            ))}
          </nav>
        </div>
      </div>
    </motion.header>
  )
}
