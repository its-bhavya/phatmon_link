/**
 * Tetris Game
 * Classic falling block puzzle game with line clearing
 * Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7
 */

import { Game } from './game.js';
import { HighScoreManager } from './highScores.js';

export class TetrisGame extends Game {
    /**
     * @param {HTMLCanvasElement} canvas - The game canvas
     * @param {CanvasRenderingContext2D} context - The canvas 2D context
     */
    constructor(canvas, context) {
        super(canvas, context);
        
        // Board configuration
        this.boardWidth = 10;  // 10 columns
        this.boardHeight = 20; // 20 rows
        this.blockSize = Math.min(
            Math.floor(canvas.width / (this.boardWidth + 4)),
            Math.floor(canvas.height / (this.boardHeight + 4))
        );
        
        // Calculate board offset to center it
        this.boardOffsetX = Math.floor((canvas.width - this.boardWidth * this.blockSize) / 2);
        this.boardOffsetY = Math.floor((canvas.height - this.boardHeight * this.blockSize) / 2);
        
        // Game board (2D array)
        this.board = [];
        
        // Current piece state
        this.currentPiece = null;
        this.currentPosition = { x: 0, y: 0 };
        this.currentRotation = 0;
        
        // Next piece
        this.nextPiece = null;
        
        // Game timing
        this.dropInterval = 1000; // Start at 1 second
        this.timeSinceLastDrop = 0;
        this.fastDrop = false; // Soft drop flag
        
        // Scoring
        this.linesCleared = 0;
        this.level = 1;
        
        // Colors (monochrome)
        this.backgroundColor = '#000000';
        this.foregroundColor = '#FFFFFF';
        
        // Define tetromino shapes (I, O, T, S, Z, J, L)
        this.tetrominoes = this.defineTetrominoes();
    }
    
    /**
     * Define the seven tetromino shapes with their rotations
     * Each shape is defined as a 2D array for each rotation state
     */
    defineTetrominoes() {
        return {
            'I': {
                shape: [
                    [[0,0,0,0],
                     [1,1,1,1],
                     [0,0,0,0],
                     [0,0,0,0]],
                    
                    [[0,0,1,0],
                     [0,0,1,0],
                     [0,0,1,0],
                     [0,0,1,0]],
                    
                    [[0,0,0,0],
                     [0,0,0,0],
                     [1,1,1,1],
                     [0,0,0,0]],
                    
                    [[0,1,0,0],
                     [0,1,0,0],
                     [0,1,0,0],
                     [0,1,0,0]]
                ]
            },
            'O': {
                shape: [
                    [[1,1],
                     [1,1]],
                    
                    [[1,1],
                     [1,1]],
                    
                    [[1,1],
                     [1,1]],
                    
                    [[1,1],
                     [1,1]]
                ]
            },
            'T': {
                shape: [
                    [[0,1,0],
                     [1,1,1],
                     [0,0,0]],
                    
                    [[0,1,0],
                     [0,1,1],
                     [0,1,0]],
                    
                    [[0,0,0],
                     [1,1,1],
                     [0,1,0]],
                    
                    [[0,1,0],
                     [1,1,0],
                     [0,1,0]]
                ]
            },
            'S': {
                shape: [
                    [[0,1,1],
                     [1,1,0],
                     [0,0,0]],
                    
                    [[0,1,0],
                     [0,1,1],
                     [0,0,1]],
                    
                    [[0,0,0],
                     [0,1,1],
                     [1,1,0]],
                    
                    [[1,0,0],
                     [1,1,0],
                     [0,1,0]]
                ]
            },
            'Z': {
                shape: [
                    [[1,1,0],
                     [0,1,1],
                     [0,0,0]],
                    
                    [[0,0,1],
                     [0,1,1],
                     [0,1,0]],
                    
                    [[0,0,0],
                     [1,1,0],
                     [0,1,1]],
                    
                    [[0,1,0],
                     [1,1,0],
                     [1,0,0]]
                ]
            },
            'J': {
                shape: [
                    [[1,0,0],
                     [1,1,1],
                     [0,0,0]],
                    
                    [[0,1,1],
                     [0,1,0],
                     [0,1,0]],
                    
                    [[0,0,0],
                     [1,1,1],
                     [0,0,1]],
                    
                    [[0,1,0],
                     [0,1,0],
                     [1,1,0]]
                ]
            },
            'L': {
                shape: [
                    [[0,0,1],
                     [1,1,1],
                     [0,0,0]],
                    
                    [[0,1,0],
                     [0,1,0],
                     [0,1,1]],
                    
                    [[0,0,0],
                     [1,1,1],
                     [1,0,0]],
                    
                    [[1,1,0],
                     [0,1,0],
                     [0,1,0]]
                ]
            }
        };
    }
    
    /**
     * Initialize game state
     */
    init() {
        // Reset game state
        this.gameOver = false;
        this.score = 0;
        this.linesCleared = 0;
        this.level = 1;
        this.dropInterval = 1000;
        this.timeSinceLastDrop = 0;
        this.fastDrop = false;
        
        // Initialize empty board
        this.board = [];
        for (let y = 0; y < this.boardHeight; y++) {
            this.board[y] = [];
            for (let x = 0; x < this.boardWidth; x++) {
                this.board[y][x] = 0;
            }
        }
        
        // Spawn first piece
        this.nextPiece = this.getRandomPiece();
        this.spawnNewPiece();
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
     * Get a random tetromino piece
     */
    getRandomPiece() {
        const pieces = ['I', 'O', 'T', 'S', 'Z', 'J', 'L'];
        return pieces[Math.floor(Math.random() * pieces.length)];
    }
    
    /**
     * Spawn a new piece at the top
     */
    spawnNewPiece() {
        this.currentPiece = this.nextPiece;
        this.nextPiece = this.getRandomPiece();
        this.currentRotation = 0;
        
        // Start position (top center)
        this.currentPosition = {
            x: Math.floor(this.boardWidth / 2) - 1,
            y: 0
        };
        
        // Check if piece can be placed (game over if not)
        if (!this.isValidPosition(this.currentPosition.x, this.currentPosition.y, this.currentRotation)) {
            this.gameOver = true;
        }
    }
    
    /**
     * Check if a piece position is valid
     */
    isValidPosition(x, y, rotation) {
        const shape = this.tetrominoes[this.currentPiece].shape[rotation];
        
        for (let row = 0; row < shape.length; row++) {
            for (let col = 0; col < shape[row].length; col++) {
                if (shape[row][col]) {
                    const boardX = x + col;
                    const boardY = y + row;
                    
                    // Check boundaries
                    if (boardX < 0 || boardX >= this.boardWidth || boardY >= this.boardHeight) {
                        return false;
                    }
                    
                    // Check collision with existing blocks (but allow negative Y for spawning)
                    if (boardY >= 0 && this.board[boardY][boardX]) {
                        return false;
                    }
                }
            }
        }
        
        return true;
    }
    
    /**
     * Lock the current piece into the board
     */
    lockPiece() {
        const shape = this.tetrominoes[this.currentPiece].shape[this.currentRotation];
        
        for (let row = 0; row < shape.length; row++) {
            for (let col = 0; col < shape[row].length; col++) {
                if (shape[row][col]) {
                    const boardX = this.currentPosition.x + col;
                    const boardY = this.currentPosition.y + row;
                    
                    if (boardY >= 0 && boardY < this.boardHeight) {
                        this.board[boardY][boardX] = 1;
                    }
                }
            }
        }
        
        // Check for completed lines
        this.checkLines();
        
        // Spawn new piece
        this.spawnNewPiece();
    }
    
    /**
     * Check for and clear completed lines (Requirement 7.5)
     */
    checkLines() {
        let linesCleared = 0;
        
        // Check each row from bottom to top
        for (let y = this.boardHeight - 1; y >= 0; y--) {
            let isComplete = true;
            
            for (let x = 0; x < this.boardWidth; x++) {
                if (!this.board[y][x]) {
                    isComplete = false;
                    break;
                }
            }
            
            if (isComplete) {
                // Remove this line
                this.board.splice(y, 1);
                
                // Add empty line at top
                const emptyLine = [];
                for (let x = 0; x < this.boardWidth; x++) {
                    emptyLine.push(0);
                }
                this.board.unshift(emptyLine);
                
                linesCleared++;
                y++; // Check this row again since we shifted
            }
        }
        
        // Update score and level
        if (linesCleared > 0) {
            this.linesCleared += linesCleared;
            
            // Scoring: 100 per line, bonus for multiple lines
            const lineScores = [0, 100, 300, 500, 800];
            this.score += lineScores[Math.min(linesCleared, 4)];
            
            // Increase level every 10 lines
            const newLevel = Math.floor(this.linesCleared / 10) + 1;
            if (newLevel > this.level) {
                this.level = newLevel;
                // Increase speed (decrease drop interval)
                this.dropInterval = Math.max(100, 1000 - (this.level - 1) * 100);
            }
        }
    }
    
    /**
     * Move piece left (Requirement 7.2)
     */
    moveLeft() {
        if (this.isValidPosition(this.currentPosition.x - 1, this.currentPosition.y, this.currentRotation)) {
            this.currentPosition.x--;
        }
    }
    
    /**
     * Move piece right (Requirement 7.2)
     */
    moveRight() {
        if (this.isValidPosition(this.currentPosition.x + 1, this.currentPosition.y, this.currentRotation)) {
            this.currentPosition.x++;
        }
    }
    
    /**
     * Move piece down
     */
    moveDown() {
        if (this.isValidPosition(this.currentPosition.x, this.currentPosition.y + 1, this.currentRotation)) {
            this.currentPosition.y++;
            this.score += 1; // Small bonus for soft drop
            return true;
        } else {
            // Piece has landed
            this.lockPiece();
            return false;
        }
    }
    
    /**
     * Rotate piece clockwise (Requirement 7.3)
     */
    rotate() {
        const newRotation = (this.currentRotation + 1) % 4;
        
        // Try basic rotation
        if (this.isValidPosition(this.currentPosition.x, this.currentPosition.y, newRotation)) {
            this.currentRotation = newRotation;
            return;
        }
        
        // Try wall kicks (move left or right to make rotation fit)
        const kicks = [-1, 1, -2, 2];
        for (let kick of kicks) {
            if (this.isValidPosition(this.currentPosition.x + kick, this.currentPosition.y, newRotation)) {
                this.currentPosition.x += kick;
                this.currentRotation = newRotation;
                return;
            }
        }
        
        // Rotation not possible
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
        this.timeSinceLastDrop += deltaTime;
        
        // Determine drop speed (faster if soft drop active)
        const currentDropInterval = this.fastDrop ? 50 : this.dropInterval;
        
        // Drop piece at intervals
        if (this.timeSinceLastDrop >= currentDropInterval) {
            this.timeSinceLastDrop = 0;
            this.moveDown();
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
        
        // Draw board border
        ctx.strokeStyle = this.foregroundColor;
        ctx.lineWidth = 2;
        ctx.strokeRect(
            this.boardOffsetX - 2,
            this.boardOffsetY - 2,
            this.boardWidth * this.blockSize + 4,
            this.boardHeight * this.blockSize + 4
        );
        
        // Draw locked blocks on board
        for (let y = 0; y < this.boardHeight; y++) {
            for (let x = 0; x < this.boardWidth; x++) {
                if (this.board[y][x]) {
                    this.drawBlock(x, y);
                }
            }
        }
        
        // Draw current piece
        if (this.currentPiece) {
            const shape = this.tetrominoes[this.currentPiece].shape[this.currentRotation];
            for (let row = 0; row < shape.length; row++) {
                for (let col = 0; col < shape[row].length; col++) {
                    if (shape[row][col]) {
                        const x = this.currentPosition.x + col;
                        const y = this.currentPosition.y + row;
                        if (y >= 0) { // Only draw if visible
                            this.drawBlock(x, y);
                        }
                    }
                }
            }
        }
        
        // Draw UI (score, level, lines, next piece)
        this.drawUI();
    }
    
    /**
     * Draw a single block
     */
    drawBlock(x, y) {
        const ctx = this.context;
        const pixelX = this.boardOffsetX + x * this.blockSize;
        const pixelY = this.boardOffsetY + y * this.blockSize;
        
        // Draw filled block (solid monochrome - Requirement 7.7)
        ctx.fillStyle = this.foregroundColor;
        ctx.fillRect(pixelX + 1, pixelY + 1, this.blockSize - 2, this.blockSize - 2);
    }
    
    /**
     * Draw UI elements (score, level, next piece)
     */
    drawUI() {
        const ctx = this.context;
        ctx.fillStyle = this.foregroundColor;
        ctx.font = '20px VT323, Courier New, monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'top';
        
        const uiX = this.boardOffsetX + this.boardWidth * this.blockSize + 20;
        let uiY = this.boardOffsetY;
        
        // Score
        ctx.fillText(`Score: ${this.score}`, uiX, uiY);
        uiY += 30;
        
        // Level
        ctx.fillText(`Level: ${this.level}`, uiX, uiY);
        uiY += 30;
        
        // Lines
        ctx.fillText(`Lines: ${this.linesCleared}`, uiX, uiY);
        uiY += 50;
        
        // High score
        const highScore = HighScoreManager.getHighScore('tetris');
        ctx.fillText(`High: ${highScore}`, uiX, uiY);
        uiY += 50;
        
        // Next piece
        ctx.fillText('Next:', uiX, uiY);
        uiY += 30;
        
        if (this.nextPiece) {
            const nextShape = this.tetrominoes[this.nextPiece].shape[0];
            for (let row = 0; row < nextShape.length; row++) {
                for (let col = 0; col < nextShape[row].length; col++) {
                    if (nextShape[row][col]) {
                        const blockX = uiX + col * 15;
                        const blockY = uiY + row * 15;
                        ctx.fillRect(blockX, blockY, 13, 13);
                    }
                }
            }
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
        
        ctx.fillText('TETRIS', centerX, centerY - 100);
        
        ctx.font = '24px VT323, Courier New, monospace';
        ctx.fillText('Arrow Keys: Move & Rotate', centerX, centerY - 30);
        ctx.fillText('Left/Right: Move Piece', centerX, centerY);
        ctx.fillText('Up: Rotate', centerX, centerY + 30);
        ctx.fillText('Down: Soft Drop', centerX, centerY + 60);
        
        // Display high score
        const highScore = HighScoreManager.getHighScore('tetris');
        ctx.font = '20px VT323, Courier New, monospace';
        ctx.fillText(`High Score: ${highScore}`, centerX, centerY + 100);
        
        ctx.font = '18px VT323, Courier New, monospace';
        ctx.fillText('Press Any Arrow Key to Start', centerX, centerY + 140);
    }
    
    /**
     * Handle key down events
     * @param {string} key - The key that was pressed
     */
    handleKeyDown(key) {
        if (this.gameOver) {
            return;
        }
        
        switch (key) {
            case 'ArrowLeft':
                this.moveLeft(); // Requirement 7.2
                break;
            case 'ArrowRight':
                this.moveRight(); // Requirement 7.2
                break;
            case 'ArrowUp':
                this.rotate(); // Requirement 7.3
                break;
            case 'ArrowDown':
                this.fastDrop = true; // Requirement 7.4
                break;
        }
    }
    
    /**
     * Handle key up events
     * @param {string} key - The key that was released
     */
    handleKeyUp(key) {
        if (key === 'ArrowDown') {
            this.fastDrop = false;
        }
    }
    
    /**
     * Get game name
     * @returns {string}
     */
    getGameName() {
        return 'tetris';
    }
}
