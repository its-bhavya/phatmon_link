/**
 * CommandLineBar Component
 * Handles user input, command history, and message submission
 * Requirements: 3.3, 3.4, 5.4, 7.1, 7.2, 7.3, 7.4, 7.5
 */

export class CommandLineBar {
    /**
     * Initialize the command line bar
     * @param {Function} onSubmit - Callback for regular messages
     * @param {Function} onCommand - Callback for commands (starting with /)
     */
    constructor(onSubmit, onCommand) {
        this.onSubmit = onSubmit;
        this.onCommand = onCommand;
        this.history = [];
        this.historyIndex = -1;
        this.currentInput = '';
        
        // Get DOM elements
        this.inputElement = document.getElementById('commandInput');
        
        if (!this.inputElement) {
            throw new Error('Command input element not found');
        }
        
        // Initialize event handlers
        this.initializeEventHandlers();
        
        // Focus input on load
        this.focus();
    }
    
    /**
     * Initialize event handlers for input
     */
    initializeEventHandlers() {
        // Handle Enter key to submit input
        this.inputElement.addEventListener('keydown', (event) => {
            this.handleKeyDown(event);
        });
        
        // Handle input changes
        this.inputElement.addEventListener('input', (event) => {
            this.handleInput(event);
        });
        
        // Ensure input stays focused
        this.inputElement.addEventListener('blur', () => {
            // Re-focus after a short delay to allow other interactions
            setTimeout(() => {
                if (document.activeElement !== this.inputElement) {
                    this.focus();
                }
            }, 100);
        });
    }
    
    /**
     * Handle keyboard input events
     * @param {KeyboardEvent} event
     */
    handleKeyDown(event) {
        switch (event.key) {
            case 'Enter':
                event.preventDefault();
                this.submitInput();
                break;
                
            case 'ArrowUp':
                event.preventDefault();
                this.navigateHistory('up');
                break;
                
            case 'ArrowDown':
                event.preventDefault();
                this.navigateHistory('down');
                break;
        }
    }
    
    /**
     * Handle input changes
     * @param {Event} event
     */
    handleInput(event) {
        // Store current input when not navigating history
        if (this.historyIndex === -1) {
            this.currentInput = this.inputElement.value;
        }
    }
    
    /**
     * Submit the current input
     */
    submitInput() {
        const input = this.inputElement.value.trim();
        
        // Don't submit empty input
        if (!input) {
            return;
        }
        
        // Add to history
        this.addToHistory(input);
        
        // Distinguish between commands (starting with /) and regular messages
        if (input.startsWith('/')) {
            // Extract command and arguments
            const parts = input.slice(1).split(' ');
            const command = parts[0].toLowerCase();
            const args = parts.slice(1);
            
            // Call command callback
            if (this.onCommand) {
                this.onCommand(command, args, input);
            }
        } else {
            // Regular message
            if (this.onSubmit) {
                this.onSubmit(input);
            }
        }
        
        // Clear input after submission (Requirement 5.4)
        this.clearInput();
    }
    
    /**
     * Clear the input field
     */
    clearInput() {
        this.inputElement.value = '';
        this.currentInput = '';
        this.historyIndex = -1;
        this.focus();
    }
    
    /**
     * Add text to command history
     * @param {string} text
     */
    addToHistory(text) {
        // Don't add duplicate consecutive entries
        if (this.history.length === 0 || this.history[this.history.length - 1] !== text) {
            this.history.push(text);
        }
        
        // Reset history navigation
        this.historyIndex = -1;
        this.currentInput = '';
    }
    
    /**
     * Navigate through command history with up/down arrows
     * @param {string} direction - 'up' or 'down'
     */
    navigateHistory(direction) {
        if (this.history.length === 0) {
            return;
        }
        
        if (direction === 'up') {
            // Moving backwards in history (older commands)
            if (this.historyIndex === -1) {
                // Save current input before navigating
                this.currentInput = this.inputElement.value;
                this.historyIndex = this.history.length - 1;
            } else if (this.historyIndex > 0) {
                this.historyIndex--;
            }
            
            // Set input to history item
            this.inputElement.value = this.history[this.historyIndex];
        } else if (direction === 'down') {
            // Moving forwards in history (newer commands)
            if (this.historyIndex === -1) {
                // Already at current input, do nothing
                return;
            }
            
            if (this.historyIndex < this.history.length - 1) {
                this.historyIndex++;
                this.inputElement.value = this.history[this.historyIndex];
            } else {
                // Reached the end, restore current input
                this.historyIndex = -1;
                this.inputElement.value = this.currentInput;
            }
        }
        
        // Move cursor to end of input
        this.inputElement.setSelectionRange(
            this.inputElement.value.length,
            this.inputElement.value.length
        );
    }
    
    /**
     * Get command history
     * @returns {Array<string>}
     */
    getHistory() {
        return [...this.history];
    }
    
    /**
     * Focus the input element
     */
    focus() {
        this.inputElement.focus();
    }
    
    /**
     * Show the cursor (cursor is handled by CSS animation)
     */
    showCursor() {
        // Cursor visibility is handled by CSS animation
        // This method is here for interface compatibility
        this.focus();
    }
    
    /**
     * Set the input value programmatically
     * @param {string} value
     */
    setValue(value) {
        this.inputElement.value = value;
        this.currentInput = value;
    }
    
    /**
     * Get the current input value
     * @returns {string}
     */
    getValue() {
        return this.inputElement.value;
    }
    
    /**
     * Disable the input
     */
    disable() {
        this.inputElement.disabled = true;
    }
    
    /**
     * Enable the input
     */
    enable() {
        this.inputElement.disabled = false;
        this.focus();
    }
}
