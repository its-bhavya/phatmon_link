/**
 * VecnaHandler Component
 * Handles Vecna-specific message types and state management
 * Requirements: 3.3, 4.2, 4.5, 9.1, 9.3, 9.4
 */

export class VecnaHandler {
    /**
     * Initialize the Vecna handler
     * @param {ChatDisplay} chatDisplay - Chat display instance
     * @param {CommandLineBar} commandBar - Command bar instance
     * @param {VecnaEffects} vecnaEffects - Vecna effects instance
     */
    constructor(chatDisplay, commandBar, vecnaEffects) {
        this.chatDisplay = chatDisplay;
        this.commandBar = commandBar;
        this.vecnaEffects = vecnaEffects;
        this.isGripActive = false;
        this.gripReleaseTimer = null;
    }
    
    /**
     * Handle Vecna emotional trigger message (Requirement 3.3)
     * Displays corrupted hostile response with special styling
     * @param {Object} message - Vecna emotional trigger message
     * @param {string} message.content - Corrupted message content
     * @param {string} [message.corruption_level] - Corruption level applied
     */
    handleEmotionalTrigger(message) {
        // Apply text corruption effects and display the message
        const messageElement = this.vecnaEffects.applyTextCorruption(message.content);
        this.chatDisplay.container.appendChild(messageElement);
        
        // Auto-scroll to show the new message
        if (this.chatDisplay.autoScroll) {
            this.chatDisplay.scrollToBottom();
        }
    }
    
    /**
     * Handle Psychic Grip activation (Requirements 4.2, 9.1, 9.4)
     * Freezes input, starts visual effects, and displays narrative with animation
     * @param {Object} message - Psychic Grip message
     * @param {string} message.content - Narrative content
     * @param {number} message.duration - Freeze duration in seconds
     * @param {Array<string>} [message.effects] - Visual effects to apply
     */
    handlePsychicGrip(message) {
        if (this.isGripActive) {
            return;
        }
        
        this.isGripActive = true;
        
        // Disable input during Psychic Grip (Requirement 4.2)
        this.commandBar.disable();
        
        // Start visual effects
        const duration = message.duration || 7;
        const effects = message.effects || ['flicker', 'inverted', 'scanlines', 'static'];
        this.vecnaEffects.startPsychicGrip(duration, effects);
        
        // Display Vecna message with character-by-character animation (Requirement 9.4)
        this.displayVecnaMessage(message.content, true);
        
        // Schedule grip release (Requirement 4.5)
        this.gripReleaseTimer = setTimeout(() => {
            this.handleGripRelease();
        }, duration * 1000);
    }
    
    /**
     * Handle Psychic Grip release (Requirement 4.5)
     * Ends visual effects, re-enables input, and shows system message
     */
    handleGripRelease() {
        if (!this.isGripActive) {
            return;
        }
        
        this.isGripActive = false;
        
        // Clear any pending release timer
        if (this.gripReleaseTimer) {
            clearTimeout(this.gripReleaseTimer);
            this.gripReleaseTimer = null;
        }
        
        // End visual effects
        this.vecnaEffects.endPsychicGrip();
        
        // Re-enable input
        this.commandBar.enable();
        
        // Display system message indicating control return (Requirement 4.5)
        this.chatDisplay.addMessage({
            type: 'system',
            content: 'Control returned to SysOp. Continue your session.'
        });
    }
    
    /**
     * Display Vecna message with special styling (Requirements 9.1, 9.3)
     * @param {string} content - Message content
     * @param {boolean} isGrip - Whether this is a Psychic Grip message (enables animation)
     */
    displayVecnaMessage(content, isGrip = false) {
        // Ensure [VECNA] prefix is present (Requirement 9.1)
        const prefixedContent = content.startsWith('[VECNA]') ? content : `[VECNA] ${content}`;
        
        // Create message element with Vecna styling (Requirement 9.3)
        const messageElement = document.createElement('div');
        messageElement.className = 'message vecna-message';
        
        // Format timestamp
        const timestamp = this.formatTimestamp();
        
        // Create timestamp span
        const timestampSpan = document.createElement('span');
        timestampSpan.className = 'timestamp';
        timestampSpan.textContent = timestamp;
        messageElement.appendChild(timestampSpan);
        
        // Add space
        messageElement.appendChild(document.createTextNode(' '));
        
        // Create content span
        const contentSpan = document.createElement('span');
        contentSpan.className = 'vecna-text';
        
        if (isGrip) {
            // Apply character-by-character animation for Psychic Grip (Requirement 9.4)
            this.animateCharacterByCharacter(contentSpan, prefixedContent);
        } else {
            // Display immediately for emotional triggers
            contentSpan.textContent = prefixedContent;
        }
        
        messageElement.appendChild(contentSpan);
        
        // Add to chat display
        this.chatDisplay.container.appendChild(messageElement);
        
        // Auto-scroll to show the new message
        if (this.chatDisplay.autoScroll) {
            this.chatDisplay.scrollToBottom();
        }
    }
    
    /**
     * Animate text character-by-character (Requirement 9.4)
     * @param {HTMLElement} element - Element to animate
     * @param {string} text - Text to display
     * @param {number} delayMs - Delay between characters in milliseconds
     */
    animateCharacterByCharacter(element, text, delayMs = 50) {
        let index = 0;
        
        const animate = () => {
            if (index < text.length) {
                element.textContent += text[index];
                index++;
                
                // Auto-scroll during animation
                if (this.chatDisplay.autoScroll) {
                    this.chatDisplay.scrollToBottom();
                }
                
                setTimeout(animate, delayMs);
            }
        };
        
        animate();
    }
    
    /**
     * Format timestamp as [HH:MM:SS]
     * @returns {string} Formatted timestamp
     */
    formatTimestamp() {
        const date = new Date();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');
        return `[${hours}:${minutes}:${seconds}]`;
    }
    
    /**
     * Check if Psychic Grip is currently active
     * @returns {boolean}
     */
    isGripCurrentlyActive() {
        return this.isGripActive;
    }
    
    /**
     * Force release Psychic Grip (for emergency cleanup)
     */
    forceRelease() {
        if (this.isGripActive) {
            this.handleGripRelease();
        }
    }
}
