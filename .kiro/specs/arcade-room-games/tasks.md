# Implementation Plan

- [x] 1. Set up game infrastructure and core components





  - Create gameManager.js module with canvas management and game lifecycle
  - Create base Game class interface that all games will implement
  - Create highScores.js module for localStorage-based score persistence
  - Set up game loop architecture with requestAnimationFrame
  - _Requirements: 3.1, 3.2, 4.1, 4.2, 9.1, 9.2, 9.5_

- [ ]* 1.1 Write property test for game state not persisting
  - **Property 10: Game state not persisted**
  - **Validates: Requirements 4.5, 5.3**

- [x] 2. Extend command handler for game commands





  - Add /play command to backend command handler with game name validation
  - Add /exit_game command to backend command handler
  - Implement room restriction logic (games only in Arcade Room)
  - Add error responses for invalid game names and wrong rooms
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.2_

- [ ]* 2.1 Write property test for command validation
  - **Property 1: Game commands rejected outside Arcade Room**
  - **Validates: Requirements 1.4**

- [ ]* 2.2 Write property test for invalid game names
  - **Property 2: Invalid game names produce error**
  - **Validates: Requirements 1.5**

- [x] 3. Integrate game manager with main application





  - Import gameManager into main.js
  - Add message handler for "launch_game" WebSocket messages
  - Add message handler for "exit_game" commands
  - Implement room change detection to terminate active games
  - Wire up keyboard event routing to active game
  - _Requirements: 3.1, 4.1, 4.2, 5.1, 5.2, 5.5_

- [ ]* 3.1 Write property test for room switch termination
  - **Property 11: Room switch terminates game**
  - **Validates: Requirements 5.1**

- [ ]* 3.2 Write property test for game cleanup
  - **Property 13: Game cleanup on room switch**
  - **Validates: Requirements 5.5**

- [ ]* 3.3 Write property test for no auto-resume
  - **Property 12: No game auto-resume**
  - **Validates: Requirements 5.2**

- [x] 4. Implement canvas display and UI management





  - Create canvas element with proper dimensions matching chat area
  - Implement chat area hiding/showing logic
  - Add exit icon rendering in top-right corner of canvas
  - Implement exit icon click handler
  - Apply monochrome styling (black background, white foreground)
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.3, 4.4_

- [ ]* 4.1 Write property test for canvas replacement
  - **Property 4: Game launch replaces chat with canvas**
  - **Validates: Requirements 3.1**

- [ ]* 4.2 Write property test for exit icon presence
  - **Property 5: Exit icon present on all game canvases**
  - **Validates: Requirements 3.2**

- [ ]* 4.3 Write property test for chat hiding
  - **Property 6: Chat elements hidden during gameplay**
  - **Validates: Requirements 3.3**

- [ ]* 4.4 Write property test for monochrome rendering
  - **Property 7: Monochrome rendering**
  - **Validates: Requirements 3.5, 7.7, 8.7**

- [ ]* 4.5 Write property test for exit mechanisms
  - **Property 8: Exit mechanisms terminate game**
  - **Validates: Requirements 4.1, 4.2**

- [ ]* 4.6 Write property test for chat restoration
  - **Property 9: Chat restoration after game exit**
  - **Validates: Requirements 4.3, 4.4**

- [x] 5. Implement Snake game





  - Create snake.js module implementing Game interface
  - Implement grid-based snake movement with direction control
  - Implement food spawning and collision detection
  - Implement snake growth mechanics
  - Implement wall and self-collision detection
  - Implement scoring system
  - Render snake and food on canvas with monochrome graphics
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 5.1 Write property test for snake movement
  - **Property 14: Snake arrow key movement**
  - **Validates: Requirements 6.2**

- [ ]* 5.2 Write property test for food collision
  - **Property 15: Snake food collision**
  - **Validates: Requirements 6.3**

- [ ]* 5.3 Write property test for wall collision
  - **Property 16: Snake wall collision ends game**
  - **Validates: Requirements 6.4**

- [ ]* 5.4 Write property test for self-collision
  - **Property 17: Snake self-collision ends game**
  - **Validates: Requirements 6.5**

- [x] 6. Implement Tetris game





  - Create tetris.js module implementing Game interface
  - Define seven tetromino shapes (I, O, T, S, Z, J, L)
  - Implement piece movement (left, right, down)
  - Implement piece rotation with wall kick detection
  - Implement line clearing and gravity mechanics
  - Implement progressive speed increase
  - Implement game over detection (blocks above top)
  - Render playing field and pieces with solid monochrome blocks
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [ ]* 6.1 Write property test for horizontal movement
  - **Property 18: Tetris horizontal movement**
  - **Validates: Requirements 7.2**

- [ ]* 6.2 Write property test for rotation
  - **Property 19: Tetris rotation**
  - **Validates: Requirements 7.3**

- [ ]* 6.3 Write property test for soft drop
  - **Property 20: Tetris soft drop**
  - **Validates: Requirements 7.4**

- [ ]* 6.4 Write property test for line clearing
  - **Property 21: Tetris line clearing**
  - **Validates: Requirements 7.5**

- [ ]* 6.5 Write property test for game over
  - **Property 22: Tetris game over condition**
  - **Validates: Requirements 7.6**

- [x] 7. Implement Breakout game





  - Create breakout.js module implementing Game interface
  - Implement paddle movement with boundary constraints
  - Implement ball physics with angle-based bouncing
  - Implement brick grid generation
  - Implement ball-brick collision detection and destruction
  - Implement ball-paddle collision with direction modification
  - Implement ball miss detection (game over)
  - Implement level completion detection (all bricks destroyed)
  - Render paddle, ball, and bricks with monochrome graphics
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

- [ ]* 7.1 Write property test for paddle movement
  - **Property 23: Breakout paddle movement**
  - **Validates: Requirements 8.2**

- [ ]* 7.2 Write property test for brick collision
  - **Property 24: Breakout brick collision**
  - **Validates: Requirements 8.3**

- [ ]* 7.3 Write property test for paddle collision
  - **Property 25: Breakout paddle collision**
  - **Validates: Requirements 8.4**

- [ ]* 7.4 Write property test for ball miss
  - **Property 26: Breakout ball miss ends game**
  - **Validates: Requirements 8.5**

- [ ]* 7.5 Write property test for level completion
  - **Property 27: Breakout level completion**
  - **Validates: Requirements 8.6**

- [x] 8. Implement high score system





  - Implement high score retrieval from localStorage
  - Implement high score comparison on game end
  - Implement high score update in localStorage
  - Display high score on game start screen
  - Handle missing high scores (default to 0)
  - Use game-specific localStorage keys
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [ ]* 8.1 Write property test for high score comparison
  - **Property 28: High score comparison**
  - **Validates: Requirements 9.1, 9.2**

- [ ]* 8.2 Write property test for high score display
  - **Property 29: High score display**
  - **Validates: Requirements 9.3**

- [ ]* 8.3 Write property test for storage keys
  - **Property 30: High score storage keys**
  - **Validates: Requirements 9.5**

- [x] 9. Extend sidebar with game launchers





  - Modify sidePanel.js to render collapsible sub-items under Arcade Room
  - Add three sub-items: Snake, Tetris, Breakout
  - Implement click handlers for each game launcher
  - Implement auto-switch to Arcade Room when clicking from other rooms
  - Update sidebar styling to match retro aesthetic
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 9.1 Write property test for sidebar game launch
  - **Property 3: Sidebar game launch from any room**
  - **Validates: Requirements 2.5**

- [ ] 10. Implement performance optimizations





  - Ensure keyboard-only input (ignore mouse/touch for game controls)
  - Optimize game loop to maintain 30+ FPS
  - Implement input debouncing for responsive controls
  - Measure and optimize input latency to < 50ms
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ]* 10.1 Write property test for keyboard-only input
  - **Property 31: Keyboard-only input**
  - **Validates: Requirements 10.1**

- [ ]* 10.2 Write property test for frame rate
  - **Property 32: Minimum frame rate**
  - **Validates: Requirements 10.2**

- [ ]* 10.3 Write property test for input responsiveness
  - **Property 33: Input responsiveness**
  - **Validates: Requirements 10.4**


- [x] 11. Ensure complete silence (no audio)



  - Verify no audio elements are created in any game code
  - Verify no audio files are loaded or referenced
  - Verify no sound playback occurs during gameplay or events
  - Add code comments documenting the silent design requirement
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

- [ ]* 11.1 Write property test for complete silence
  - **Property 34: Complete silence**
  - **Validates: Requirements 11.1, 11.2, 11.3, 11.5**

- [x] 12. Add error handling and edge cases





  - Handle canvas creation failures gracefully
  - Handle localStorage unavailability (games work, scores not saved)
  - Handle rendering errors (terminate game, restore chat)
  - Handle cleanup errors on room transitions
  - Add try-catch blocks around critical operations
  - _Requirements: All requirements (error handling)_

- [x] 13. Checkpoint - Ensure all tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Manual testing and polish
  - Test all three games end-to-end
  - Verify monochrome aesthetic matches BBS style
  - Verify smooth performance across all games
  - Test room switching during gameplay
  - Test high score persistence across sessions
  - Verify exit mechanisms work correctly
  - Test sidebar game launchers from different rooms
  - _Requirements: All requirements (integration testing)_
 