import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import ReactorProvider from './components/ReactorProvider'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import LiveDashboard from './pages/LiveDashboard'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')

  const pages = {
    dashboard: <Dashboard />,
    live: <LiveDashboard />
  }

  return (
    <ReactorProvider>
      <div className="min-h-screen bg-gradient-to-br from-pulseai-background to-gray-50 dark:from-pulseai-background-dark dark:to-gray-900">
        <Header currentPage={currentPage} setCurrentPage={setCurrentPage} />
        
        <motion.main
          key={currentPage}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="container mx-auto px-4 py-8"
        >
          {pages[currentPage]}
        </motion.main>
      </div>
    </ReactorProvider>
  )
}

export default App
