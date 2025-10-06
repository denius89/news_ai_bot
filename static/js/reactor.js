/**
 * PULSE-WS: Pure WebSocket client for PulseAI Reactor Core.
 * Replaces Socket.IO with native WebSocket for better performance and simplicity.
 */

(function() {
    'use strict';
    
    // PULSE-WS: WebSocket connection state
    let socket = null;
    let heartbeatInterval = null;
    let reconnectTimeout = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 10;
    const reconnectDelay = 3000;
    
    // PULSE-WS: Connection configuration
    const config = {
        heartbeatInterval: 25000, // 25 seconds
        reconnectDelay: 3000,     // 3 seconds
        maxReconnectAttempts: 10
    };
    
    /**
     * PULSE-WS: Get WebSocket URL based on current location
     */
    function getWebSocketURL() {
        const scheme = location.protocol === "https:" ? "wss" : "ws";
        return `${scheme}://${location.host}/ws/stream`;
    }
    
    /**
     * PULSE-WS: Connect to WebSocket server
     */
    function connect() {
        try {
            const url = getWebSocketURL();
            console.log('[PULSE-WS] Connecting to:', url);
            
            socket = new WebSocket(url);
            
            socket.onopen = function(event) {
                console.log('[PULSE-WS] Connected successfully');
                reconnectAttempts = 0;
                
                // PULSE-WS: Start heartbeat
                startHeartbeat();
                
                // PULSE-WS: Dispatch connection event
                window.dispatchEvent(new CustomEvent('reactor_connected', {
                    detail: {
                        message: 'Connected to PulseAI Reactor',
                        timestamp: Date.now()
                    }
                }));
            };
            
            socket.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    
                    // PULSE-WS: Handle different message types
                    if (data.type && data.data) {
                        // PULSE-WS: Dispatch custom event
                        window.dispatchEvent(new CustomEvent(data.type, {
                            detail: data.data
                        }));
                        
                        // PULSE-WS: Call specific handlers if they exist
                        if (window.reactor && window.reactor.handlers && window.reactor.handlers[data.type]) {
                            window.reactor.handlers[data.type](data.data);
                        }
                    } else {
                        // PULSE-WS: Handle plain text (like pong)
                        console.log('[PULSE-WS] Received:', data);
                    }
                } catch (error) {
                    // PULSE-WS: Handle non-JSON messages (like pong)
                    console.log('[PULSE-WS] Received text:', event.data);
                }
            };
            
            socket.onclose = function(event) {
                console.warn('[PULSE-WS] Connection closed:', event.code, event.reason);
                stopHeartbeat();
                
                // PULSE-WS: Dispatch disconnect event
                window.dispatchEvent(new CustomEvent('reactor_disconnected', {
                    detail: {
                        code: event.code,
                        reason: event.reason,
                        timestamp: Date.now()
                    }
                }));
                
                // PULSE-WS: Attempt reconnection
                if (reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    console.log(`[PULSE-WS] Reconnecting in ${reconnectDelay}ms (attempt ${reconnectAttempts}/${maxReconnectAttempts})`);
                    
                    reconnectTimeout = setTimeout(connect, reconnectDelay);
                } else {
                    console.error('[PULSE-WS] Max reconnection attempts reached');
                    
                    // PULSE-WS: Dispatch final disconnect event
                    window.dispatchEvent(new CustomEvent('reactor_failed', {
                        detail: {
                            message: 'Max reconnection attempts reached',
                            timestamp: Date.now()
                        }
                    }));
                }
            };
            
            socket.onerror = function(error) {
                console.error('[PULSE-WS] WebSocket error:', error);
                
                // PULSE-WS: Dispatch error event
                window.dispatchEvent(new CustomEvent('reactor_error', {
                    detail: {
                        error: error,
                        timestamp: Date.now()
                    }
                }));
            };
            
        } catch (error) {
            console.error('[PULSE-WS] Connection error:', error);
        }
    }
    
    /**
     * PULSE-WS: Start heartbeat to keep connection alive
     */
    function startHeartbeat() {
        if (heartbeatInterval) {
            clearInterval(heartbeatInterval);
        }
        
        heartbeatInterval = setInterval(function() {
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.send('ping');
            }
        }, config.heartbeatInterval);
    }
    
    /**
     * PULSE-WS: Stop heartbeat
     */
    function stopHeartbeat() {
        if (heartbeatInterval) {
            clearInterval(heartbeatInterval);
            heartbeatInterval = null;
        }
    }
    
    /**
     * PULSE-WS: Disconnect from WebSocket
     */
    function disconnect() {
        if (reconnectTimeout) {
            clearTimeout(reconnectTimeout);
            reconnectTimeout = null;
        }
        
        stopHeartbeat();
        
        if (socket) {
            socket.close();
            socket = null;
        }
    }
    
    /**
     * PULSE-WS: Send message to server
     */
    function send(type, data) {
        if (socket && socket.readyState === WebSocket.OPEN) {
            const message = {
                type: type,
                data: data,
                timestamp: Date.now()
            };
            
            socket.send(JSON.stringify(message));
        } else {
            console.warn('[PULSE-WS] Cannot send message: WebSocket not connected');
        }
    }
    
    /**
     * PULSE-WS: Subscribe to specific events
     */
    function subscribe(events) {
        if (Array.isArray(events)) {
            send('subscribe', events.join(','));
        } else {
            send('subscribe', events);
        }
    }
    
    /**
     * PULSE-WS: Get connection status
     */
    function getStatus() {
        return {
            connected: socket && socket.readyState === WebSocket.OPEN,
            readyState: socket ? socket.readyState : WebSocket.CLOSED,
            reconnectAttempts: reconnectAttempts,
            url: getWebSocketURL()
        };
    }
    
    /**
     * PULSE-WS: Global Reactor client API
     */
    window.reactor = {
        connect: connect,
        disconnect: disconnect,
        send: send,
        subscribe: subscribe,
        getStatus: getStatus,
        config: config,
        handlers: {} // For custom event handlers
        
        // Legacy compatibility methods
        // These maintain compatibility with existing code
    };
    
    // PULSE-WS: Auto-connect when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            // Small delay to ensure all scripts are loaded
            setTimeout(connect, 100);
        });
    } else {
        // DOM is already ready
        setTimeout(connect, 100);
    }
    
    // PULSE-WS: Cleanup on page unload
    window.addEventListener('beforeunload', function() {
        disconnect();
    });
    
    console.log('[PULSE-WS] Reactor WebSocket client initialized');
    
})();