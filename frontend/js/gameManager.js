/**
 * Game Manager
 * Orchestrates game lifecycle, canvas management, and game state transitions
 * Requirements: 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.5, 10.1, 10.2, 10.3, 10.4
 * 
 * Performance Optimizations:
 * - Keyboard-only input (Requirement 10.1): Mouse/touch disabled for game controls
 * - FPS monitoring (Requirement 10.2): Tracks and maintains 30+ FPS
 * - Input debouncing (Requirement 10.3): Prevents input flooding at ~60Hz
 * - Input latency tracking (Requirement 10.4): Measures and warns if > 50ms
 * 
 * SILENT DESIGN REQUIREMENT (Requirements 11.1, 11.2, 11.3, 11.4, 11.5):
 * All games managed by this system are intentionally designed to be completely silent.
 * - No audio elements are created in any game code
 * - No audio files are loaded or referenced
 * - No sound playback occurs during gameplay or events
 * - All feedback is provided through visual means only
 * This maintains the quiet retro-terminal atmosphere of the BBS.
 */

import { HighScoreManager } from './highScores.js';

export class GameManager {
    /**
     * @param {ChatDisplay} chatDisplay - Reference to chat display
     * @param {CommandLineBar} commandBar - Reference to command bar
     * @param {SidePanel} sidePanel - Reference to side panel
     */
    constructor(chatDisplay, commandBar, sidePanel) {
        this.chatDisplay = chatDisplay;
        this.commandBar = commandBar;
        this.sidePanel = sidePanel;
        
        // Game state
        this.isActive = false;
        this.currentGame = null;
        this.canvas = null;
        this.gameInstance = null;
        this.animationFrameId = null;
        this.lastFrameTime = 0;
        
        // Canvas configuration (monochrome retro style)
        this.canvasConfig = {
            backgroundColor: '#000000',  // Pure black
            foregroundColor: '#FFFFFF',  // Pure white
            font: 'VT323, Courier New, monospace',
            fontSize: 19
        };
        
        // Keyboard event handler (bound to this instance)
        this.keyDownHandler = this.handleKeyDown.bind(this);
        this.keyUpHandler = this.handleKeyUp.bind(this);
        
        // Exit icon configuration
        this.exitIconSize = 30;
        this.exitIconPadding = 10;
        
        // Performance monitoring (Requirement 10.2, 10.4)
        this.performanceMetrics = {
            fps: 0,
            frameCount: 0,
            lastFpsUpdate: 0,
            inputLatency: 0,
            lastInputTime: 0
        };
        
        // Input debouncing (Requirement 10.3)
        this.inputDebounce = {
            lastKeyTime: {},
            debounceDelay: 16 // ~60Hz input rate (16ms between inputs)
        };
        
        // Keyboard-only input enforcement (Requirement 10.1)
        this.mouseInputDisabled = true;
        this.touchInputDisabled = true;
    }
    
    /**
     * Launch a game
     * @param {string} gameName - Name of the game to launch (snake, tetris, breakout)
     * @returns {Promise<boolean>} - True if game launched successfully
     */
    async launchGame(gameName) {
        // Validate game name
        const validGames = ['snake', 'tetris', 'breakout'];
        if (!validGames.includes(gameName.toLowerCase())) {
            console.error('Invalid game name:', gameName);
            return false;
        }
        
        // Exit any active game first
        if (this.isActive) {
            this.exitGame();
        }
        
        // Create canvas
        if (!this.createCanvas()) {
            console.error('Failed to create canvas');
            return false;
        }
        
        // Initialize game instance (will be implemented when games are created)
        try {
            this.currentGame = gameName.toLowerCase();
            this.gameInstance = await this.createGameInstance(gameName);
            
            if (!this.gameInstance) {
                throw new Error('Failed to create game instance');
            }
            
            // Initialize and start game
            this.gameInstance.init();
            this.gameInstance.start();
            
            // Set up keyboard listeners
            document.addEventListener('keydown', this.keyDownHandler);
            document.addEventListener('keyup', this.keyUpHandler);
            
            // Start game loop
            this.isActive = true;
            this.lastFrameTime = performance.now();
            this.startGameLoop();
            
            return true;
        } catch (error) {
            console.error('Failed to launch game:', error);
            this.removeCanvas();
            return false;
        }
    }
    
    /**
     * Create game instance based on game name
     * @param {string} gameName - Name of the game
     * @returns {Game|null} - Game instance or null
     */
    async createGameInstance(gameName) {
        const ctx = this.canvas.getContext('2d');
        
        switch (gameName.toLowerCase()) {
            case 'snake': {
                const { SnakeGame } = await import('./snake.js');
                return new SnakeGame(this.canvas, ctx);
            }
            case 'tetris': {
                const { TetrisGame } = await import('./tetris.js');
                return new TetrisGame(this.canvas, ctx);
            }
            case 'breakout': {
                const { BreakoutGame } = await import('./breakout.js');
                return new BreakoutGame(this.canvas, ctx);
            }
            default:
                console.error('Unknown game:', gameName);
                return null;
        }
    }
    
    /**
     * Exit the current game
     */
    exitGame() {
        if (!this.isActive) {
            return;
        }
        
        // Stop game loop
        this.stopGameLoop();
        
        // Save high score if applicable
        if (this.gameInstance && this.currentGame) {
            const finalScore = this.gameInstance.getScore();
            const isNewHigh = HighScoreManager.updateHighScore(this.currentGame, finalScore);
            
            if (isNewHigh) {
                console.log(`New high score for ${this.currentGame}: ${finalScore}`);
            }
        }
        
        // Stop game instance
        if (this.gameInstance) {
            try {
                this.gameInstance.stop();
            } catch (error) {
                console.error('Error stopping game:', error);
            }
        }
        
        // Remove keyboard listeners
        document.removeEventListener('keydown', this.keyDownHandler);
        document.removeEventListener('keyup', this.keyUpHandler);
        
        // Remove canvas and restore chat
        this.removeCanvas();
        
        // Reset state
        this.isActive = false;
        this.currentGame = null;
        this.gameInstance = null;
        this.animationFrameId = null;
    }
    
    /**
     * Check if a game is currently active
     * @returns {boolean}
     */
    isGameActive() {
        return this.isActive;
    }
    
    /**
     * Get the name of the current game
     * @returns {string|null}
     */
    getCurrentGame() {
        return this.currentGame;
    }
    
    /**
     * Get current performance metrics
     * @returns {Object} Performance metrics
     */
    getPerformanceMetrics() {
        return {
            fps: this.performanceMetrics.fps,
            inputLatency: this.performanceMetrics.inputLatency,
            targetFps: 30,
            targetLatency: 50
        };
    }
    
    /**
     * Create and display the game canvas
     * @returns {boolean} - True if canvas created successfully
     */
    createCanvas() {
        try {
            // Get chat display container
            const chatContainer = document.getElementById('chatDisplay');
            if (!chatContainer) {
                console.error('Chat display container not found');
                this.showErrorMessage('Failed to initialize game: chat container not found');
                return false;
            }
            
            // Hide chat display
            try {
                chatContainer.style.display = 'none';
            } catch (error) {
                console.error('Error hiding chat display:', error);
                // Continue anyway
            }
            
            // Hide command bar (we'll still listen for /exit_game)
            const commandBarElement = document.querySelector('.command-bar');
            if (commandBarElement) {
                try {
                    commandBarElement.style.display = 'none';
                } catch (error) {
                    console.error('Error hiding command bar:', error);
                    // Continue anyway
                }
            }
            
            // Create canvas element
            try {
                this.canvas = document.createElement('canvas');
                if (!this.canvas) {
                    throw new Error('Failed to create canvas element');
                }
                
                this.canvas.id = 'gameCanvas';
                this.canvas.style.display = 'block';
                this.canvas.style.backgroundColor = this.canvasConfig.backgroundColor;
                this.canvas.style.cursor = 'default';
                this.canvas.style.position = 'absolute';
                this.canvas.style.top = '0';
                this.canvas.style.left = '0';
                this.canvas.style.zIndex = '10';
            } catch (error) {
                console.error('Error creating canvas element:', error);
                this.showErrorMessage('Failed to create game canvas');
                this.restoreChatDisplay();
                return false;
            }
            
            // Set canvas dimensions to match chat area
            try {
                const mainContent = document.querySelector('.main-content');
                if (mainContent) {
                    this.canvas.width = mainContent.clientWidth || 800;
                    this.canvas.height = (mainContent.clientHeight || 600) - 65; // Subtract command bar height
                } else {
                    // Fallback dimensions
                    this.canvas.width = 800;
                    this.canvas.height = 600;
                }
                
                // Validate dimensions
                if (this.canvas.width <= 0 || this.canvas.height <= 0) {
                    throw new Error('Invalid canvas dimensions');
                }
            } catch (error) {
                console.error('Error setting canvas dimensions:', error);
                this.canvas.width = 800;
                this.canvas.height = 600;
            }
            
            // Add canvas to main content area
            try {
                const mainContent = document.querySelector('.main-content');
                if (mainContent) {
                    mainContent.appendChild(this.canvas);
                } else {
                    document.body.appendChild(this.canvas);
                }
            } catch (error) {
                console.error('Error appending canvas to DOM:', error);
                this.showErrorMessage('Failed to display game canvas');
                this.canvas = null;
                this.restoreChatDisplay();
                return false;
            }
            
            // Verify canvas context is available
            try {
                const ctx = this.canvas.getContext('2d');
                if (!ctx) {
                    throw new Error('Failed to get 2D context from canvas');
                }
            } catch (error) {
                console.error('Error getting canvas context:', error);
                this.showErrorMessage('Failed to initialize game graphics');
                this.removeCanvas();
                return false;
            }
            
            // Set up canvas click handler for exit icon ONLY (Requirement 10.1)
            // Mouse/touch input is disabled for game controls
            try {
                this.canvas.addEventListener('click', this.handleCanvasClick.bind(this));
                
                // Disable mouse/touch input for game controls (Requirement 10.1)
                if (this.mouseInputDisabled) {
                    this.canvas.addEventListener('mousedown', this.preventMouseInput.bind(this));
                    this.canvas.addEventListener('mousemove', this.preventMouseInput.bind(this));
                }
                
                if (this.touchInputDisabled) {
                    this.canvas.addEventListener('touchstart', this.preventTouchInput.bind(this), { passive: false });
                    this.canvas.addEventListener('touchmove', this.preventTouchInput.bind(this), { passive: false });
                }
            } catch (error) {
                console.error('Error setting up canvas event listeners:', error);
                // Continue anyway - game will still work without these
            }
            
            return true;
        } catch (error) {
            console.error('Unexpected error creating canvas:', error);
            this.showErrorMessage('An unexpected error occurred while initializing the game');
            this.restoreChatDisplay();
            return false;
        }
    }
    
    /**
     * Restore chat display (helper for error recovery)
     */
    restoreChatDisplay() {
        try {
            const chatContainer = document.getElementById('chatDisplay');
            if (chatContainer) {
                chatContainer.style.display = 'block';
            }
            
            const commandBarElement = document.querySelector('.command-bar');
            if (commandBarElement) {
                commandBarElement.style.display = 'flex';
            }
        } catch (error) {
            console.error('Error restoring chat display:', error);
        }
    }
    
    /**
     * Show error message to user
     * @param {string} message - Error message to display
     */
    showErrorMessage(message) {
        try {
            // Try to display error in chat if possible
            if (this.chatDisplay && typeof this.chatDisplay.addSystemMessage === 'function') {
                this.chatDisplay.addSystemMessage(message);
            } else {
                // Fallback to console
                console.error(message);
            }
        } catch (error) {
            console.error('Error showing error message:', error);
        }
    }
    
    /**
     * Remove the game canvas and restore chat display
     */
    removeCanvas() {
        try {
            // Remove canvas from DOM
            if (this.canvas) {
                try {
                    // Remove event listeners to prevent memory leaks
                    if (this.canvas.parentNode) {
                        this.canvas.removeEventListener('click', this.handleCanvasClick);
                        this.canvas.removeEventListener('mousedown', this.preventMouseInput);
                        this.canvas.removeEventListener('mousemove', this.preventMouseInput);
                        this.canvas.removeEventListener('touchstart', this.preventTouchInput);
                        this.canvas.removeEventListener('touchmove', this.preventTouchInput);
                        
                        this.canvas.parentNode.removeChild(this.canvas);
                    }
                } catch (error) {
                    console.error('Error removing canvas from DOM:', error);
                }
                this.canvas = null;
            }
            
            // Restore chat display
            try {
                const chatContainer = document.getElementById('chatDisplay');
                if (chatContainer) {
                    chatContainer.style.display = 'block';
                }
            } catch (error) {
                console.error('Error restoring chat display:', error);
            }
            
            // Restore command bar
            try {
                const commandBarElement = document.querySelector('.command-bar');
                if (commandBarElement) {
                    commandBarElement.style.display = 'flex';
                }
            } catch (error) {
                console.error('Error restoring command bar:', error);
            }
        } catch (error) {
            console.error('Unexpected error removing canvas:', error);
            // Force cleanup
            this.canvas = null;
            this.restoreChatDisplay();
        }
    }
    
    /**
     * Handle room change - terminate game if user leaves Arcade Room
     * @param {string} newRoom - Name of the new room
     */
    handleRoomChange(newRoom) {
        try {
            // Terminate game if user leaves Arcade Room (or Arcade Hall)
            if (this.isActive && newRoom !== 'Arcade Hall' && newRoom !== 'Arcade Room') {
                this.exitGame();
            }
        } catch (error) {
            console.error('Error handling room change:', error);
            // Force cleanup to prevent game from running in background
            try {
                this.stopGameLoop();
                this.removeCanvas();
                this.isActive = false;
            } catch (cleanupError) {
                console.error('Error during forced cleanup:', cleanupError);
            }
        }
    }
    
    /**
     * Handle canvas click (for exit icon)
     * @param {MouseEvent} event - Click event
     */
    handleCanvasClick(event) {
        if (!this.canvas) return;
        
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // Check if click is within exit icon bounds (top-right corner)
        const iconX = this.canvas.width - this.exitIconSize - this.exitIconPadding;
        const iconY = this.exitIconPadding;
        
        if (x >= iconX && x <= iconX + this.exitIconSize &&
            y >= iconY && y <= iconY + this.exitIconSize) {
            this.exitGame();
        }
    }
    
    /**
     * Prevent mouse input for game controls (Requirement 10.1)
     * Mouse is only allowed for exit icon
     * @param {MouseEvent} event - Mouse event
     */
    preventMouseInput(event) {
        // Allow click events for exit icon, but prevent other mouse interactions
        if (event.type !== 'click') {
            event.preventDefault();
            event.stopPropagation();
        }
    }
    
    /**
     * Prevent touch input for game controls (Requirement 10.1)
     * Touch is only allowed for exit icon tap
     * @param {TouchEvent} event - Touch event
     */
    preventTouchInput(event) {
        // Prevent all touch interactions except taps on exit icon
        // The click event will handle exit icon taps
        event.preventDefault();
        event.stopPropagation();
    }
    
    /**
     * Render exit icon in top-right corner
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     */
    renderExitIcon(ctx) {
        const x = this.canvas.width - this.exitIconSize - this.exitIconPadding;
        const y = this.exitIconPadding;
        const size = this.exitIconSize;
        
        // Draw white X
        ctx.strokeStyle = this.canvasConfig.foregroundColor;
        ctx.lineWidth = 3;
        ctx.lineCap = 'round';
        
        // Draw X lines
        ctx.beginPath();
        ctx.moveTo(x + 5, y + 5);
        ctx.lineTo(x + size - 5, y + size - 5);
        ctx.moveTo(x + size - 5, y + 5);
        ctx.lineTo(x + 5, y + size - 5);
        ctx.stroke();
        
        // Draw border
        ctx.strokeStyle = this.canvasConfig.foregroundColor;
        ctx.lineWidth = 2;
        ctx.strokeRect(x, y, size, size);
    }
    
    /**
     * Handle keyboard key down
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeyDown(event) {
        if (!this.isActive || !this.gameInstance) return;
        
        // Prevent default behavior for arrow keys and space
        if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' '].includes(event.key)) {
            event.preventDefault();
        }
        
        // Input debouncing (Requirement 10.3)
        const currentTime = performance.now();
        const lastTime = this.inputDebounce.lastKeyTime[event.key] || 0;
        
        if (currentTime - lastTime < this.inputDebounce.debounceDelay) {
            // Too soon, skip this input
            return;
        }
        
        // Update last input time
        this.inputDebounce.lastKeyTime[event.key] = currentTime;
        
        // Measure input latency (Requirement 10.4)
        this.performanceMetrics.lastInputTime = currentTime;
        
        // Route to game instance
        try {
            const startTime = performance.now();
            this.gameInstance.handleKeyDown(event.key);
            const endTime = performance.now();
            
            // Track input latency
            this.performanceMetrics.inputLatency = endTime - startTime;
            
            // Warn if latency exceeds 50ms
            if (this.performanceMetrics.inputLatency > 50) {
                console.warn(`High input latency detected: ${this.performanceMetrics.inputLatency.toFixed(2)}ms`);
            }
        } catch (error) {
            console.error('Error handling key down:', error);
        }
    }
    
    /**
     * Handle keyboard key up
     * @param {KeyboardEvent} event - Keyboard event
     */
    handleKeyUp(event) {
        if (!this.isActive || !this.gameInstance) return;
        
        // Route to game instance
        try {
            this.gameInstance.handleKeyUp(event.key);
        } catch (error) {
            console.error('Error handling key up:', error);
        }
    }
    
    /**
     * Start the game loop
     */
    startGameLoop() {
        this.lastFrameTime = performance.now();
        this.gameLoop();
    }
    
    /**
     * Stop the game loop
     */
    stopGameLoop() {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }
    
    /**
     * Main game loop
     */
    gameLoop() {
        if (!this.isActive || !this.gameInstance || !this.canvas) {
            return;
        }
        
        try {
            // Calculate delta time
            const currentTime = performance.now();
            const deltaTime = currentTime - this.lastFrameTime;
            this.lastFrameTime = currentTime;
            
            // FPS tracking (Requirement 10.2)
            this.performanceMetrics.frameCount++;
            if (currentTime - this.performanceMetrics.lastFpsUpdate >= 1000) {
                this.performanceMetrics.fps = this.performanceMetrics.frameCount;
                this.performanceMetrics.frameCount = 0;
                this.performanceMetrics.lastFpsUpdate = currentTime;
                
                // Warn if FPS drops below 30
                if (this.performanceMetrics.fps < 30) {
                    console.warn(`Low FPS detected: ${this.performanceMetrics.fps} FPS`);
                }
            }
            
            // Verify canvas context is still available
            const ctx = this.canvas.getContext('2d');
            if (!ctx) {
                throw new Error('Canvas context lost');
            }
            
            try {
                // Update game state
                this.gameInstance.update(deltaTime);
            } catch (error) {
                console.error('Error updating game state:', error);
                throw error; // Re-throw to trigger game exit
            }
            
            try {
                // Clear canvas
                ctx.fillStyle = this.canvasConfig.backgroundColor;
                ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                
                // Render game
                this.gameInstance.render();
                
                // Render exit icon on top
                this.renderExitIcon(ctx);
            } catch (error) {
                console.error('Error rendering game:', error);
                throw error; // Re-throw to trigger game exit
            }
            
            // Check if game is over
            try {
                if (this.gameInstance.isGameOver()) {
                    this.handleGameOver();
                    return;
                }
            } catch (error) {
                console.error('Error checking game over state:', error);
                // Assume game is over to be safe
                this.handleGameOver();
                return;
            }
            
            // Continue loop
            this.animationFrameId = requestAnimationFrame(() => this.gameLoop());
        } catch (error) {
            console.error('Critical error in game loop:', error);
            this.showErrorMessage('Game encountered an error and will exit');
            this.exitGame();
        }
    }
    
    /**
     * Handle game over state
     */
    handleGameOver() {
        try {
            // Display game over message on canvas
            if (this.canvas && this.gameInstance) {
                try {
                    const ctx = this.canvas.getContext('2d');
                    if (!ctx) {
                        throw new Error('Canvas context not available');
                    }
                    
                    const finalScore = this.gameInstance.getScore();
                    const highScore = HighScoreManager.getHighScore(this.currentGame);
                    const isNewHigh = finalScore > highScore;
                    
                    // Clear canvas
                    ctx.fillStyle = this.canvasConfig.backgroundColor;
                    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                    
                    // Display game over text
                    ctx.fillStyle = this.canvasConfig.foregroundColor;
                    ctx.font = `48px ${this.canvasConfig.font}`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    
                    const centerX = this.canvas.width / 2;
                    const centerY = this.canvas.height / 2;
                    
                    ctx.fillText('GAME OVER', centerX, centerY - 60);
                    
                    ctx.font = `24px ${this.canvasConfig.font}`;
                    ctx.fillText(`Score: ${finalScore}`, centerX, centerY);
                    
                    if (isNewHigh) {
                        ctx.fillText('NEW HIGH SCORE!', centerX, centerY + 40);
                    } else {
                        ctx.fillText(`High Score: ${highScore}`, centerX, centerY + 40);
                    }
                    
                    ctx.font = `18px ${this.canvasConfig.font}`;
                    ctx.fillText('Click X to exit', centerX, centerY + 100);
                    
                    // Render exit icon
                    this.renderExitIcon(ctx);
                    
                    // Update high score
                    if (isNewHigh) {
                        HighScoreManager.setHighScore(this.currentGame, finalScore);
                    }
                } catch (error) {
                    console.error('Error rendering game over screen:', error);
                    // Fall back to just exiting the game
                    this.exitGame();
                    return;
                }
            }
            
            // Stop the game loop but keep canvas visible
            this.stopGameLoop();
        } catch (error) {
            console.error('Error handling game over:', error);
            // Force exit to ensure clean state
            this.exitGame();
        }
    }
}
