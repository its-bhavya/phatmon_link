/**
 * SupportHandler Component
 * Handles support bot messages and crisis hotline information
 * Requirements: 12.1, 12.2, 12.3, 12.4
 */

export class SupportHandler {
    /**
     * Initialize the support handler
     * @param {ChatDisplay} chatDisplay - ChatDisplay instance for rendering messages
     * @param {CommandLineBar} commandBar - CommandLineBar instance (optional, for future use)
     */
    constructor(chatDisplay, commandBar = null) {
        this.chatDisplay = chatDisplay;
        this.commandBar = commandBar;
        this.inSupportRoom = false;
    }
    
    /**
     * Handle support room creation and initial greeting
     * Requirement 12.1, 12.3
     * @param {Object} message - Support activation message from server
     * @param {string} message.content - Greeting message content
     * @param {string} message.room - Support room name
     * @param {string} [message.timestamp] - ISO timestamp
     */
    handleSupportActivation(message) {
        // Mark that user is now in a support room
        this.inSupportRoom = true;
        
        // Display the support activation message with [SUPPORT] prefix
        this.displaySupportMessage(message.content, message.timestamp);
    }
    
    /**
     * Handle support bot response
     * Requirement 12.1, 12.2
     * @param {Object} message - Support response message from server
     * @param {string} message.content - Bot response content
     * @param {string} [message.timestamp] - ISO timestamp
     */
    handleSupportResponse(message) {
        // Display the support response with [SUPPORT] prefix
        this.displaySupportMessage(message.content, message.timestamp);
    }
    
    /**
     * Handle crisis hotline information
     * Requirement 12.1, 12.2, 12.4
     * @param {Object} message - Crisis hotlines message from server
     * @param {string} message.content - Formatted hotline information
     * @param {string} [message.timestamp] - ISO timestamp
     */
    handleCrisisHotlines(message) {
        // Display crisis hotline information with prominent styling
        this.displayCrisisMessage(message.content, message.timestamp);
    }
    
    /**
     * Display support message with [SUPPORT] prefix and special styling
     * Requirement 12.1, 12.2
     * @param {string} content - Message content
     * @param {string} [timestamp] - ISO timestamp
     */
    displaySupportMessage(content, timestamp = null) {
        // Create message element manually for custom styling
        const messageElement = this.createSupportMessageElement(content, timestamp);
        
        // Add to chat display container directly
        const container = this.chatDisplay.container;
        container.appendChild(messageElement);
        
        // Auto-scroll if enabled
        if (this.chatDisplay.autoScroll) {
            this.chatDisplay.scrollToBottom();
        }
    }
    
    /**
     * Display crisis message with prominent styling
     * Requirement 12.1, 12.2, 12.4
     * @param {string} content - Crisis message content
     * @param {string} [timestamp] - ISO timestamp
     */
    displayCrisisMessage(content, timestamp = null) {
        // Create crisis message element with special styling
        const messageElement = this.createCrisisMessageElement(content, timestamp);
        
        // Add to chat display container directly
        const container = this.chatDisplay.container;
        container.appendChild(messageElement);
        
        // Auto-scroll if enabled
        if (this.chatDisplay.autoScroll) {
            this.chatDisplay.scrollToBottom();
        }
    }
    
    /**
     * Create a support message element with [SUPPORT] prefix
     * Requirement 12.1, 12.2
     * @param {string} content - Message content
     * @param {string} [timestamp] - ISO timestamp
     * @returns {HTMLElement}
     */
    createSupportMessageElement(content, timestamp = null) {
        const div = document.createElement('div');
        div.className = 'message support-message';
        
        // Format timestamp
        const formattedTimestamp = this.formatTimestamp(timestamp);
        
        // Create message with [SUPPORT] prefix
        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'timestamp';
        timestampSpan.textContent = formattedTimestamp;
        
        const supportPrefix = document.createElement('span');
        supportPrefix.className = 'support-prefix';
        supportPrefix.textContent = '[SUPPORT]';
        
        const contentSpan = document.createElement('span');
        contentSpan.className = 'support-content';
        contentSpan.textContent = ` ${content}`;
        
        div.appendChild(timestampSpan);
        div.appendChild(document.createTextNode(' '));
        div.appendChild(supportPrefix);
        div.appendChild(contentSpan);
        
        return div;
    }
    
    /**
     * Create a crisis message element with prominent styling
     * Requirement 12.1, 12.2, 12.4
     * @param {string} content - Crisis message content
     * @param {string} [timestamp] - ISO timestamp
     * @returns {HTMLElement}
     */
    createCrisisMessageElement(content, timestamp = null) {
        const div = document.createElement('div');
        div.className = 'message crisis-message';
        
        // Format timestamp
        const formattedTimestamp = this.formatTimestamp(timestamp);
        
        // Create message with [SUPPORT] prefix and crisis styling
        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'timestamp';
        timestampSpan.textContent = formattedTimestamp;
        
        const supportPrefix = document.createElement('span');
        supportPrefix.className = 'support-prefix crisis-prefix';
        supportPrefix.textContent = '[SUPPORT - CRISIS RESOURCES]';
        
        const contentSpan = document.createElement('span');
        contentSpan.className = 'crisis-content';
        contentSpan.textContent = ` ${content}`;
        
        div.appendChild(timestampSpan);
        div.appendChild(document.createTextNode(' '));
        div.appendChild(supportPrefix);
        div.appendChild(contentSpan);
        
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
     * Check if user is currently in a support room
     * @returns {boolean}
     */
    isInSupportRoom() {
        return this.inSupportRoom;
    }
    
    /**
     * Mark that user has left the support room
     */
    leaveSupportRoom() {
        this.inSupportRoom = false;
    }
}
