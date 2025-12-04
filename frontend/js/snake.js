/**
 * Snake Game
 * Classic grid-based snake game with food collection
 * Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
 */

import { Game } from './game.js';
import { HighScoreManager } from './highScores.js';

export class SnakeGame extends Game {
    /**
     * @param {HTMLCanvasElement} canvas - The game canvas
     * @param {CanvasRenderingContext2D} context - The canvas 2D context
     */
    constructor(canvas, context) {
        super(canvas, context);
        
        // Grid configuration
        this.gridSize = 20; // Size of each grid cell in pixels
        this.gridWidth = Math.floor(canvas.width / this.gridSize);
        this.gridHeight = Math.floor(canvas.height / this.gridSize);
        
        // Snake state
        this.snake = [];
        this.direction = { x: 1, y: 0 }; // Start moving right
        this.nextDirection = { x: 1, y: 0 }; // Buffer for next direction
        
        // Food state
        this.food = { x: 0, y: 0 };
        
        // Game timing
        this.moveInterval = 150; // Move every 150ms
        this.timeSinceLastMove = 0;
        
        // Colors (monochrome)
        this.backgroundColor = '#000000';
        this.foregroundColor = '#FFFFFF';
    }
    
    /**
     * Initialize game state
     */
    init() {
        // Reset game state
        this.gameOver = false;
        this.score = 0;
        this.timeSinceLastMove = 0;
        
        // Initialize snake in the center, length 3
        const centerX = Math.floor(this.gridWidth / 2);
        const centerY = Math.floor(this.gridHeight / 2);
        
        this.snake = [
            { x: centerX, y: centerY },
            { x: centerX - 1, y: centerY },
            { x: centerX - 2, y: centerY }
        ];
        
        // Start moving right
        this.direction = { x: 1, y: 0 };
        this.nextDirection = { x: 1, y: 0 };
        
        // Spawn initial food
        this.spawnFood();
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
     * Update game state
     * @param {number} deltaTime - Time elapsed since last update (ms)
     */
    update(deltaTime) {
        if (this.gameOver) {
            return;
        }
        
        // Accumulate time
        this.timeSinceLastMove += deltaTime;
        
        // Move snake at fixed intervals
        if (this.timeSinceLastMove >= this.moveInterval) {
            this.timeSinceLastMove = 0;
            
            // Update direction from buffer
            this.direction = { ...this.nextDirection };
            
            // Calculate new head position
            const head = this.snake[0];
            const newHead = {
                x: head.x + this.direction.x,
                y: head.y + this.direction.y
            };
            
            // Check wall collision (Requirement 6.4)
            if (newHead.x < 0 || newHead.x >= this.gridWidth ||
                newHead.y < 0 || newHead.y >= this.gridHeight) {
                this.gameOver = true;
                return;
            }
            
            // Check self-collision (Requirement 6.5)
            for (let segment of this.snake) {
                if (segment.x === newHead.x && segment.y === newHead.y) {
                    this.gameOver = true;
                    return;
                }
            }
            
            // Add new head
            this.snake.unshift(newHead);
            
            // Check food collision (Requirement 6.3)
            if (newHead.x === this.food.x && newHead.y === this.food.y) {
                // Snake grows (don't remove tail)
                this.score += 10;
                this.spawnFood();
            } else {
                // Remove tail (snake doesn't grow)
                this.snake.pop();
            }
        }
    }
    
    /**
     * Render game graphics
     */
    render() {
        const ctx = this.context;
        
        // Clear canvas with black background
        ctx.fillStyle = this.backgroundColor;
        ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw grid (subtle)
        ctx.strokeStyle = '#222222';
        ctx.lineWidth = 1;
        for (let x = 0; x <= this.gridWidth; x++) {
            ctx.beginPath();
            ctx.moveTo(x * this.gridSize, 0);
            ctx.lineTo(x * this.gridSize, this.canvas.height);
            ctx.stroke();
        }
        for (let y = 0; y <= this.gridHeight; y++) {
            ctx.beginPath();
            ctx.moveTo(0, y * this.gridSize);
            ctx.lineTo(this.canvas.width, y * this.gridSize);
            ctx.stroke();
        }
        
        // Draw food (white square)
        ctx.fillStyle = this.foregroundColor;
        ctx.fillRect(
            this.food.x * this.gridSize + 1,
            this.food.y * this.gridSize + 1,
            this.gridSize - 2,
            this.gridSize - 2
        );
        
        // Draw snake (white squares)
        ctx.fillStyle = this.foregroundColor;
        for (let segment of this.snake) {
            ctx.fillRect(
                segment.x * this.gridSize + 1,
                segment.y * this.gridSize + 1,
                this.gridSize - 2,
                this.gridSize - 2
            );
        }
        
        // Draw score
        ctx.fillStyle = this.foregroundColor;
        ctx.font = '20px VT323, Courier New, monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        ctx.fillText(`Score: ${this.score}`, 10, 10);
        
        // Draw high score
        const highScore = HighScoreManager.getHighScore('snake');
        ctx.fillText(`High: ${highScore}`, 10, 35);
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
        
        ctx.fillText('SNAKE', centerX, centerY - 80);
        
        ctx.font = '24px VT323, Courier New, monospace';
        ctx.fillText('Use Arrow Keys to Move', centerX, centerY - 20);
        ctx.fillText('Eat Food to Grow', centerX, centerY + 10);
        ctx.fillText('Avoid Walls and Yourself', centerX, centerY + 40);
        
        // Display high score
        const highScore = HighScoreManager.getHighScore('snake');
        ctx.font = '20px VT323, Courier New, monospace';
        ctx.fillText(`High Score: ${highScore}`, centerX, centerY + 80);
        
        ctx.font = '18px VT323, Courier New, monospace';
        ctx.fillText('Press Any Arrow Key to Start', centerX, centerY + 120);
    }
    
    /**
     * Spawn food at a random empty location
     */
    spawnFood() {
        let validPosition = false;
        let newFood = { x: 0, y: 0 };
        
        // Keep trying until we find a position not occupied by snake
        while (!validPosition) {
            newFood.x = Math.floor(Math.random() * this.gridWidth);
            newFood.y = Math.floor(Math.random() * this.gridHeight);
            
            // Check if position is occupied by snake
            validPosition = true;
            for (let segment of this.snake) {
                if (segment.x === newFood.x && segment.y === newFood.y) {
                    validPosition = false;
                    break;
                }
            }
        }
        
        this.food = newFood;
    }
    
    /**
     * Handle key down events (Requirement 6.2)
     * @param {string} key - The key that was pressed
     */
    handleKeyDown(key) {
        // Arrow keys control direction
        // Prevent 180-degree turns
        switch (key) {
            case 'ArrowUp':
                if (this.direction.y === 0) {
                    this.nextDirection = { x: 0, y: -1 };
                }
                break;
            case 'ArrowDown':
                if (this.direction.y === 0) {
                    this.nextDirection = { x: 0, y: 1 };
                }
                break;
            case 'ArrowLeft':
                if (this.direction.x === 0) {
                    this.nextDirection = { x: -1, y: 0 };
                }
                break;
            case 'ArrowRight':
                if (this.direction.x === 0) {
                    this.nextDirection = { x: 1, y: 0 };
                }
                break;
        }
    }
    
    /**
     * Handle key up events
     * @param {string} key - The key that was released
     */
    handleKeyUp(key) {
        // No action needed for key up in Snake
    }
    
    /**
     * Get game name
     * @returns {string}
     */
    getGameName() {
        return 'snake';
    }
}
