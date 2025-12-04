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
                return false;
            }
            
            // Hide chat display
            chatContainer.style.display = 'none';
            
            // Hide command bar (we'll still listen for /exit_game)
            const commandBarElement = document.querySelector('.command-bar');
            if (commandBarElement) {
                commandBarElement.style.display = 'none';
            }
            
            // Create canvas element
            this.canvas = document.createElement('canvas');
            this.canvas.id = 'gameCanvas';
            this.canvas.style.display = 'block';
            this.canvas.style.backgroundColor = this.canvasConfig.backgroundColor;
            this.canvas.style.cursor = 'default';
            this.canvas.style.position = 'absolute';
            this.canvas.style.top = '0';
            this.canvas.style.left = '0';
            this.canvas.style.zIndex = '10';
            
            // Set canvas dimensions to match chat area
            const mainContent = document.querySelector('.main-content');
            if (mainContent) {
                this.canvas.width = mainContent.clientWidth;
                this.canvas.height = mainContent.clientHeight - 65; // Subtract command bar height
            } else {
                // Fallback dimensions
                this.canvas.width = 800;
                this.canvas.height = 600;
            }
            
            // Add canvas to main content area
            if (mainContent) {
                mainContent.appendChild(this.canvas);
            } else {
                document.body.appendChild(this.canvas);
            }
            
            // Set up canvas click handler for exit icon ONLY (Requirement 10.1)
            // Mouse/touch input is disabled for game controls
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
            
            return true;
        } catch (error) {
            console.error('Error creating canvas:', error);
            return false;
        }
    }
    
    /**
     * Remove the game canvas and restore chat display
     */
    removeCanvas() {
        try {
            // Remove canvas from DOM
            if (this.canvas && this.canvas.parentNode) {
                this.canvas.parentNode.removeChild(this.canvas);
            }
            this.canvas = null;
            
            // Restore chat display
            const chatContainer = document.getElementById('chatDisplay');
            if (chatContainer) {
                chatContainer.style.display = 'block';
            }
            
            // Restore command bar
            const commandBarElement = document.querySelector('.command-bar');
            if (commandBarElement) {
                commandBarElement.style.display = 'flex';
            }
        } catch (error) {
            console.error('Error removing canvas:', error);
        }
    }
    
    /**
     * Handle room change - terminate game if user leaves Arcade Room
     * @param {string} newRoom - Name of the new room
     */
    handleRoomChange(newRoom) {
        // Terminate game if user leaves Arcade Room (or Arcade Hall)
        if (this.isActive && newRoom !== 'Arcade Hall' && newRoom !== 'Arcade Room') {
            this.exitGame();
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
        
        try {
            // Update game state
            this.gameInstance.update(deltaTime);
            
            // Clear canvas
            const ctx = this.canvas.getContext('2d');
            ctx.fillStyle = this.canvasConfig.backgroundColor;
            ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            
            // Render game
            this.gameInstance.render();
            
            // Render exit icon on top
            this.renderExitIcon(ctx);
            
            // Check if game is over
            if (this.gameInstance.isGameOver()) {
                this.handleGameOver();
                return;
            }
            
            // Continue loop
            this.animationFrameId = requestAnimationFrame(() => this.gameLoop());
        } catch (error) {
            console.error('Error in game loop:', error);
            this.exitGame();
        }
    }
    
    /**
     * Handle game over state
     */
    handleGameOver() {
        // Display game over message on canvas
        if (this.canvas && this.gameInstance) {
            const ctx = this.canvas.getContext('2d');
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
        }
        
        // Stop the game loop but keep canvas visible
        this.stopGameLoop();
    }
}
