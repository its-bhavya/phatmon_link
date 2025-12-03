/**
 * VecnaEffects Component
 * Manages visual effects during Vecna activation
 * Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
 */

export class VecnaEffects {
    /**
     * Initialize the Vecna effects manager
     * @param {HTMLElement} chatDisplay - The chat display container element
     */
    constructor(chatDisplay) {
        this.chatDisplay = chatDisplay;
        this.isActive = false;
        this.effectsContainer = null;
        this.staticInterval = null;
        this.flickerInterval = null;
    }
    
    /**
     * Apply text corruption effect to message display (Requirement 5.1)
     * @param {string} message - The corrupted message to display
     * @returns {HTMLElement} The message element with corruption styling
     */
    applyTextCorruption(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message vecna-corrupted';
        
        // Add [VECNA] prefix if not already present
        const content = message.startsWith('[VECNA]') ? message : `[VECNA] ${message}`;
        
        // Create timestamp
        const timestamp = this.formatTimestamp();
        
        messageElement.innerHTML = `<span class="timestamp">${timestamp}</span> <span class="vecna-text">${this.escapeHtml(content)}</span>`;
        
        return messageElement;
    }
    
    /**
     * Start Psychic Grip visual effects (Requirements 5.2, 5.3, 5.4, 5.5)
     * @param {number} duration - Duration in seconds
     * @param {Array<string>} effects - Array of effect names to apply
     */
    startPsychicGrip(duration, effects = ['flicker', 'inverted', 'scanlines', 'static']) {
        if (this.isActive) {
            return;
        }
        
        this.isActive = true;
        
        // Create effects container if it doesn't exist
        if (!this.effectsContainer) {
            this.effectsContainer = document.createElement('div');
            this.effectsContainer.className = 'vecna-effects-container';
            document.body.appendChild(this.effectsContainer);
        }
        
        // Apply screen flicker effect (Requirement 5.2)
        if (effects.includes('flicker')) {
            this.applyScreenFlicker();
        }
        
        // Apply inverted colors effect (Requirement 5.3)
        if (effects.includes('inverted')) {
            this.applyInvertedColors();
        }
        
        // Apply scanline ripple effect (Requirement 5.4)
        if (effects.includes('scanlines')) {
            this.applyScanlineRipple();
        }
        
        // Apply ASCII static storm effect (Requirement 5.5)
        if (effects.includes('static')) {
            this.showStaticStorm();
        }
        
        // Schedule cleanup after duration
        setTimeout(() => {
            this.endPsychicGrip();
        }, duration * 1000);
    }
    
    /**
     * End Psychic Grip and restore normal display (Requirement 5.6)
     */
    endPsychicGrip() {
        if (!this.isActive) {
            return;
        }
        
        this.isActive = false;
        
        // Remove all visual effects
        this.removeScreenFlicker();
        this.removeInvertedColors();
        this.removeScanlineRipple();
        this.hideStaticStorm();
        
        // Clean up effects container
        if (this.effectsContainer) {
            this.effectsContainer.remove();
            this.effectsContainer = null;
        }
    }
    
    /**
     * Apply screen flicker effect (Requirement 5.2)
     */
    applyScreenFlicker() {
        const terminalScreen = document.querySelector('.terminal-screen');
        if (terminalScreen) {
            terminalScreen.classList.add('vecna-psychic-grip');
        }
        
        // Add random flicker intensity changes
        this.flickerInterval = setInterval(() => {
            if (terminalScreen) {
                const opacity = 0.7 + Math.random() * 0.3;
                terminalScreen.style.opacity = opacity;
            }
        }, 100);
    }
    
    /**
     * Remove screen flicker effect
     */
    removeScreenFlicker() {
        const terminalScreen = document.querySelector('.terminal-screen');
        if (terminalScreen) {
            terminalScreen.classList.remove('vecna-psychic-grip');
            terminalScreen.style.opacity = '1';
        }
        
        if (this.flickerInterval) {
            clearInterval(this.flickerInterval);
            this.flickerInterval = null;
        }
    }
    
    /**
     * Apply inverted color effect (Requirement 5.3)
     */
    applyInvertedColors() {
        const terminalScreen = document.querySelector('.terminal-screen');
        if (terminalScreen) {
            terminalScreen.classList.add('vecna-inverted');
        }
    }
    
    /**
     * Remove inverted color effect
     */
    removeInvertedColors() {
        const terminalScreen = document.querySelector('.terminal-screen');
        if (terminalScreen) {
            terminalScreen.classList.remove('vecna-inverted');
        }
    }
    
    /**
     * Apply scanline ripple effect (Requirement 5.4)
     */
    applyScanlineRipple() {
        if (!this.effectsContainer) {
            return;
        }
        
        const scanlines = document.createElement('div');
        scanlines.className = 'vecna-scanlines';
        this.effectsContainer.appendChild(scanlines);
    }
    
    /**
     * Remove scanline ripple effect
     */
    removeScanlineRipple() {
        if (this.effectsContainer) {
            const scanlines = this.effectsContainer.querySelector('.vecna-scanlines');
            if (scanlines) {
                scanlines.remove();
            }
        }
    }
    
    /**
     * Show ASCII static storm overlay (Requirement 5.5)
     */
    showStaticStorm() {
        if (!this.effectsContainer) {
            return;
        }
        
        const staticOverlay = document.createElement('div');
        staticOverlay.className = 'vecna-static';
        this.effectsContainer.appendChild(staticOverlay);
        
        // Generate random ASCII characters for static effect
        this.updateStaticContent(staticOverlay);
        
        // Update static content periodically for animation
        this.staticInterval = setInterval(() => {
            this.updateStaticContent(staticOverlay);
        }, 50);
    }
    
    /**
     * Hide ASCII static storm overlay
     */
    hideStaticStorm() {
        if (this.staticInterval) {
            clearInterval(this.staticInterval);
            this.staticInterval = null;
        }
        
        if (this.effectsContainer) {
            const staticOverlay = this.effectsContainer.querySelector('.vecna-static');
            if (staticOverlay) {
                staticOverlay.remove();
            }
        }
    }
    
    /**
     * Update static overlay content with random ASCII characters
     * @param {HTMLElement} staticOverlay - The static overlay element
     */
    updateStaticContent(staticOverlay) {
        const chars = '█▓▒░▄▀■□▪▫';
        const rows = 30;
        const cols = 80;
        let content = '';
        
        for (let i = 0; i < rows; i++) {
            for (let j = 0; j < cols; j++) {
                // Random character with some empty spaces
                if (Math.random() > 0.7) {
                    content += chars[Math.floor(Math.random() * chars.length)];
                } else {
                    content += ' ';
                }
            }
            content += '\n';
        }
        
        staticOverlay.textContent = content;
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
     * Check if Vecna effects are currently active
     * @returns {boolean}
     */
    isEffectsActive() {
        return this.isActive;
    }
}
