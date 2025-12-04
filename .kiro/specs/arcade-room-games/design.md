# Design Document

## Overview

The Arcade Room Games feature extends the Iris BBS with three playable retro-style games accessible from the Arcade Room (currently named "Arcade Hall"). The implementation follows a modular architecture with a game engine manager that handles canvas rendering, input processing, and game state management. Each game (Snake, Tetris, Breakout) is implemented as a separate module with its own game logic while sharing common infrastructure for rendering, input handling, and high score persistence.

The design integrates seamlessly with the existing BBS architecture by:
- Extending the command handler to recognize game launch commands
- Adding game launcher UI elements to the sidebar
- Replacing the chat display area with a canvas during gameplay
- Automatically terminating games when users switch rooms
- Maintaining the monochrome retro-terminal aesthetic throughout

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
├─────────────────────────────────────────────────────────┤
│  main.js (Application Entry Point)                      │
│    ├─ commandBar.js (Command Input)                     │
│    ├─ chatDisplay.js (Chat Messages)                    │
│    ├─ sidePanel.js (Room/User Lists)                    │
│    └─ gameManager.js (NEW - Game Orchestration)         │
│         ├─ snake.js (Snake Game Logic)                  │
│         ├─ tetris.js (Tetris Game Logic)                │
│         ├─ breakout.js (Breakout Game Logic)            │
│         └─ highScores.js (Score Persistence)            │
└─────────────────────────────────────────────────────────┘
                          │
                          │ WebSocket
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Backend Layer                         │
├─────────────────────────────────────────────────────────┤
│  main.py (FastAPI Application)                          │
│    └─ commands/handler.py (EXTENDED)                    │
│         └─ Game command validation                      │
└─────────────────────────────────────────────────────────┘
```

### Component Interaction Flow

1. **Game Launch Flow**:
   - User types `/play snake` OR clicks sidebar game item
   - Command handler validates user is in Arcade Room
   - GameManager creates canvas and initializes game
   - Chat area is hidden, canvas is displayed
   - Game loop starts with keyboard input handling

2. **Game Exit Flow**:
   - User clicks exit icon OR types `/exit_game` OR switches rooms
   - Game loop stops, final score is compared with high score
   - Canvas is removed, chat area is restored
   - User returns to normal Arcade Room chat

## Components and Interfaces

### 1. GameManager (New Component)

**Responsibility**: Orchestrates game lifecycle, canvas management, and game state transitions.

**Interface**:
```javascript
class GameManager {
    constructor(chatDisplay, commandBar, sidePanel)
    
    // Game lifecycle
    launchGame(gameName: string): void
    exitGame(): void
    isGameActive(): boolean
    getCurrentGame(): string | null
    
    // Canvas management
    createCanvas(): HTMLCanvasElement
    removeCanvas(): void
    
    // Event handling
    handleRoomChange(newRoom: string): void
    handleKeyPress(event: KeyboardEvent): void
}
```

**Key Methods**:
- `launchGame(gameName)`: Validates game name, creates canvas, initializes game instance, starts game loop
- `exitGame()`: Stops game loop, saves high score if applicable, removes canvas, restores chat
- `handleRoomChange(newRoom)`: Terminates active game if user leaves Arcade Room
- `handleKeyPress(event)`: Routes keyboard input to active game instance

### 2. Game Base Interface

**Responsibility**: Defines common interface that all games must implement.

**Interface**:
```javascript
class Game {
    constructor(canvas: HTMLCanvasElement, context: CanvasRenderingContext2D)
    
    // Game lifecycle
    init(): void
    start(): void
    stop(): void
    reset(): void
    
    // Game loop
    update(deltaTime: number): void
    render(): void
    
    // Input handling
    handleKeyDown(key: string): void
    handleKeyUp(key: string): void
    
    // State queries
    isGameOver(): boolean
    getScore(): number
    getGameName(): string
}
```

### 3. Snake Game

**Responsibility**: Implements classic Snake game mechanics.

**State**:
```javascript
{
    snake: Array<{x: number, y: number}>,  // Snake segments
    direction: {x: number, y: number},      // Current direction
    food: {x: number, y: number},           // Food position
    score: number,                          // Current score
    gameOver: boolean,                      // Game state
    gridSize: number,                       // Grid cell size
    speed: number                           // Movement speed (ms)
}
```

**Key Logic**:
- Grid-based movement with collision detection
- Snake grows when eating food
- Game ends on wall or self-collision
- Score increases with each food item

### 4. Tetris Game

**Responsibility**: Implements falling block puzzle mechanics.

**State**:
```javascript
{
    board: Array<Array<number>>,            // 10x20 grid
    currentPiece: Tetromino,                // Active piece
    currentPosition: {x: number, y: number}, // Piece position
    score: number,                          // Current score
    linesCleared: number,                   // Total lines cleared
    gameOver: boolean,                      // Game state
    dropInterval: number,                   // Fall speed (ms)
    lastDropTime: number                    // Timing control
}
```

**Key Logic**:
- Seven tetromino shapes (I, O, T, S, Z, J, L)
- Rotation with wall kick detection
- Line clearing with gravity
- Progressive speed increase
- Game ends when pieces stack above top

### 5. Breakout Game

**Responsibility**: Implements paddle and ball brick-breaking mechanics.

**State**:
```javascript
{
    paddle: {x: number, y: number, width: number, height: number},
    ball: {x: number, y: number, dx: number, dy: number, radius: number},
    bricks: Array<{x: number, y: number, width: number, height: number, alive: boolean}>,
    score: number,
    gameOver: boolean,
    levelComplete: boolean
}
```

**Key Logic**:
- Ball physics with angle-based bouncing
- Paddle collision with ball direction modification
- Brick destruction and scoring
- Level completion detection
- Game ends when ball falls below paddle

### 6. HighScoreManager (New Component)

**Responsibility**: Persists and retrieves high scores using localStorage.

**Interface**:
```javascript
class HighScoreManager {
    getHighScore(gameName: string): number
    setHighScore(gameName: string, score: number): void
    isNewHighScore(gameName: string, score: number): boolean
}
```

**Storage Keys**:
- `arcade_highscore_snake`
- `arcade_highscore_tetris`
- `arcade_highscore_breakout`

### 7. Command Handler Extension (Backend)

**Responsibility**: Validates game commands and ensures user is in Arcade Room.

**New Commands**:
- `/play snake` - Launch Snake game
- `/play tetris` - Launch Tetris game
- `/play breakout` - Launch Breakout game
- `/exit_game` - Exit current game

**Validation Logic**:
```python
def play_command(user: User, game_name: str) -> dict:
    current_room = websocket_manager.get_user_room(user.username)
    
    if current_room != "Arcade Hall":
        return error_response("Games are only available in the Arcade Room")
    
    valid_games = ["snake", "tetris", "breakout"]
    if game_name.lower() not in valid_games:
        return error_response(f"Unknown game: {game_name}. Available: {', '.join(valid_games)}")
    
    return {
        "type": "launch_game",
        "game": game_name.lower()
    }
```

### 8. Sidebar Extension

**Responsibility**: Adds collapsible game launcher menu under Arcade Room.

**UI Structure**:
```
Arcade Hall (5 users)
  ├─ Snake
  ├─ Tetris
  └─ Breakout
```

**Implementation**:
- Extend `sidePanel.js` to render sub-items for Arcade Room
- Add click handlers that trigger game launch
- Auto-switch to Arcade Room if user clicks game from different room

## Data Models

### Game State Model

```javascript
{
    isActive: boolean,           // Whether a game is currently running
    currentGame: string | null,  // Name of active game ('snake', 'tetris', 'breakout')
    canvas: HTMLCanvasElement | null,  // Canvas element reference
    gameInstance: Game | null,   // Active game instance
    animationFrameId: number | null,  // RequestAnimationFrame ID for cleanup
    lastFrameTime: number        // For delta time calculation
}
```

### High Score Model

```javascript
{
    snake: number,      // Best score for Snake
    tetris: number,     // Best score for Tetris
    breakout: number    // Best score for Breakout
}
```

### Canvas Configuration

```javascript
{
    width: number,      // Canvas width (matches chat area)
    height: number,     // Canvas height (matches chat area)
    backgroundColor: '#000000',  // Pure black
    foregroundColor: '#FFFFFF',  // Pure white
    font: 'VT323, Courier New, monospace',  // Retro terminal font
    fontSize: 19        // Consistent with terminal
}
```

## Cor
rectness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

After analyzing the acceptance criteria, several properties are redundant and can be consolidated:
- Properties 4.5 and 5.3 both test game state discarding - these can be combined
- Properties 11.1, 11.2, 11.3, and 11.5 all test silence - these can be combined
- Properties 3.5, 7.7, and 8.7 all test monochrome rendering - these can be combined

**Property 1: Game commands rejected outside Arcade Room**
*For any* room that is not the Arcade Room, when a user attempts to execute a game command (/play snake, /play tetris, /play breakout), the system should return an error message indicating games are only available in the Arcade Room.
**Validates: Requirements 1.4**

**Property 2: Invalid game names produce error**
*For any* string that is not "snake", "tetris", or "breakout", when used with the /play command, the system should return an error message listing the available games.
**Validates: Requirements 1.5**

**Property 3: Sidebar game launch from any room**
*For any* room that is not the Arcade Room, when a user clicks a game launcher in the sidebar, the system should switch the user to the Arcade Room and then launch the selected game.
**Validates: Requirements 2.5**

**Property 4: Game launch replaces chat with canvas**
*For any* game (snake, tetris, breakout), when the game is launched, the chat area should be completely replaced with a game canvas.
**Validates: Requirements 3.1**

**Property 5: Exit icon present on all game canvases**
*For any* active game canvas, an exit icon should be rendered in the top-right corner.
**Validates: Requirements 3.2**

**Property 6: Chat elements hidden during gameplay**
*For any* active game session, all chat messages and chat input elements should be hidden from view.
**Validates: Requirements 3.3**

**Property 7: Monochrome rendering**
*For any* game canvas pixel, the color value should be either pure black (#000000) or pure white (#FFFFFF) with no gradients or intermediate values.
**Validates: Requirements 3.5, 7.7, 8.7**

**Property 8: Exit mechanisms terminate game**
*For any* active game session, when the user clicks the exit icon OR types /exit_game, the game should terminate and the chat area should be restored.
**Validates: Requirements 4.1, 4.2**

**Property 9: Chat restoration after game exit**
*For any* game termination, the Arcade Room chat history should be displayed and the command input bar should be restored.
**Validates: Requirements 4.3, 4.4**

**Property 10: Game state not persisted**
*For any* game session, when the game is exited (either manually or by room switch), re-launching the same game should start with a fresh initial state, not the previous game state.
**Validates: Requirements 4.5, 5.3**

**Property 11: Room switch terminates game**
*For any* active game session, when the user switches to a different room, the game should be terminated immediately.
**Validates: Requirements 5.1**

**Property 12: No game auto-resume**
*For any* user who left the Arcade Room during a game session, when they return to the Arcade Room, the chat area should be displayed instead of the game canvas.
**Validates: Requirements 5.2**

**Property 13: Game cleanup on room switch**
*For any* room switch during an active game, all game rendering loops and input event listeners should be removed and no longer execute.
**Validates: Requirements 5.5**

**Property 14: Snake arrow key movement**
*For any* arrow key press during Snake gameplay, the snake should move in the corresponding direction (up/down/left/right).
**Validates: Requirements 6.2**

**Property 15: Snake food collision**
*For any* collision between the snake head and a food item, the snake length should increase by exactly one segment and a new food item should spawn at a different location.
**Validates: Requirements 6.3**

**Property 16: Snake wall collision ends game**
*For any* collision between the snake head and a wall boundary, the game should end and display the final score.
**Validates: Requirements 6.4**

**Property 17: Snake self-collision ends game**
*For any* collision between the snake head and its own tail, the game should end and display the final score.
**Validates: Requirements 6.5**

**Property 18: Tetris horizontal movement**
*For any* left or right arrow key press during Tetris gameplay, the active tetromino should move one unit in the corresponding horizontal direction (unless blocked).
**Validates: Requirements 7.2**

**Property 19: Tetris rotation**
*For any* up arrow key press during Tetris gameplay, the active tetromino should rotate 90 degrees clockwise (unless blocked by walls or other blocks).
**Validates: Requirements 7.3**

**Property 20: Tetris soft drop**
*For any* down arrow key press during Tetris gameplay, the active tetromino should descend faster than the normal fall speed.
**Validates: Requirements 7.4**

**Property 21: Tetris line clearing**
*For any* completely filled horizontal line in the Tetris playing field, that line should be cleared and all blocks above should shift down by one row.
**Validates: Requirements 7.5**

**Property 22: Tetris game over condition**
*For any* tetromino placement that results in blocks extending above the top boundary of the playing field, the game should end and display the final score.
**Validates: Requirements 7.6**

**Property 23: Breakout paddle movement**
*For any* left or right arrow key press during Breakout gameplay, the paddle should move in the corresponding horizontal direction (within screen bounds).
**Validates: Requirements 8.2**

**Property 24: Breakout brick collision**
*For any* collision between the ball and a brick, the brick should be destroyed, removed from the playing field, and the ball should bounce.
**Validates: Requirements 8.3**

**Property 25: Breakout paddle collision**
*For any* collision between the ball and the paddle, the ball should bounce upward (with angle depending on paddle hit location).
**Validates: Requirements 8.4**

**Property 26: Breakout ball miss ends game**
*For any* ball position where the y-coordinate is below the paddle's bottom edge, the game should end and display the final score.
**Validates: Requirements 8.5**

**Property 27: Breakout level completion**
*For any* game state where all bricks have been destroyed, the level should be marked as complete and a victory message should be displayed.
**Validates: Requirements 8.6**

**Property 28: High score comparison**
*For any* game ending, the final score should be compared with the stored high score for that game, and if higher, the high score should be updated.
**Validates: Requirements 9.1, 9.2**

**Property 29: High score display**
*For any* game start, the current high score for that game should be displayed on the start screen or game canvas.
**Validates: Requirements 9.3**

**Property 30: High score storage keys**
*For any* high score storage operation, the system should use game-specific localStorage keys in the format "arcade_highscore_{gamename}".
**Validates: Requirements 9.5**

**Property 31: Keyboard-only input**
*For any* active game session, only keyboard input should affect game state; mouse and touch inputs should be ignored for game controls.
**Validates: Requirements 10.1**

**Property 32: Minimum frame rate**
*For any* game rendering loop, the frame rate should be maintained at 30 FPS or higher during normal gameplay.
**Validates: Requirements 10.2**

**Property 33: Input responsiveness**
*For any* keyboard input during gameplay, the game should respond to the input within 50 milliseconds.
**Validates: Requirements 10.4**

**Property 34: Complete silence**
*For any* game session, no audio elements should be created, no audio files should be loaded, and no sound should be played at any point during gameplay or game events.
**Validates: Requirements 11.1, 11.2, 11.3, 11.5**

## Error Handling

### Game Launch Errors

1. **Invalid Room Error**:
   - Condition: User attempts to launch game outside Arcade Room
   - Response: Display error message "Games are only available in the Arcade Room"
   - Recovery: User must navigate to Arcade Room first

2. **Invalid Game Name Error**:
   - Condition: User types `/play <invalid_name>`
   - Response: Display error message "Unknown game: {name}. Available games: snake, tetris, breakout"
   - Recovery: User can retry with valid game name

3. **Canvas Creation Error**:
   - Condition: Canvas element cannot be created or attached to DOM
   - Response: Display error message "Failed to initialize game. Please try again."
   - Recovery: Restore chat area, allow user to retry

### Game Runtime Errors

1. **Rendering Error**:
   - Condition: Canvas context is lost or rendering fails
   - Response: Terminate game gracefully, display error message
   - Recovery: Restore chat area, save high score if applicable

2. **Input Handler Error**:
   - Condition: Keyboard event listener fails
   - Response: Log error, continue game with degraded input handling
   - Recovery: Game remains playable with remaining input methods

3. **localStorage Error**:
   - Condition: localStorage is unavailable or quota exceeded
   - Response: Continue game without high score persistence, display warning
   - Recovery: Game remains fully playable, high scores not saved

### Room Transition Errors

1. **Cleanup Error**:
   - Condition: Game fails to terminate cleanly on room switch
   - Response: Force remove canvas and event listeners
   - Recovery: Ensure chat area is restored in new room

2. **State Restoration Error**:
   - Condition: Chat area fails to restore after game exit
   - Response: Reload page to reset UI state
   - Recovery: User session is preserved via JWT token

## Testing Strategy

### Unit Testing

**Framework**: Jest for JavaScript unit tests

**Test Coverage**:

1. **GameManager Tests**:
   - Game launch with valid game names
   - Game launch rejection outside Arcade Room
   - Canvas creation and removal
   - Room change handling
   - Exit command handling

2. **Individual Game Tests**:
   - Snake: Movement, collision detection, food spawning, scoring
   - Tetris: Piece movement, rotation, line clearing, game over
   - Breakout: Paddle movement, ball physics, brick collision, level completion

3. **HighScoreManager Tests**:
   - Score retrieval with no existing score
   - Score storage and retrieval
   - High score comparison logic
   - localStorage key formatting

4. **Command Handler Tests** (Backend):
   - `/play` command validation
   - Room restriction enforcement
   - Invalid game name handling
   - `/exit_game` command processing

### Property-Based Testing

**Framework**: fast-check for JavaScript property-based testing

**Configuration**: Each property test should run a minimum of 100 iterations

**Test Tagging**: Each property-based test must include a comment with the format:
`// Feature: arcade-room-games, Property {number}: {property_text}`

**Property Test Coverage**:

1. **Command Validation Properties**:
   - Property 1: Test with randomly generated room names (excluding Arcade Room)
   - Property 2: Test with randomly generated invalid game names

2. **UI State Properties**:
   - Property 4: Test with all three game names
   - Property 6: Test with randomly generated game states
   - Property 7: Test by sampling random canvas pixels

3. **Game Termination Properties**:
   - Property 8: Test with random game states and both exit methods
   - Property 10: Test by launching, playing, exiting, and re-launching with random actions
   - Property 11: Test with random room transitions during gameplay

4. **Snake Game Properties**:
   - Property 14: Test with random arrow key sequences
   - Property 15: Test with random snake positions and food locations
   - Property 16-17: Test with random collision scenarios

5. **Tetris Game Properties**:
   - Property 18-20: Test with random tetromino types and positions
   - Property 21: Test with randomly generated board states
   - Property 22: Test with random block stacking scenarios

6. **Breakout Game Properties**:
   - Property 23: Test with random paddle positions
   - Property 24-25: Test with random ball trajectories
   - Property 26-27: Test with random game states

7. **High Score Properties**:
   - Property 28: Test with randomly generated scores
   - Property 30: Test with all game names

8. **Performance Properties**:
   - Property 32: Test with random game states over time
   - Property 33: Test with random input timing

9. **Audio Properties**:
   - Property 34: Test throughout random game sessions

### Integration Testing

1. **End-to-End Game Flow**:
   - User in Lobby → Navigate to Arcade Room → Launch game → Play → Exit → Return to chat
   - User in Arcade Room → Launch game → Switch rooms → Verify game terminated → Return to Arcade Room

2. **Sidebar Integration**:
   - Click game launcher from different rooms
   - Verify room switch and game launch
   - Verify sidebar state updates

3. **High Score Persistence**:
   - Play game → Achieve score → Exit → Re-launch → Verify high score displayed
   - Clear localStorage → Launch game → Verify default high score (0)

4. **Multi-Game Session**:
   - Launch Snake → Exit → Launch Tetris → Exit → Launch Breakout → Exit
   - Verify each game starts fresh and high scores are independent

### Manual Testing Checklist

1. **Visual Verification**:
   - Verify monochrome aesthetic matches BBS style
   - Verify exit icon is visible and clickable
   - Verify game graphics are crisp and pixelated
   - Verify no color gradients or anti-aliasing

2. **Performance Verification**:
   - Play each game for 5+ minutes
   - Verify smooth frame rate (no stuttering)
   - Verify responsive input (no lag)

3. **Accessibility Verification**:
   - Verify keyboard-only navigation works
   - Verify high contrast mode compatibility
   - Verify reduced motion preferences respected

## Implementation Notes

### Canvas Rendering Optimization

1. **Double Buffering**: Use off-screen canvas for complex rendering to prevent flicker
2. **Dirty Rectangle**: Only redraw changed portions of canvas when possible
3. **RequestAnimationFrame**: Use RAF for smooth 60 FPS rendering with automatic throttling

### Input Handling Best Practices

1. **Event Delegation**: Attach keyboard listeners at document level, filter by game state
2. **Debouncing**: Prevent rapid repeated inputs from causing issues
3. **Key State Tracking**: Track key down/up states to handle held keys properly

### localStorage Best Practices

1. **Error Handling**: Wrap all localStorage operations in try-catch
2. **Quota Management**: High scores are small, but verify storage availability
3. **Data Validation**: Validate retrieved scores are valid numbers

### Game Loop Architecture

```javascript
class GameLoop {
    constructor(game) {
        this.game = game;
        this.lastFrameTime = 0;
        this.animationFrameId = null;
    }
    
    start() {
        this.lastFrameTime = performance.now();
        this.loop();
    }
    
    loop() {
        const currentTime = performance.now();
        const deltaTime = currentTime - this.lastFrameTime;
        this.lastFrameTime = currentTime;
        
        // Update game state
        this.game.update(deltaTime);
        
        // Render game
        this.game.render();
        
        // Continue loop if game is not over
        if (!this.game.isGameOver()) {
            this.animationFrameId = requestAnimationFrame(() => this.loop());
        }
    }
    
    stop() {
        if (this.animationFrameId) {
            cancelAnimationFrame(this.animationFrameId);
            this.animationFrameId = null;
        }
    }
}
```

### Memory Management

1. **Canvas Cleanup**: Remove canvas from DOM and null references
2. **Event Listener Cleanup**: Remove all event listeners on game exit
3. **Animation Frame Cleanup**: Cancel RAF on game termination
4. **Game Instance Cleanup**: Null game instance references to allow garbage collection

## Security Considerations

1. **Input Validation**: Validate all user inputs (commands, game names) on backend
2. **localStorage Limits**: High scores are user-specific and non-sensitive
3. **XSS Prevention**: No user-generated content rendered in games
4. **Resource Limits**: Games are lightweight and run client-side only

## Performance Targets

1. **Initial Load**: Game should launch within 200ms of command
2. **Frame Rate**: Maintain 30+ FPS during gameplay
3. **Input Latency**: Respond to input within 50ms
4. **Memory Usage**: Each game should use < 10MB of memory
5. **Code Size**: Each game module should be < 50KB minified

## Browser Compatibility

**Minimum Requirements**:
- Modern browsers with Canvas API support (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- JavaScript ES6+ support
- localStorage API support
- RequestAnimationFrame API support

**Graceful Degradation**:
- If Canvas API unavailable: Display error message, disable game features
- If localStorage unavailable: Games work but high scores not persisted
- If RAF unavailable: Fall back to setTimeout-based game loop

## Future Enhancements

1. **Additional Games**: Pong, Space Invaders, Pac-Man
2. **Difficulty Levels**: Easy/Medium/Hard modes for each game
3. **Leaderboards**: Server-side high score tracking across all users
4. **Game Replays**: Record and replay game sessions
5. **Multiplayer**: Two-player modes for competitive play
6. **Achievements**: Unlock badges for specific accomplishments
7. **Customization**: Allow users to customize game colors (within monochrome palette)
