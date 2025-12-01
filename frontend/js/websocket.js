/**
 * WebSocket Client for Phantom Link BBS
 * Manages WebSocket connection with automatic reconnection and exponential backoff
 */
class WebSocketClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 3;
    this.reconnectDelay = 1000; // Start with 1 second
    this.maxReconnectDelay = 8000; // Max 8 seconds
    this.isManualDisconnect = false;
    this.reconnectTimeout = null;
    
    // Callback handlers
    this.messageCallbacks = [];
    this.connectCallbacks = [];
    this.disconnectCallbacks = [];
  }

  /**
   * Connect to WebSocket server with JWT token from localStorage
   */
  connect() {
    // Get JWT token from localStorage
    const token = localStorage.getItem('jwt_token');
    
    if (!token) {
      this.notifyError('No authentication token found. Please login.');
      return;
    }

    // Build WebSocket URL with token as query parameter
    const wsUrl = `${this.url}?token=${encodeURIComponent(token)}`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      
      // Set up event handlers
      this.ws.onopen = this.handleOpen.bind(this);
      this.ws.onmessage = this.handleMessage.bind(this);
      this.ws.onclose = this.handleClose.bind(this);
      this.ws.onerror = this.handleError.bind(this);
      
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.notifyError('Failed to establish connection');
      this.attemptReconnect();
    }
  }

  /**
   * Handle WebSocket connection opened
   */
  handleOpen(event) {
    console.log('WebSocket connected');
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
    this.isManualDisconnect = false;
    
    // Notify connection status
    this.notifyStatus('Connected to Phantom Link BBS');
    
    // Call connect callbacks
    this.connectCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error('Error in connect callback:', error);
      }
    });
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);
      
      // Call all registered message callbacks
      this.messageCallbacks.forEach(callback => {
        try {
          callback(message);
        } catch (error) {
          console.error('Error in message callback:', error);
        }
      });
      
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  /**
   * Handle WebSocket connection closed
   */
  handleClose(event) {
    console.log('WebSocket disconnected', event.code, event.reason);
    
    // Call disconnect callbacks
    this.disconnectCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error('Error in disconnect callback:', error);
      }
    });
    
    // Attempt reconnection if not manually disconnected
    if (!this.isManualDisconnect) {
      this.notifyStatus('Connection lost. Attempting to reconnect...');
      this.attemptReconnect();
    }
  }

  /**
   * Handle WebSocket errors
   */
  handleError(event) {
    console.error('WebSocket error:', event);
    this.notifyError('Connection error occurred');
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  attemptReconnect() {
    // Check if we've exceeded max attempts
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this.notifyError(`Failed to reconnect after ${this.maxReconnectAttempts} attempts. Please refresh the page.`);
      return;
    }
    
    this.reconnectAttempts++;
    
    // Calculate delay with exponential backoff
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );
    
    this.notifyStatus(`Reconnecting in ${delay / 1000} seconds... (Attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    // Clear any existing reconnect timeout
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }
    
    // Schedule reconnection
    this.reconnectTimeout = setTimeout(() => {
      console.log(`Reconnection attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
      this.connect();
    }, delay);
  }

  /**
   * Manually disconnect from WebSocket
   */
  disconnect() {
    this.isManualDisconnect = true;
    
    // Clear any pending reconnect timeout
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    
    // Close WebSocket connection
    if (this.ws) {
      this.ws.close(1000, 'Manual disconnect');
      this.ws = null;
    }
    
    this.notifyStatus('Disconnected');
  }

  /**
   * Send a message through WebSocket
   * @param {Object} message - Message object to send
   */
  send(message) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected');
      this.notifyError('Cannot send message: Not connected');
      return false;
    }
    
    try {
      const jsonMessage = JSON.stringify(message);
      this.ws.send(jsonMessage);
      return true;
    } catch (error) {
      console.error('Error sending message:', error);
      this.notifyError('Failed to send message');
      return false;
    }
  }

  /**
   * Register a callback for incoming messages
   * @param {Function} callback - Function to call when message received
   */
  onMessage(callback) {
    if (typeof callback === 'function') {
      this.messageCallbacks.push(callback);
    }
  }

  /**
   * Register a callback for connection established
   * @param {Function} callback - Function to call when connected
   */
  onConnect(callback) {
    if (typeof callback === 'function') {
      this.connectCallbacks.push(callback);
    }
  }

  /**
   * Register a callback for disconnection
   * @param {Function} callback - Function to call when disconnected
   */
  onDisconnect(callback) {
    if (typeof callback === 'function') {
      this.disconnectCallbacks.push(callback);
    }
  }

  /**
   * Manually trigger reconnection
   */
  reconnect() {
    this.disconnect();
    this.isManualDisconnect = false;
    this.reconnectAttempts = 0;
    setTimeout(() => this.connect(), 100);
  }

  /**
   * Notify connection status (can be overridden or extended)
   * @param {string} message - Status message
   */
  notifyStatus(message) {
    console.log('Status:', message);
    // This can be extended to show UI notifications
    // For now, we'll dispatch a custom event that the UI can listen to
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('ws-status', { 
        detail: { message, type: 'info' } 
      }));
    }
  }

  /**
   * Notify error (can be overridden or extended)
   * @param {string} message - Error message
   */
  notifyError(message) {
    console.error('Error:', message);
    // Dispatch custom event for UI to handle
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('ws-status', { 
        detail: { message, type: 'error' } 
      }));
    }
  }

  /**
   * Check if WebSocket is currently connected
   * @returns {boolean}
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Get current connection state
   * @returns {string} - 'connecting', 'open', 'closing', 'closed', or 'disconnected'
   */
  getState() {
    if (!this.ws) return 'disconnected';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'open';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
        return 'closed';
      default:
        return 'unknown';
    }
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = WebSocketClient;
}
