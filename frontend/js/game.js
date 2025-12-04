/**
 * Base Game Interface
 * All games must implement this interface
 * Requirements: 3.1, 3.2, 4.1, 4.2
 * 
 * SILENT DESIGN REQUIREMENT (Requirements 11.1, 11.2, 11.3, 11.4, 11.5):
 * All games implementing this interface must be completely silent without any audio.
 * - No audio elements should be created
 * - No audio files should be loaded or referenced
 * - No sound playback should occur during gameplay or events
 * - All feedback must be provided through visual means only
 * This maintains the quiet retro-terminal atmosphere of the BBS.
 */

export class Game {
    /**
     * @param {HTMLCanvasElement} canvas - The game canvas
     * @param {CanvasRenderingContext2D} context - The canvas 2D context
     */
    constructor(canvas, context) {
        if (new.target === Game) {
            throw new TypeError("Cannot construct Game instances directly - it's an abstract class");
        }
        
        this.canvas = canvas;
        this.context = context;
        this.gameOver = false;
        this.score = 0;
    }
    
    /**
     * Initialize game state
     * Must be implemented by subclasses
     */
    init() {
        throw new Error("Method 'init()' must be implemented");
    }
    
    /**
     * Start the game
     * Must be implemented by subclasses
     */
    start() {
        throw new Error("Method 'start()' must be implemented");
    }
    
    /**
     * Stop the game
     * Must be implemented by subclasses
     */
    stop() {
        throw new Error("Method 'stop()' must be implemented");
    }
    
    /**
     * Reset game to initial state
     * Must be implemented by subclasses
     */
    reset() {
        throw new Error("Method 'reset()' must be implemented");
    }
    
    /**
     * Update game state
     * @param {number} deltaTime - Time elapsed since last update (ms)
     * Must be implemented by subclasses
     */
    update(deltaTime) {
        throw new Error("Method 'update()' must be implemented");
    }
    
    /**
     * Render game graphics
     * Must be implemented by subclasses
     */
    render() {
        throw new Error("Method 'render()' must be implemented");
    }
    
    /**
     * Handle key down events
     * @param {string} key - The key that was pressed
     * Must be implemented by subclasses
     */
    handleKeyDown(key) {
        throw new Error("Method 'handleKeyDown()' must be implemented");
    }
    
    /**
     * Handle key up events
     * @param {string} key - The key that was released
     * Must be implemented by subclasses
     */
    handleKeyUp(key) {
        throw new Error("Method 'handleKeyUp()' must be implemented");
    }
    
    /**
     * Check if game is over
     * @returns {boolean}
     */
    isGameOver() {
        return this.gameOver;
    }
    
    /**
     * Get current score
     * @returns {number}
     */
    getScore() {
        return this.score;
    }
    
    /**
     * Get game name
     * Must be implemented by subclasses
     * @returns {string}
     */
    getGameName() {
        throw new Error("Method 'getGameName()' must be implemented");
    }
}
