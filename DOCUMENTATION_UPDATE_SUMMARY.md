# Documentation Update Summary

**Commit:** `9f2dd69cbd168aadb93e7b0b86eaa914edaaad86`  
**Message:** setup game infrastructure and core components  
**Date:** December 4, 2025

## Overview

This commit introduces the core game infrastructure for the Arcade Room Games feature, implementing three new JavaScript modules that provide the foundation for retro-style games (Snake, Tetris, Breakout) in the Iris BBS terminal interface.

---

## Files Added

### 1. `frontend/js/game.js`
**Purpose:** Abstract base class defining the interface that all games must implement.

### 2. `frontend/js/gameManager.js`
**Purpose:** Orchestrates game lifecycle, canvas management, and game state transitions.

### 3. `frontend/js/highScores.js`
**Purpose:** Manages localStorage-based high score persistence for all games.

---

## API Documentation

## `frontend/js/game.js`

### Class: `Game` (Abstract)

Base class that defines the interface for all arcade games. Cannot be instantiated directly.

#### Constructor

```javascript
constructor(canvas, context)
```

**Parameters:**
- `canvas` (HTMLCanvasElement) - The game canvas element
- `context` (CanvasRenderingContext2D) - The canvas 2D rendering context

**Throws:**
- `TypeError` - If attempting to instantiate Game directly (must be subclassed)

**Properties:**
- `canvas` (HTMLCanvasElement) - Reference to the game canvas
- `context` (CanvasRenderingContext2D) - Reference to the canvas context
- `gameOver` (boolean) - Game over state flag (default: false)
- `score` (number) - Current game score (default: 0)

---

#### Methods

##### `init()`
Initialize game state. Must be implemented by subclasses.

**Throws:**
- `Error` - If not implemented by subclass

---

##### `start()`
Start the game. Must be implemented by subclasses.

**Throws:**
- `Error` - If not implemented by subclass

---

##### `stop()`
Stop the game. Must be implemented by subclasses.

**Throws:**
- `Error` - If not implemented by subclass

---

##### `reset()`
Reset game to initial state. Must be implemented by subclasses.

**Throws:**
- `Error` - If not implemented by subclass

---

##### `update(deltaTime)`
Update game state based on elapsed time.

**Parameters:**
- `deltaTime` (number) - Time elapsed since last update in milliseconds

**Throws:**
- `Error` - If not implemented by subclass

---

##### `render()`
Render game graphics to the canvas. Must be implemented by subclasses.

**Throws:**
- `Error` - If not implemented by subclass

---

##### `handleKeyDown(key)`
Handle keyboard key press events.

**Parameters:**
- `key` (string) - The key that was pressed (e.g., 'ArrowUp', 'w')

**Throws:**
- `Error` - If not implemented by subclass

---

##### `handleKeyUp(key)`
Handle keyboard key release events.

**Parameters:**
- `key` (string) - The key that was released

**Throws:**
- `Error` - If not implemented by subclass

---

##### `isGameOver()`
Check if the game is over.

**Returns:**
- (boolean) - True if game is over, false otherwise

---

##### `getScore()`
Get the current game score.

**Returns:**
- (number) - Current score

---

##### `getGameName()`
Get the name of the game. Must be implemented by subclasses.

**Returns:**
- (string) - Game name (e.g., 'snake', 'tetris', 'breakout')

**Throws:**
- `Error` - If not implemented by subclass

---

## `frontend/js/gameManager.js`

### Class: `GameManager`

Orchestrates the complete game lifecycle including canvas management, game state transitions, input handling, and integration with the BBS interface.

#### Constructor

```javascript
constructor(chatDisplay, commandBar, sidePanel)
```

**Parameters:**
- `chatDisplay` (ChatDisplay) - Reference to the chat display component
- `commandBar` (CommandLineBar) - Reference to the command bar component
- `sidePanel` (SidePanel) - Reference to the side panel component

**Properties:**
- `chatDisplay` - Reference to chat display
- `commandBar` - Reference to command bar
- `sidePanel` - Reference to side panel
- `isActive` (boolean) - Whether a game is currently running
- `currentGame` (string|null) - Name of active game ('snake', 'tetris', 'breakout')
- `canvas` (HTMLCanvasElement|null) - Canvas element reference
- `gameInstance` (Game|null) - Active game instance
- `animationFrameId` (number|null) - RequestAnimationFrame ID for cleanup
- `lastFrameTime` (number) - Timestamp for delta time calculation
- `canvasConfig` (object) - Canvas styling configuration
  - `backgroundColor` (string) - '#000000' (pure black)
  - `foregroundColor` (string) - '#FFFFFF' (pure white)
  - `font` (string) - 'VT323, Courier New, monospace'
  - `fontSize` (number) - 19
- `exitIconSize` (number) - Exit icon dimensions (30px)
- `exitIconPadding` (number) - Exit icon padding from edge (10px)

---

#### Methods

##### `launchGame(gameName)`
Launch a game by name.

**Parameters:**
- `gameName` (string) - Name of the game to launch ('snake', 'tetris', or 'breakout')

**Returns:**
- (boolean) - True if game launched successfully, false otherwise

**Behavior:**
1. Validates game name against allowed games
2. Exits any currently active game
3. Creates canvas and hides chat interface
4. Initializes game instance
5. Sets up keyboard event listeners
6. Starts game loop

**Error Handling:**
- Returns false if game name is invalid
- Returns false if canvas creation fails
- Returns false if game instance creation fails
- Cleans up and restores chat on any error

---

##### `exitGame()`
Exit the current game and restore chat interface.

**Behavior:**
1. Stops game loop
2. Saves high score if applicable
3. Stops game instance
4. Removes keyboard event listeners
5. Removes canvas and restores chat display
6. Resets all game state

**Note:** Safe to call even if no game is active (no-op).

---

##### `isGameActive()`
Check if a game is currently active.

**Returns:**
- (boolean) - True if a game is running, false otherwise

---

##### `getCurrentGame()`
Get the name of the currently active game.

**Returns:**
- (string|null) - Game name ('snake', 'tetris', 'breakout') or null if no game active

---

##### `createCanvas()`
Create and display the game canvas, hiding the chat interface.

**Returns:**
- (boolean) - True if canvas created successfully, false otherwise

**Behavior:**
1. Hides chat display container
2. Hides command bar
3. Creates canvas element with monochrome styling
4. Sets canvas dimensions to match terminal content area
5. Appends canvas to DOM
6. Sets up click handler for exit icon

**Fallback:** Uses 800x600 dimensions if terminal content area not found.

---

##### `removeCanvas()`
Remove the game canvas and restore chat display.

**Behavior:**
1. Removes canvas from DOM
2. Restores chat display visibility
3. Restores command bar visibility
4. Nullifies canvas reference

**Error Handling:** Catches and logs any errors during cleanup.

---

##### `handleRoomChange(newRoom)`
Handle room change events - terminates game if user leaves Arcade Room.

**Parameters:**
- `newRoom` (string) - Name of the new room

**Behavior:**
- Calls `exitGame()` if active game exists and new room is not 'Arcade Hall' or 'Arcade Room'

---

##### `createGameInstance(gameName)`
Create a game instance based on game name.

**Parameters:**
- `gameName` (string) - Name of the game

**Returns:**
- (Game|null) - Game instance or null

**Note:** Currently returns null as individual games are not yet implemented. Will be updated when Snake, Tetris, and Breakout classes are added.

---

##### `handleCanvasClick(event)`
Handle canvas click events (for exit icon detection).

**Parameters:**
- `event` (MouseEvent) - Click event

**Behavior:**
- Calculates click position relative to canvas
- Checks if click is within exit icon bounds (top-right corner)
- Calls `exitGame()` if exit icon was clicked

---

##### `renderExitIcon(ctx)`
Render the exit icon in the top-right corner of the canvas.

**Parameters:**
- `ctx` (CanvasRenderingContext2D) - Canvas rendering context

**Rendering:**
- Draws white 'X' symbol
- Draws white border around icon
- Uses monochrome color scheme
- Positioned with 10px padding from top-right corner

---

##### `handleKeyDown(event)`
Handle keyboard key down events and route to active game.

**Parameters:**
- `event` (KeyboardEvent) - Keyboard event

**Behavior:**
- Prevents default behavior for arrow keys and space
- Routes key press to game instance's `handleKeyDown()` method
- Catches and logs any errors

**Note:** Only processes events when a game is active.

---

##### `handleKeyUp(event)`
Handle keyboard key up events and route to active game.

**Parameters:**
- `event` (KeyboardEvent) - Keyboard event

**Behavior:**
- Routes key release to game instance's `handleKeyUp()` method
- Catches and logs any errors

**Note:** Only processes events when a game is active.

---

##### `startGameLoop()`
Start the game loop using requestAnimationFrame.

**Behavior:**
- Initializes `lastFrameTime` with current timestamp
- Calls `gameLoop()` to begin animation loop

---

##### `stopGameLoop()`
Stop the game loop.

**Behavior:**
- Cancels pending animation frame
- Nullifies animation frame ID

---

##### `gameLoop()`
Main game loop - updates and renders game state.

**Behavior:**
1. Calculates delta time since last frame
2. Updates game state via `gameInstance.update(deltaTime)`
3. Clears canvas
4. Renders game via `gameInstance.render()`
5. Renders exit icon overlay
6. Checks for game over condition
7. Schedules next frame via requestAnimationFrame

**Error Handling:**
- Catches errors and calls `exitGame()` to clean up
- Automatically stops loop if game is over

---

##### `handleGameOver()`
Handle game over state - display results and update high scores.

**Behavior:**
1. Retrieves final score from game instance
2. Compares with stored high score
3. Renders game over screen with:
   - "GAME OVER" title
   - Final score
   - High score or "NEW HIGH SCORE!" message
   - Exit instruction
4. Updates high score in localStorage if applicable
5. Stops game loop but keeps canvas visible

---

## `frontend/js/highScores.js`

### Class: `HighScoreManager` (Static)

Utility class for managing high score persistence using browser localStorage. All methods are static.

#### Static Properties

##### `KEY_PREFIX`
Storage key prefix for high scores.

**Value:** `'arcade_highscore_'`

**Usage:** Combined with game name to create unique localStorage keys (e.g., 'arcade_highscore_snake')

---

#### Static Methods

##### `getHighScore(gameName)`
Retrieve the high score for a specific game.

**Parameters:**
- `gameName` (string) - Name of the game ('snake', 'tetris', 'breakout')

**Returns:**
- (number) - High score, or 0 if none exists or on error

**Behavior:**
- Constructs localStorage key using `KEY_PREFIX + gameName.toLowerCase()`
- Retrieves value from localStorage
- Parses as integer
- Returns 0 if value is null, NaN, or error occurs

**Error Handling:**
- Catches localStorage errors (e.g., quota exceeded, unavailable)
- Logs warning and returns 0 on error

---

##### `setHighScore(gameName, score)`
Save a high score for a specific game.

**Parameters:**
- `gameName` (string) - Name of the game
- `score` (number) - Score to save

**Returns:**
- (boolean) - True if save was successful, false on error

**Behavior:**
- Constructs localStorage key
- Converts score to string
- Stores in localStorage

**Error Handling:**
- Catches localStorage errors
- Logs warning and returns false on error

---

##### `isNewHighScore(gameName, score)`
Check if a score qualifies as a new high score.

**Parameters:**
- `gameName` (string) - Name of the game
- `score` (number) - Score to check

**Returns:**
- (boolean) - True if score is higher than current high score

**Behavior:**
- Retrieves current high score
- Compares with provided score
- Returns true only if new score is strictly greater

---

##### `updateHighScore(gameName, score)`
Update high score if the new score is higher.

**Parameters:**
- `gameName` (string) - Name of the game
- `score` (number) - Score to potentially save

**Returns:**
- (boolean) - True if high score was updated, false otherwise

**Behavior:**
- Checks if score is a new high score
- Saves score only if it's higher than current high score
- Returns false if score is not higher (no update performed)

---

## Usage Examples

### Example 1: Implementing a Game

```javascript
import { Game } from './game.js';

class SnakeGame extends Game {
    constructor(canvas, context) {
        super(canvas, context);
        this.snake = [];
        this.direction = { x: 1, y: 0 };
        this.food = { x: 0, y: 0 };
    }
    
    init() {
        // Initialize snake at center
        this.snake = [
            { x: 10, y: 10 },
            { x: 9, y: 10 },
            { x: 8, y: 10 }
        ];
        this.spawnFood();
        this.score = 0;
        this.gameOver = false;
    }
    
    start() {
        // Game starts immediately
    }
    
    stop() {
        // Cleanup if needed
    }
    
    reset() {
        this.init();
    }
    
    update(deltaTime) {
        // Move snake, check collisions, etc.
    }
    
    render() {
        // Draw snake and food on canvas
        this.context.fillStyle = '#FFFFFF';
        this.snake.forEach(segment => {
            this.context.fillRect(segment.x * 20, segment.y * 20, 18, 18);
        });
    }
    
    handleKeyDown(key) {
        if (key === 'ArrowUp' && this.direction.y === 0) {
            this.direction = { x: 0, y: -1 };
        }
        // Handle other directions...
    }
    
    handleKeyUp(key) {
        // Not needed for Snake
    }
    
    getGameName() {
        return 'snake';
    }
    
    spawnFood() {
        this.food = {
            x: Math.floor(Math.random() * 30),
            y: Math.floor(Math.random() * 20)
        };
    }
}
```

### Example 2: Integrating GameManager

```javascript
import { GameManager } from './gameManager.js';

// In main.js initialization
const gameManager = new GameManager(chatDisplay, commandBar, sidePanel);

// Handle game launch command from WebSocket
websocket.on('message', (data) => {
    if (data.type === 'launch_game') {
        const success = gameManager.launchGame(data.game);
        if (!success) {
            chatDisplay.addSystemMessage('Failed to launch game');
        }
    }
});

// Handle room changes
websocket.on('room_change', (data) => {
    gameManager.handleRoomChange(data.room);
});

// Handle exit game command
commandBar.on('command', (cmd) => {
    if (cmd === '/exit_game') {
        gameManager.exitGame();
    }
});
```

### Example 3: Using HighScoreManager

```javascript
import { HighScoreManager } from './highScores.js';

// Get high score for display
const snakeHighScore = HighScoreManager.getHighScore('snake');
console.log(`Snake High Score: ${snakeHighScore}`);

// Check if player achieved new high score
const finalScore = 150;
if (HighScoreManager.isNewHighScore('snake', finalScore)) {
    console.log('Congratulations! New high score!');
    HighScoreManager.setHighScore('snake', finalScore);
}

// Or use the convenience method
const wasUpdated = HighScoreManager.updateHighScore('tetris', 2500);
if (wasUpdated) {
    console.log('High score updated!');
}
```

### Example 4: Complete Game Launch Flow

```javascript
// User types: /play snake

// 1. Backend validates command and sends WebSocket message
{
    type: 'launch_game',
    game: 'snake'
}

// 2. Frontend receives message and launches game
gameManager.launchGame('snake');

// 3. GameManager:
//    - Hides chat display
//    - Creates canvas
//    - Initializes SnakeGame instance
//    - Starts game loop
//    - Listens for keyboard input

// 4. User plays game...

// 5. User clicks exit icon or types /exit_game
gameManager.exitGame();

// 6. GameManager:
//    - Stops game loop
//    - Saves high score if applicable
//    - Removes canvas
//    - Restores chat display
```

---

## Integration Points

### Required Integrations

1. **Command Handler** (`backend/commands/handler.py`)
   - Add `/play <game>` command
   - Add `/exit_game` command
   - Validate user is in Arcade Room
   - Send `launch_game` WebSocket message

2. **Main Application** (`frontend/js/main.js`)
   - Import and instantiate GameManager
   - Handle `launch_game` WebSocket messages
   - Handle room change events
   - Route `/exit_game` commands

3. **Sidebar** (`frontend/js/sidePanel.js`)
   - Add collapsible game menu under Arcade Room
   - Add click handlers for Snake, Tetris, Breakout
   - Trigger game launch on click

4. **Individual Games** (To be implemented)
   - `frontend/js/snake.js` - Implement SnakeGame class
   - `frontend/js/tetris.js` - Implement TetrisGame class
   - `frontend/js/breakout.js` - Implement BreakoutGame class
   - Update `GameManager.createGameInstance()` to instantiate games

---

## Design Decisions

### Monochrome Aesthetic
All games use pure black (#000000) and white (#FFFFFF) colors to maintain the retro terminal aesthetic. No gradients, colors, or anti-aliasing.

### Silent Operation
No audio is played. All feedback is visual only, maintaining the quiet BBS atmosphere.

### localStorage for Persistence
High scores are stored client-side in browser localStorage. This is appropriate because:
- Scores are non-sensitive
- No server-side storage required
- Works offline
- Per-user, per-browser persistence

### Canvas Replacement Strategy
The game canvas completely replaces the chat area rather than overlaying it. This:
- Provides maximum space for gameplay
- Eliminates visual distractions
- Maintains clear separation between chat and game modes
- Simplifies state management

### Room-Based Game Termination
Games automatically terminate when users leave the Arcade Room. This prevents:
- Games running in background
- Resource leaks
- Confusion about game state
- Unexpected behavior when returning to Arcade Room

---

## Error Handling

### Canvas Creation Failures
- Returns false from `createCanvas()`
- Logs error to console
- Allows retry by user

### localStorage Unavailability
- Games continue to function
- High scores not persisted
- Warning logged to console
- No user-facing error (graceful degradation)

### Game Instance Errors
- Caught in game loop
- Triggers `exitGame()` for cleanup
- Restores chat interface
- Logs error for debugging

### Keyboard Event Errors
- Caught and logged
- Game continues running
- Prevents single input error from crashing game

---

## Performance Considerations

### Frame Rate
- Uses `requestAnimationFrame` for optimal frame rate
- Target: 30+ FPS (per requirements)
- Delta time calculation for smooth animation
- Automatic throttling by browser

### Memory Management
- Canvas removed from DOM on exit
- Event listeners cleaned up
- Animation frames cancelled
- Game instances nullified for garbage collection

### Input Responsiveness
- Direct event routing to game instance
- Minimal processing overhead
- Target: <50ms input latency (per requirements)

---

## Testing Recommendations

### Unit Tests

1. **Game Base Class**
   - Test abstract class cannot be instantiated
   - Test all methods throw errors when not implemented
   - Test `isGameOver()` and `getScore()` return correct values

2. **GameManager**
   - Test `launchGame()` with valid/invalid game names
   - Test `exitGame()` cleans up properly
   - Test `handleRoomChange()` terminates games correctly
   - Test canvas creation and removal
   - Test keyboard event routing
   - Test game loop execution

3. **HighScoreManager**
   - Test `getHighScore()` returns 0 for new games
   - Test `setHighScore()` persists scores
   - Test `isNewHighScore()` comparison logic
   - Test `updateHighScore()` only updates when higher
   - Test localStorage error handling

### Integration Tests

1. **Complete Game Flow**
   - Launch game → Play → Exit → Verify chat restored
   - Launch game → Switch rooms → Verify game terminated
   - Launch game → Achieve high score → Verify saved

2. **Multi-Game Session**
   - Launch Snake → Exit → Launch Tetris → Exit
   - Verify independent high scores
   - Verify clean state transitions

3. **Error Scenarios**
   - localStorage disabled
   - Canvas creation failure
   - Game instance errors during gameplay

---

## Future Enhancements

1. **Game Implementations**
   - Snake game with grid-based movement
   - Tetris with falling blocks and line clearing
   - Breakout with paddle and ball physics

2. **Additional Features**
   - Pause functionality
   - Difficulty levels
   - Server-side leaderboards
   - Game replays
   - Achievements system

3. **Performance Optimizations**
   - Off-screen canvas for complex rendering
   - Dirty rectangle optimization
   - Web Workers for game logic

---

## Related Requirements

This implementation satisfies the following requirements from the spec:

- **Requirement 3.1-3.5**: Canvas display and monochrome styling
- **Requirement 4.1-4.5**: Game exit mechanisms and chat restoration
- **Requirement 5.1-5.5**: Room change handling and game termination
- **Requirement 9.1-9.5**: High score persistence and display
- **Requirement 10.1-10.5**: Performance and input handling
- **Requirement 11.1-11.5**: Silent operation (no audio)

---

## Changelog

### 2025-12-04 - Initial Implementation
- Added `Game` abstract base class
- Added `GameManager` for game lifecycle orchestration
- Added `HighScoreManager` for score persistence
- Implemented canvas management and UI transitions
- Implemented keyboard input routing
- Implemented game loop with requestAnimationFrame
- Implemented exit icon rendering and click handling
- Implemented room change detection and game termination
- Implemented high score comparison and storage

---

**README.md update skipped** — No new public exports requiring README documentation. These are internal game infrastructure modules that will be integrated into the existing BBS application.
