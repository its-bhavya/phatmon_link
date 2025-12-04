/**
 * High Score Manager
 * Manages localStorage-based score persistence
 * Requirements: 9.1, 9.2, 9.5
 * 
 * SILENT DESIGN REQUIREMENT (Requirements 11.1, 11.2, 11.3, 11.4, 11.5):
 * High score updates are intentionally silent without any audio feedback.
 * - No audio elements are created when scores are saved or updated
 * - No sound effects play when achieving a new high score
 * - All feedback is provided through visual means only
 * This maintains the quiet retro-terminal atmosphere of the BBS.
 */

export class HighScoreManager {
    /**
     * Storage key prefix for high scores
     */
    static KEY_PREFIX = 'arcade_highscore_';
    
    /**
     * Check if localStorage is available
     * @returns {boolean} - True if localStorage is available
     */
    static isLocalStorageAvailable() {
        try {
            const test = '__localStorage_test__';
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch (error) {
            return false;
        }
    }
    
    /**
     * Get high score for a specific game
     * @param {string} gameName - Name of the game (snake, tetris, breakout)
     * @returns {number} - High score (0 if none exists or localStorage unavailable)
     */
    static getHighScore(gameName) {
        try {
            // Check if localStorage is available
            if (!this.isLocalStorageAvailable()) {
                console.warn('localStorage is not available - high scores will not persist');
                return 0;
            }
            
            // Validate game name
            if (!gameName || typeof gameName !== 'string') {
                console.warn('Invalid game name provided to getHighScore');
                return 0;
            }
            
            const key = this.KEY_PREFIX + gameName.toLowerCase();
            const stored = localStorage.getItem(key);
            
            if (stored === null || stored === undefined) {
                return 0;
            }
            
            const score = parseInt(stored, 10);
            
            // Validate parsed score
            if (isNaN(score) || score < 0) {
                console.warn(`Invalid high score data for ${gameName}: ${stored}`);
                return 0;
            }
            
            return score;
        } catch (error) {
            console.warn('Failed to retrieve high score:', error);
            return 0;
        }
    }
    
    /**
     * Set high score for a specific game
     * @param {string} gameName - Name of the game (snake, tetris, breakout)
     * @param {number} score - Score to save
     * @returns {boolean} - True if save was successful
     */
    static setHighScore(gameName, score) {
        try {
            // Check if localStorage is available
            if (!this.isLocalStorageAvailable()) {
                console.warn('localStorage is not available - high score will not be saved');
                return false;
            }
            
            // Validate inputs
            if (!gameName || typeof gameName !== 'string') {
                console.warn('Invalid game name provided to setHighScore');
                return false;
            }
            
            if (typeof score !== 'number' || isNaN(score) || score < 0) {
                console.warn('Invalid score provided to setHighScore:', score);
                return false;
            }
            
            const key = this.KEY_PREFIX + gameName.toLowerCase();
            localStorage.setItem(key, score.toString());
            return true;
        } catch (error) {
            // Handle quota exceeded or other localStorage errors
            if (error.name === 'QuotaExceededError') {
                console.warn('localStorage quota exceeded - high score cannot be saved');
            } else {
                console.warn('Failed to save high score:', error);
            }
            return false;
        }
    }
    
    /**
     * Check if a score is a new high score
     * @param {string} gameName - Name of the game
     * @param {number} score - Score to check
     * @returns {boolean} - True if this is a new high score
     */
    static isNewHighScore(gameName, score) {
        try {
            // Validate inputs
            if (typeof score !== 'number' || isNaN(score) || score < 0) {
                return false;
            }
            
            const currentHighScore = this.getHighScore(gameName);
            return score > currentHighScore;
        } catch (error) {
            console.warn('Error checking if new high score:', error);
            return false;
        }
    }
    
    /**
     * Update high score if the new score is higher
     * @param {string} gameName - Name of the game
     * @param {number} score - Score to potentially save
     * @returns {boolean} - True if high score was updated
     */
    static updateHighScore(gameName, score) {
        try {
            if (this.isNewHighScore(gameName, score)) {
                return this.setHighScore(gameName, score);
            }
            return false;
        } catch (error) {
            console.warn('Error updating high score:', error);
            return false;
        }
    }
}
