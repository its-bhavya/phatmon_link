/**
 * Game Manager
 * Orchestrates game lifecycle, canvas management, and game state transitions
 * Requirements: 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.5
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
    }
    
    /**
     * Launch a game
     * @param {string} gameName - Name of the game to launch (snake, tetris, breakout)
     * @returns {boolean} - True if game launched successfully
     */
    launchGame(gameName) {
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
            this.gameInstance = this.createGameInstance(gameName);
            
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
    createGameInstance(gameName) {
        // This will be implemented when individual games are created
        // For now, return null to indicate games aren't implemented yet
        console.warn(`Game "${gameName}" not yet implemented`);
        return null;
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
            
            // Set up canvas click handler for exit icon
            this.canvas.addEventListener('click', this.handleCanvasClick.bind(this));
            
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
        
        // Route to game instance
        try {
            this.gameInstance.handleKeyDown(event.key);
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
