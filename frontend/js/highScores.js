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
     * Get high score for a specific game
     * @param {string} gameName - Name of the game (snake, tetris, breakout)
     * @returns {number} - High score (0 if none exists)
     */
    static getHighScore(gameName) {
        try {
            const key = this.KEY_PREFIX + gameName.toLowerCase();
            const stored = localStorage.getItem(key);
            
            if (stored === null) {
                return 0;
            }
            
            const score = parseInt(stored, 10);
            return isNaN(score) ? 0 : score;
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
            const key = this.KEY_PREFIX + gameName.toLowerCase();
            localStorage.setItem(key, score.toString());
            return true;
        } catch (error) {
            console.warn('Failed to save high score:', error);
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
        const currentHighScore = this.getHighScore(gameName);
        return score > currentHighScore;
    }
    
    /**
     * Update high score if the new score is higher
     * @param {string} gameName - Name of the game
     * @param {number} score - Score to potentially save
     * @returns {boolean} - True if high score was updated
     */
    static updateHighScore(gameName, score) {
        if (this.isNewHighScore(gameName, score)) {
            return this.setHighScore(gameName, score);
        }
        return false;
    }
}
