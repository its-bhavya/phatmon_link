/**
 * InstantAnswerHandler Component
 * Handles instant answer messages from the AI recall system
 * Requirements: 7.1, 7.2, 7.4
 */

export class InstantAnswerHandler {
    /**
     * Initialize the instant answer handler
     * @param {ChatDisplay} chatDisplay - ChatDisplay instance for rendering messages
     */
    constructor(chatDisplay) {
        this.chatDisplay = chatDisplay;
    }
    
    /**
     * Handle instant answer message
     * Requirement 7.1, 7.2, 7.4
     * @param {Object} message - Instant answer message from server
     * @param {string} message.content - AI-generated summary content
     * @param {Array} message.sources - Source messages with username, timestamp, snippet
     * @param {boolean} message.is_novel - Whether this is a novel question
     * @param {string} [message.timestamp] - ISO timestamp
     */
    handleInstantAnswer(message) {
        // Display the instant answer with special styling
        this.displayInstantAnswer(message.content, message.sources, message.is_novel, message.timestamp);
    }
    
    /**
     * Display instant answer message with [INSTANT ANSWER] prefix and special styling
     * Requirement 7.1, 7.2
     * @param {string} content - AI-generated summary content
     * @param {Array} sources - Source messages array
     * @param {boolean} isNovel - Whether this is a novel question
     * @param {string} [timestamp] - ISO timestamp
     */
    displayInstantAnswer(content, sources, isNovel, timestamp = null) {
        // Create instant answer message element with custom styling
        const messageElement = this.createInstantAnswerElement(content, sources, isNovel, timestamp);
        
        // Add to chat display container directly
        const container = this.chatDisplay.container;
        container.appendChild(messageElement);
        
        // Auto-scroll if enabled
        if (this.chatDisplay.autoScroll) {
            this.chatDisplay.scrollToBottom();
        }
    }
    
    /**
     * Create an instant answer message element with [INSTANT ANSWER] prefix
     * Requirement 7.1, 7.2, 7.4
     * @param {string} content - AI-generated summary content
     * @param {Array} sources - Source messages array
     * @param {boolean} isNovel - Whether this is a novel question
     * @param {string} [timestamp] - ISO timestamp
     * @returns {HTMLElement}
     */
    createInstantAnswerElement(content, sources, isNovel, timestamp = null) {
        const div = document.createElement('div');
        div.className = 'message instant-answer-message';
        
        // Format timestamp
        const formattedTimestamp = this.formatTimestamp(timestamp);
        
        // Create timestamp span
        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'timestamp';
        timestampSpan.textContent = formattedTimestamp;
        
        // Create instant answer prefix
        const instantAnswerPrefix = document.createElement('span');
        instantAnswerPrefix.className = 'instant-answer-prefix';
        instantAnswerPrefix.textContent = '[INSTANT ANSWER]';
        
        // Create content container
        const contentContainer = document.createElement('div');
        contentContainer.className = 'instant-answer-content-container';
        
        // Add AI disclaimer (Requirement 7.2)
        const disclaimer = document.createElement('div');
        disclaimer.className = 'instant-answer-disclaimer';
        disclaimer.textContent = '⚠ AI-generated from past discussions';
        contentContainer.appendChild(disclaimer);
        
        // Handle novel questions
        if (isNovel) {
            const novelMessage = document.createElement('div');
            novelMessage.className = 'instant-answer-novel';
            novelMessage.textContent = 'This appears to be a new question. No similar past discussions found.';
            contentContainer.appendChild(novelMessage);
        } else {
            // Add main content
            const contentSpan = document.createElement('div');
            contentSpan.className = 'instant-answer-content';
            contentSpan.textContent = content;
            contentContainer.appendChild(contentSpan);
            
            // Add source attribution if sources exist (Requirement 7.4)
            if (sources && sources.length > 0) {
                const sourcesContainer = document.createElement('div');
                sourcesContainer.className = 'instant-answer-sources';
                
                const sourcesHeader = document.createElement('div');
                sourcesHeader.className = 'instant-answer-sources-header';
                sourcesHeader.textContent = 'Sources:';
                sourcesContainer.appendChild(sourcesHeader);
                
                sources.forEach((source, index) => {
                    const sourceItem = document.createElement('div');
                    sourceItem.className = 'instant-answer-source-item';
                    
                    // Format source timestamp
                    const sourceTimestamp = this.formatSourceTimestamp(source.timestamp);
                    
                    // Create source text with username and timestamp
                    sourceItem.textContent = `${index + 1}. ${source.username} (${sourceTimestamp})`;
                    
                    // Add snippet if available
                    if (source.snippet) {
                        const snippetDiv = document.createElement('div');
                        snippetDiv.className = 'instant-answer-source-snippet';
                        snippetDiv.textContent = `   "${source.snippet}"`;
                        sourceItem.appendChild(snippetDiv);
                    }
                    
                    sourcesContainer.appendChild(sourceItem);
                });
                
                contentContainer.appendChild(sourcesContainer);
            }
        }
        
        // Assemble the message
        div.appendChild(timestampSpan);
        div.appendChild(document.createTextNode(' '));
        div.appendChild(instantAnswerPrefix);
        div.appendChild(contentContainer);
        
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
     * Format source timestamp as readable date/time
     * @param {string|Date} timestamp - ISO timestamp or Date object
     * @returns {string} Formatted timestamp
     */
    formatSourceTimestamp(timestamp) {
        const date = new Date(timestamp);
        
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        
        return `${month}/${day} ${hours}:${minutes}`;
    }
}
