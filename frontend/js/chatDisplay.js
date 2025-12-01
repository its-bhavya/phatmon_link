/**
 * ChatDisplay Component
 * Handles displaying chat messages with timestamps and formatting
 * Requirements: 5.3, 7.4, 9.2, 9.4, 9.5
 */

export class ChatDisplay {
    /**
     * Initialize the chat display
     * @param {string} containerId - ID of the container element
     */
    constructor(containerId = 'chatDisplay') {
        this.container = document.getElementById(containerId);
        
        if (!this.container) {
            throw new Error(`Chat display container with ID "${containerId}" not found`);
        }
        
        // Auto-scroll is enabled by default
        this.autoScroll = true;
        
        // Track if user has scrolled up manually
        this.setupScrollTracking();
    }
    
    /**
     * Setup scroll tracking to detect manual scrolling
     */
    setupScrollTracking() {
        this.container.addEventListener('scroll', () => {
            // Check if user is at the bottom
            const isAtBottom = this.container.scrollHeight - this.container.scrollTop <= this.container.clientHeight + 50;
            this.autoScroll = isAtBottom;
        });
    }
    
    /**
     * Add a message to the chat display
     * @param {Object} message - Message object
     * @param {string} message.type - Message type ('chat_message', 'system', 'error')
     * @param {string} message.content - Message content
     * @param {string} [message.username] - Username (for chat messages)
     * @param {string} [message.timestamp] - ISO timestamp (optional, will use current time if not provided)
     */
    addMessage(message) {
        const messageElement = this.createMessageElement(message);
        this.container.appendChild(messageElement);
        
        // Auto-scroll to latest message if enabled (Requirement 9.5)
        if (this.autoScroll) {
            this.scrollToBottom();
        }
    }
    
    /**
     * Create a message element
     * @param {Object} message - Message object
     * @returns {HTMLElement}
     */
    createMessageElement(message) {
        const div = document.createElement('div');
        div.className = 'message';
        
        // Format timestamp as [HH:MM:SS] (Requirement 5.3, 9.2)
        const timestamp = this.formatTimestamp(message.timestamp);
        
        // Different styling for system messages (Requirement 9.4)
        if (message.type === 'system') {
            div.classList.add('system');
            div.innerHTML = `<span class="timestamp">${timestamp}</span> <span>* SYSTEM: ${this.escapeHtml(message.content)}</span>`;
        } else if (message.type === 'error') {
            div.classList.add('error');
            div.innerHTML = `<span class="timestamp">${timestamp}</span> <span>* ERROR: ${this.escapeHtml(message.content)}</span>`;
        } else if (message.type === 'chat_message' || message.username) {
            // Format messages as "[HH:MM:SS] <username> message" (Requirement 5.3)
            const username = message.username || 'Unknown';
            div.innerHTML = `<span class="timestamp">${timestamp}</span> <span class="username">&lt;${this.escapeHtml(username)}&gt;</span> ${this.escapeHtml(message.content)}`;
        } else {
            // Generic message
            div.innerHTML = `<span class="timestamp">${timestamp}</span> <span>${this.escapeHtml(message.content)}</span>`;
        }
        
        return div;
    }
    
    /**
     * Format timestamp as [HH:MM:SS]
     * @param {string|Date} [timestamp] - ISO timestamp or Date object
     * @returns {string} Formatted timestamp
     */
    formatTimestamp(timestamp) {
        const date = timestamp ? new Date(timestamp) : new Date();
        
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        
        return `[${hours}:${minutes}:${seconds}]`;
    }
    
    /**
     * Escape HTML to prevent XSS attacks
     * @param {string} text - Text to escape
     * @returns {string} Escaped text
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    /**
     * Clear all messages from the display (for /clear command)
     * Requirement 7.4
     */
    clear() {
        this.container.innerHTML = '';
        this.autoScroll = true;
    }
    
    /**
     * Scroll to the bottom of the chat display
     */
    scrollToBottom() {
        this.container.scrollTop = this.container.scrollHeight;
    }
    
    /**
     * Add multiple messages at once
     * @param {Array<Object>} messages - Array of message objects
     */
    addMessages(messages) {
        messages.forEach(message => this.addMessage(message));
    }
    
    /**
     * Get the number of messages currently displayed
     * @returns {number}
     */
    getMessageCount() {
        return this.container.children.length;
    }
    
    /**
     * Enable auto-scroll
     */
    enableAutoScroll() {
        this.autoScroll = true;
        this.scrollToBottom();
    }
    
    /**
     * Disable auto-scroll
     */
    disableAutoScroll() {
        this.autoScroll = false;
    }
    
    /**
     * Check if auto-scroll is enabled
     * @returns {boolean}
     */
    isAutoScrollEnabled() {
        return this.autoScroll;
    }
}
