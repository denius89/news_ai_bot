/**
 * PULSE-WS: React component for PulseAI Reactor WebSocket integration.
 * Replaces Socket.IO with native WebSocket for better performance.
 */

import React, { createContext, useContext, useEffect, useState } from 'react'

// PULSE-WS: Create Reactor context
const ReactorContext = createContext()

// PULSE-WS: Reactor Provider component
export function ReactorProvider({ children }) {
  const [connected, setConnected] = useState(false)
  const [events, setEvents] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    // PULSE-WS: Wait for global reactor client to be available
    const checkReactor = () => {
      if (window.reactor) {
        console.log('PULSE-WS: Reactor client found, initializing...')
        initializeReactor()
      } else {
        // Retry after a short delay
        setTimeout(checkReactor, 100)
      }
    }

    const initializeReactor = () => {
      // PULSE-WS: Set up event listeners
      const handleConnect = (event) => {
        console.log('PULSE-WS: Reactor connected')
        setConnected(true)
        setError(null)
      }

      const handleDisconnect = (event) => {
        console.log('PULSE-WS: Reactor disconnected')
        setConnected(false)
      }

      const handleError = (event) => {
        console.error('PULSE-WS: Reactor error:', event.detail)
        setError(event.detail.error)
        setConnected(false)
      }

      const handleEvent = (event) => {
        console.log('PULSE-WS: Received event:', event.type, event.detail)
        
        // PULSE-WS: Add event to state
        setEvents(prev => [
          ...prev.slice(-49), // Keep last 50 events
          {
            type: event.type,
            data: event.detail,
            timestamp: Date.now()
          }
        ])
      }

      // PULSE-WS: Add event listeners
      window.addEventListener('reactor_connected', handleConnect)
      window.addEventListener('reactor_disconnected', handleDisconnect)
      window.addEventListener('reactor_error', handleError)
      
      // PULSE-WS: Add listeners for specific Reactor events
      window.addEventListener('ai_metrics_updated', handleEvent)
      window.addEventListener('news_processed', handleEvent)
      window.addEventListener('digest_created', handleEvent)
      window.addEventListener('event_detected', handleEvent)
      window.addEventListener('user_action', handleEvent)
      window.addEventListener('system_health_check', handleEvent)
      window.addEventListener('reactor_heartbeat', handleEvent)

      // PULSE-WS: Cleanup function
      return () => {
        window.removeEventListener('reactor_connected', handleConnect)
        window.removeEventListener('reactor_disconnected', handleDisconnect)
        window.removeEventListener('reactor_error', handleError)
        window.removeEventListener('ai_metrics_updated', handleEvent)
        window.removeEventListener('news_processed', handleEvent)
        window.removeEventListener('digest_created', handleEvent)
        window.removeEventListener('event_detected', handleEvent)
        window.removeEventListener('user_action', handleEvent)
        window.removeEventListener('system_health_check', handleEvent)
        window.removeEventListener('reactor_heartbeat', handleEvent)
      }
    }

    // PULSE-WS: Start checking for reactor client
    checkReactor()

    // PULSE-WS: Cleanup on unmount
    return () => {
      if (window.reactor) {
        window.reactor.disconnect()
      }
    }
  }, [])

  // PULSE-WS: Reactor context value
  const contextValue = {
    connected,
    events,
    error,
    send: (type, data) => {
      if (window.reactor) {
        window.reactor.send(type, data)
      }
    },
    subscribe: (events) => {
      if (window.reactor) {
        window.reactor.subscribe(events)
      }
    },
    getStatus: () => {
      return window.reactor ? window.reactor.getStatus() : { connected: false }
    }
  }

  return (
    <ReactorContext.Provider value={contextValue}>
      {children}
    </ReactorContext.Provider>
  )
}

// PULSE-WS: Hook to use Reactor context
export function useReactor() {
  const context = useContext(ReactorContext)
  if (!context) {
    throw new Error('useReactor must be used within a ReactorProvider')
  }
  return context
}

export default ReactorProvider