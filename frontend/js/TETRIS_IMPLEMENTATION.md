# Tetris Game Implementation

## Overview

The Tetris game is a classic falling block puzzle game implemented in JavaScript using HTML Canvas. It follows the Game interface defined in `game.js` and integrates with the GameManager for lifecycle management.

## Requirements Fulfilled

- **7.1**: Display playing field with falling tetromino blocks
- **7.2**: Horizontal movement with left/right arrow keys
- **7.3**: Rotation with up arrow key and wall kick detection
- **7.4**: Soft drop acceleration with down arrow key
- **7.5**: Line clearing and gravity mechanics
- **7.6**: Game over detection when blocks stack above top
- **7.7**: Monochrome rendering with solid blocks

## Architecture

### Tetromino Shapes

The game implements all seven standard tetromino pieces:
- **I**: Straight line (4 blocks)
- **O**: Square (2x2 blocks)
- **T**: T-shape
- **S**: S-shape
- **Z**: Z-shape
- **J**: J-shape
- **L**: L-shape

Each piece has 4 rotation states stored as 2D arrays.

### Game Board

- 10 columns × 20 rows
- Represented as a 2D array
- Blocks are locked into the board when they land
- Board is centered on the canvas

### Game Mechanics

1. **Piece Movement**:
   - Left/Right: Move piece horizontally (Requirement 7.2)
   - Down: Soft drop (faster falling) (Requirement 7.4)
   - Up: Rotate clockwise (Requirement 7.3)

2. **Rotation System**:
   - 4 rotation states per piece
   - Wall kick detection: tries offsets (-1, 1, -2, 2) if basic rotation fails
   - Prevents rotation if no valid position found

3. **Line Clearing** (Requirement 7.5):
   - Checks for complete horizontal lines after each piece locks
   - Removes complete lines
   - Shifts blocks above downward (gravity)
   - Awards points based on lines cleared simultaneously

4. **Scoring**:
   - 1 point per soft drop move
   - 100 points for 1 line
   - 300 points for 2 lines
   - 500 points for 3 lines
   - 800 points for 4 lines (Tetris!)

5. **Progressive Difficulty**:
   - Level increases every 10 lines cleared
   - Drop speed increases with level
   - Starts at 1000ms, decreases by 100ms per level
   - Minimum drop interval: 100ms

6. **Game Over** (Requirement 7.6):
   - Triggered when a new piece cannot be placed at spawn position
   - Occurs when blocks stack above the top of the playing field

### Rendering

- **Monochrome Style** (Requirement 7.7):
  - Background: Pure black (#000000)
  - Foreground: Pure white (#FFFFFF)
  - Solid blocks without gradients or textures

- **UI Elements**:
  - Score display
  - Level display
  - Lines cleared counter
  - High score display
  - Next piece preview

### Game States

1. **Start Screen**:
   - Title and instructions
   - High score display
   - Waits for arrow key press to begin

2. **Playing**:
   - Active game loop
   - Piece falling and player control
   - Line clearing and scoring

3. **Game Over**:
   - Final score display
   - High score comparison
   - Exit prompt

## Integration

### With GameManager

The Tetris game is launched via:
```javascript
const { TetrisGame } = await import('./tetris.js');
const game = new TetrisGame(canvas, ctx);
```

### With High Score System

- Retrieves high score on start: `HighScoreManager.getHighScore('tetris')`
- Updates high score on game over if score is higher
- Stored in localStorage with key: `arcade_highscore_tetris`

## Testing

A standalone test file is provided at `test-tetris.html` for manual testing:
- Open in browser to test game independently
- Verify all controls work correctly
- Check line clearing mechanics
- Verify game over conditions
- Test rotation and wall kicks

## Key Implementation Details

### Collision Detection

The `isValidPosition()` method checks:
1. Piece is within board boundaries (left, right, bottom)
2. Piece doesn't overlap with locked blocks
3. Allows negative Y during spawning (pieces start above visible area)

### Wall Kicks

When rotation would place piece outside boundaries or into blocks:
1. Try basic rotation at current position
2. Try shifting left by 1, then right by 1
3. Try shifting left by 2, then right by 2
4. If all fail, rotation is cancelled

### Line Clearing Algorithm

1. Iterate through rows from bottom to top
2. Check if row is completely filled
3. If filled, remove row and add empty row at top
4. Re-check same row index (since rows shifted down)
5. Update score and level based on lines cleared

## Performance

- Uses requestAnimationFrame for smooth rendering
- Fixed time step for piece dropping
- Efficient collision detection (only checks piece blocks)
- Minimal canvas redraws (full clear + redraw each frame)

## Future Enhancements

Potential improvements (not in current requirements):
- Hard drop (instant drop to bottom)
- Hold piece functionality
- Ghost piece (preview of landing position)
- Different scoring systems (T-spin detection)
- Particle effects on line clear
- Multiple difficulty modes
