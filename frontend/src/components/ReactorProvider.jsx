import React, { createContext, useContext, useState, useEffect } from 'react'
import io from 'socket.io-client'

const ReactorContext = createContext()

export const useReactor = () => {
  const context = useContext(ReactorContext)
  if (!context) {
    throw new Error('useReactor must be used within a ReactorProvider')
  }
  return context
}

export default function ReactorProvider({ children }) {
  const [socket, setSocket] = useState(null)
  const [connected, setConnected] = useState(false)
  const [events, setEvents] = useState([])
  const [metrics, setMetrics] = useState({})

  useEffect(() => {
    const newSocket = io('http://localhost:8001', {
      transports: ['websocket', 'polling']
    })
    
    newSocket.on('connect', () => {
      setConnected(true)
      console.log('Connected to Reactor')
    })
    
    newSocket.on('disconnect', () => {
      setConnected(false)
      console.log('Disconnected from Reactor')
    })
    
    newSocket.on('reactor_event', (data) => {
      setEvents(prev => [data, ...prev.slice(0, 9)]) // Keep last 10 events
      
      // Update metrics based on event type
      if (data.event === 'ai_metrics_updated') {
        setMetrics(prev => ({ ...prev, ...data.data }))
      }
    })
    
    setSocket(newSocket)
    
    return () => {
      newSocket.close()
    }
  }, [])

  const emitEvent = (eventName, data) => {
    if (socket) {
      socket.emit('test_event', { event: eventName, data })
    }
  }

  const value = {
    socket,
    connected,
    events,
    metrics,
    emitEvent
  }

  return (
    <ReactorContext.Provider value={value}>
      {children}
    </ReactorContext.Provider>
  )
}
