/**
 * Breakout Game
 * Classic brick-breaking game with paddle and ball
 * Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
 * 
 * SILENT DESIGN REQUIREMENT (Requirements 11.1, 11.2, 11.3, 11.4, 11.5):
 * This game is intentionally designed to be completely silent without any audio.
 * - No audio elements are created
 * - No audio files are loaded or referenced
 * - No sound playback occurs during gameplay or events
 * - All feedback is provided through visual means only
 * This maintains the quiet retro-terminal atmosphere of the BBS.
 */

import { Game } from './game.js';
import { HighScoreManager } from './highScores.js';

export class BreakoutGame extends Game {
    /**
     * @param {HTMLCanvasElement} canvas - The game canvas
     * @param {CanvasRenderingContext2D} context - The canvas 2D context
     */
    constructor(canvas, context) {
        super(canvas, context);
        
        // Paddle configuration
        this.paddleWidth = 100;
        this.paddleHeight = 15;
        this.paddleSpeed = 8;
        this.paddle = {
            x: 0,
            y: 0,
            width: this.paddleWidth,
            height: this.paddleHeight,
            dx: 0 // Velocity
        };
        
        // Ball configuration
        this.ballRadius = 6;
        this.ballSpeed = 4;
        this.ball = {
            x: 0,
            y: 0,
            dx: 0,
            dy: 0,
            radius: this.ballRadius
        };
        
        // Brick configuration
        this.brickRows = 5;
        this.brickCols = 10;
        this.brickWidth = 0;
        this.brickHeight = 20;
        this.brickPadding = 5;
        this.brickOffsetTop = 60;
        this.brickOffsetLeft = 0;
        this.bricks = [];
        
        // Calculate brick dimensions based on canvas
        this.calculateBrickDimensions();
        
        // Game state
        this.levelComplete = false;
        this.ballLaunched = false;
        
        // Input state
        this.keys = {
            left: false,
            right: false
        };
        
        // Colors (monochrome)
        this.backgroundColor = '#000000';
        this.foregroundColor = '#FFFFFF';
    }
    
    /**
     * Calculate brick dimensions based on canvas size
     */
    calculateBrickDimensions() {
        const totalPadding = (this.brickCols + 1) * this.brickPadding;
        const availableWidth = this.canvas.width - totalPadding;
        this.brickWidth = Math.floor(availableWidth / this.brickCols);
        this.brickOffsetLeft = this.brickPadding;
    }
    
    /**
     * Initialize game state
     */
    init() {
        // Reset game state
        this.gameOver = false;
        this.levelComplete = false;
        this.score = 0;
        this.ballLaunched = false;
        
        // Initialize paddle (Requirement 8.1)
        this.paddle.x = (this.canvas.width - this.paddleWidth) / 2;
        this.paddle.y = this.canvas.height - this.paddleHeight - 30;
        this.paddle.dx = 0;
        
        // Initialize ball (Requirement 8.1)
        this.ball.x = this.canvas.width / 2;
        this.ball.y = this.paddle.y - this.ballRadius - 1;
        this.ball.dx = 0;
        this.ball.dy = 0;
        
        // Initialize bricks (Requirement 8.1)
        this.initBricks();
        
        // Reset input state
        this.keys.left = false;
        this.keys.right = false;
    }
    
    /**
     * Initialize brick grid
     */
    initBricks() {
        this.bricks = [];
        
        for (let row = 0; row < this.brickRows; row++) {
            this.bricks[row] = [];
            for (let col = 0; col < this.brickCols; col++) {
                const brickX = this.brickOffsetLeft + col * (this.brickWidth + this.brickPadding);
                const brickY = this.brickOffsetTop + row * (this.brickHeight + this.brickPadding);
                
                this.bricks[row][col] = {
                    x: brickX,
                    y: brickY,
                    width: this.brickWidth,
                    height: this.brickHeight,
                    alive: true
                };
            }
        }
    }
    
    /**
     * Start the game
     */
    start() {
        // Display start screen with high score
        this.renderStartScreen();
    }
    
    /**
     * Stop the game
     */
    stop() {
        // Nothing special to clean up
    }
    
    /**
     * Reset game to initial state
     */
    reset() {
        this.init();
    }
    
    /**
     * Launch the ball
     */
    launchBall() {
        if (!this.ballLaunched) {
            this.ballLaunched = true;
            // Launch at a random angle upward
            const angle = (Math.random() * 60 + 60) * Math.PI / 180; // 60-120 degrees
            this.ball.dx = this.ballSpeed * Math.cos(angle);
            this.ball.dy = -this.ballSpeed * Math.sin(angle);
        }
    }
    
    /**
     * Update game state
     * @param {number} deltaTime - Time elapsed since last update (ms)
     */
    update(deltaTime) {
        if (this.gameOver || this.levelComplete) {
            return;
        }
        
        // Update paddle position (Requirement 8.2)
        if (this.keys.left) {
            this.paddle.x -= this.paddleSpeed;
        }
        if (this.keys.right) {
            this.paddle.x += this.paddleSpeed;
        }
        
        // Keep paddle within bounds
        if (this.paddle.x < 0) {
            this.paddle.x = 0;
        }
        if (this.paddle.x + this.paddle.width > this.canvas.width) {
            this.paddle.x = this.canvas.width - this.paddle.width;
        }
        
        // If ball not launched, keep it on paddle
        if (!this.ballLaunched) {
            this.ball.x = this.paddle.x + this.paddle.width / 2;
            this.ball.y = this.paddle.y - this.ballRadius - 1;
            return;
        }
        
        // Update ball position
        this.ball.x += this.ball.dx;
        this.ball.y += this.ball.dy;
        
        // Ball collision with walls
        if (this.ball.x - this.ballRadius < 0) {
            this.ball.x = this.ballRadius;
            this.ball.dx = -this.ball.dx;
        }
        if (this.ball.x + this.ballRadius > this.canvas.width) {
            this.ball.x = this.canvas.width - this.ballRadius;
            this.ball.dx = -this.ball.dx;
        }
        if (this.ball.y - this.ballRadius < 0) {
            this.ball.y = this.ballRadius;
            this.ball.dy = -this.ball.dy;
        }
        
        // Ball collision with paddle (Requirement 8.4)
        if (this.checkPaddleCollision()) {
            // Bounce ball upward
            this.ball.dy = -Math.abs(this.ball.dy);
            
            // Modify angle based on where ball hit paddle
            const hitPos = (this.ball.x - this.paddle.x) / this.paddle.width; // 0 to 1
            const angle = (hitPos - 0.5) * 120; // -60 to +60 degrees
            const speed = Math.sqrt(this.ball.dx * this.ball.dx + this.ball.dy * this.ball.dy);
            
            this.ball.dx = speed * Math.sin(angle * Math.PI / 180);
            this.ball.dy = -speed * Math.cos(angle * Math.PI / 180);
            
            // Ensure ball moves upward
            if (this.ball.dy > 0) {
                this.ball.dy = -this.ball.dy;
            }
            
            // Move ball above paddle to prevent multiple collisions
            this.ball.y = this.paddle.y - this.ballRadius - 1;
        }
        
        // Ball miss detection (Requirement 8.5)
        if (this.ball.y - this.ballRadius > this.canvas.height) {
            this.gameOver = true;
            return;
        }
        
        // Ball collision with bricks (Requirement 8.3)
        this.checkBrickCollisions();
        
        // Check level completion (Requirement 8.6)
        if (this.checkLevelComplete()) {
            this.levelComplete = true;
        }
    }
    
    /**
     * Check collision between ball and paddle
     * @returns {boolean} True if collision detected
     */
    checkPaddleCollision() {
        return this.ball.x + this.ballRadius > this.paddle.x &&
               this.ball.x - this.ballRadius < this.paddle.x + this.paddle.width &&
               this.ball.y + this.ballRadius > this.paddle.y &&
               this.ball.y - this.ballRadius < this.paddle.y + this.paddle.height &&
               this.ball.dy > 0; // Only collide when ball is moving down
    }
    
    /**
     * Check collision between ball and bricks
     */
    checkBrickCollisions() {
        for (let row = 0; row < this.brickRows; row++) {
            for (let col = 0; col < this.brickCols; col++) {
                const brick = this.bricks[row][col];
                
                if (!brick.alive) {
                    continue;
                }
                
                // Check if ball intersects brick
                if (this.ball.x + this.ballRadius > brick.x &&
                    this.ball.x - this.ballRadius < brick.x + brick.width &&
                    this.ball.y + this.ballRadius > brick.y &&
                    this.ball.y - this.ballRadius < brick.y + brick.height) {
                    
                    // Destroy brick (Requirement 8.3)
                    brick.alive = false;
                    this.score += 10;
                    
                    // Determine bounce direction based on collision side
                    const ballCenterX = this.ball.x;
                    const ballCenterY = this.ball.y;
                    const brickCenterX = brick.x + brick.width / 2;
                    const brickCenterY = brick.y + brick.height / 2;
                    
                    const dx = ballCenterX - brickCenterX;
                    const dy = ballCenterY - brickCenterY;
                    
                    // Determine which side was hit
                    if (Math.abs(dx / brick.width) > Math.abs(dy / brick.height)) {
                        // Hit left or right side
                        this.ball.dx = -this.ball.dx;
                    } else {
                        // Hit top or bottom
                        this.ball.dy = -this.ball.dy;
                    }
                    
                    // Only process one brick collision per frame
                    return;
                }
            }
        }
    }
    
    /**
     * Check if all bricks are destroyed
     * @returns {boolean} True if level is complete
     */
    checkLevelComplete() {
        for (let row = 0; row < this.brickRows; row++) {
            for (let col = 0; col < this.brickCols; col++) {
                if (this.bricks[row][col].alive) {
                    return false;
                }
            }
        }
        return true;
    }
    
    /**
     * Render game graphics
     */
    render() {
        const ctx = this.context;
        
        // Clear canvas with black background
        ctx.fillStyle = this.backgroundColor;
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw paddle (Requirement 8.7 - monochrome)
        ctx.fillStyle = this.foregroundColor;
        ctx.fillRect(this.paddle.x, this.paddle.y, this.paddle.width, this.paddle.height);
        
        // Draw ball (Requirement 8.7 - monochrome)
        ctx.fillStyle = this.foregroundColor;
        ctx.beginPath();
        ctx.arc(this.ball.x, this.ball.y, this.ball.radius, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw bricks (Requirement 8.7 - monochrome)
        ctx.fillStyle = this.foregroundColor;
        for (let row = 0; row < this.brickRows; row++) {
            for (let col = 0; col < this.brickCols; col++) {
                const brick = this.bricks[row][col];
                if (brick.alive) {
                    ctx.fillRect(brick.x, brick.y, brick.width, brick.height);
                }
            }
        }
        
        // Draw score
        ctx.fillStyle = this.foregroundColor;
        ctx.font = '20px VT323, Courier New, monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        ctx.fillText(`Score: ${this.score}`, 10, 10);
        
        // Draw high score
        const highScore = HighScoreManager.getHighScore('breakout');
        ctx.fillText(`High: ${highScore}`, 10, 35);
        
        // Draw launch instruction if ball not launched
        if (!this.ballLaunched) {
            ctx.font = '18px VT323, Courier New, monospace';
            ctx.textAlign = 'center';
            ctx.fillText('Press SPACE to Launch', this.canvas.width / 2, this.canvas.height - 60);
        }
        
        // Draw victory message if level complete
        if (this.levelComplete) {
            ctx.fillStyle = this.foregroundColor;
            ctx.font = '48px VT323, Courier New, monospace';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('VICTORY!', this.canvas.width / 2, this.canvas.height / 2);
            
            ctx.font = '24px VT323, Courier New, monospace';
            ctx.fillText(`Final Score: ${this.score}`, this.canvas.width / 2, this.canvas.height / 2 + 50);
        }
    }
    
    /**
     * Render start screen
     */
    renderStartScreen() {
        const ctx = this.context;
        
        // Clear canvas
        ctx.fillStyle = this.backgroundColor;
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Display title and instructions
        ctx.fillStyle = this.foregroundColor;
        ctx.font = '48px VT323, Courier New, monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        
        ctx.fillText('BREAKOUT', centerX, centerY - 100);
        
        ctx.font = '24px VT323, Courier New, monospace';
        ctx.fillText('Arrow Keys: Move Paddle', centerX, centerY - 30);
        ctx.fillText('Space: Launch Ball', centerX, centerY);
        ctx.fillText('Break All Bricks to Win', centerX, centerY + 30);
        
        // Display high score
        const highScore = HighScoreManager.getHighScore('breakout');
        ctx.font = '20px VT323, Courier New, monospace';
        ctx.fillText(`High Score: ${highScore}`, centerX, centerY + 80);
        
        ctx.font = '18px VT323, Courier New, monospace';
        ctx.fillText('Press Any Arrow Key to Start', centerX, centerY + 120);
    }
    
    /**
     * Handle key down events
     * @param {string} key - The key that was pressed
     */
    handleKeyDown(key) {
        if (this.gameOver || this.levelComplete) {
            return;
        }
        
        switch (key) {
            case 'ArrowLeft':
                this.keys.left = true; // Requirement 8.2
                break;
            case 'ArrowRight':
                this.keys.right = true; // Requirement 8.2
                break;
            case ' ':
            case 'Space':
                this.launchBall();
                break;
        }
    }
    
    /**
     * Handle key up events
     * @param {string} key - The key that was released
     */
    handleKeyUp(key) {
        switch (key) {
            case 'ArrowLeft':
                this.keys.left = false;
                break;
            case 'ArrowRight':
                this.keys.right = false;
                break;
        }
    }
    
    /**
     * Get game name
     * @returns {string}
     */
    getGameName() {
        return 'breakout';
    }
}
