# Implementation Plan: Core Terminal Chat + Rooms

- [x] 1. Set up project structure and dependencies





  - Create backend and frontend directory structure
  - Initialize Python virtual environment
  - Create requirements.txt with FastAPI, uvicorn, passlib, python-jose, sqlalchemy, aiosqlite, hypothesis, pytest
  - Create .env.example file with configuration template
  - Set up .gitignore for Python and environment files
  - _Requirements: All_

- [x] 2. Implement database models and connection





  - Create database.py with SQLAlchemy setup for SQLite
  - Define User model with id, username, password_hash, created_at, last_login fields
  - Define Session model with id, user_id, token, created_at, expires_at fields
  - Create database initialization function
  - Add indexes for username and token lookups
  - _Requirements: 1.4, 1.6, 2.2_

- [ ]* 2.1 Write property test for username validation
  - **Property 1: Username validation**
  - **Validates: Requirements 1.4**

- [ ]* 2.2 Write property test for password validation
  - **Property 2: Password validation**
  - **Validates: Requirements 1.5**

- [x] 3. Implement authentication service





  - Create auth/service.py with AuthService class
  - Implement password hashing using bcrypt (cost factor 12)
  - Implement password verification
  - Implement username validation (3-20 characters, unique check)
  - Implement password validation (minimum 8 characters)
  - Implement JWT token generation with user ID and username
  - Implement JWT token validation
  - _Requirements: 1.4, 1.5, 1.6, 2.2, 2.3_

- [ ]* 3.1 Write property test for successful registration
  - **Property 3: Successful registration creates account and session**
  - **Validates: Requirements 1.6**

- [ ]* 3.2 Write property test for valid credentials authentication
  - **Property 4: Valid credentials authenticate successfully**
  - **Validates: Requirements 2.2**

- [ ]* 3.3 Write property test for invalid credentials retry
  - **Property 5: Invalid credentials allow retry**
  - **Validates: Requirements 2.3**

- [ ]* 3.4 Write property test for welcome message format
  - **Property 6: Welcome message contains required information**
  - **Validates: Requirements 2.5**

- [x] 4. Create authentication HTTP endpoints





  - Create main.py with FastAPI app initialization
  - Implement POST /api/auth/register endpoint
  - Implement POST /api/auth/login endpoint
  - Add request/response models using Pydantic
  - Implement error handling for duplicate usernames
  - Implement error handling for validation failures
  - Track failed login attempts (max 3 per connection)
  - _Requirements: 1.4, 1.5, 1.6, 1.7, 2.2, 2.3, 2.4, 2.5_

- [ ]* 4.1 Write unit tests for authentication endpoints
  - Test successful registration flow
  - Test duplicate username rejection
  - Test invalid username/password validation
  - Test successful login flow
  - Test invalid credentials handling
  - Test failed login attempt tracking
  - _Requirements: 1.4, 1.5, 1.6, 1.7, 2.2, 2.3, 2.4_

- [x] 5. Implement room service and models







  - Create rooms/service.py with RoomService class
  - Define Room model with name, description, users set
  - Implement create_default_rooms() for Lobby, Techline, Arcade Hall, Archives
  - Implement get_rooms() to list all rooms
  - Implement join_room() to add user to room
  - Implement leave_room() to remove user from room
  - Implement get_users_in_room() to list room members
  - Implement get_room_count() to count users in room
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ]* 5.1 Write property test for users starting in Lobby
  - **Property 7: Authenticated users start in Lobby**
  - **Validates: Requirements 4.2**

- [ ]* 5.2 Write property test for room changes
  - **Property 8: Room changes update user location**
  - **Validates: Requirements 4.3**

- [ ]* 5.3 Write property test for room entry display
  - **Property 9: Room entry displays room information**
  - **Validates: Requirements 4.4**

- [x] 6. Implement WebSocket manager





  - Create websocket/manager.py with WebSocketManager class
  - Implement connect() to handle new WebSocket connections
  - Implement disconnect() to clean up closed connections
  - Implement send_to_user() to send message to specific user
  - Implement broadcast_to_room() to send message to all users in room
  - Implement broadcast_to_all() to send message to all connected users
  - Maintain active_connections dict mapping WebSocket to ActiveUser
  - Maintain user_websockets dict mapping username to WebSocket
  - _Requirements: 5.1, 5.2, 6.1, 6.2, 6.3_

- [ ]* 6.1 Write property test for message isolation
  - **Property 10: Message isolation by room**
  - **Validates: Requirements 4.5**

- [ ]* 6.2 Write property test for message broadcasting
  - **Property 11: Messages broadcast to room members**
  - **Validates: Requirements 5.2**

- [ ]* 6.3 Write property test for message format
  - **Property 12: Message format includes required fields**
  - **Validates: Requirements 5.3, 9.2**

- [x] 7. Implement command handler





  - Create commands/handler.py with CommandHandler class
  - Implement handle_command() to route commands
  - Implement help_command() to return list of available commands
  - Implement rooms_command() to return room list with user counts
  - Implement users_command() to return active users list
  - Implement clear_command() to return clear signal
  - Implement join_command() to handle room switching
  - Implement error handling for invalid commands
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 7.1 Write property test for rooms command
  - **Property 20: Rooms command shows all rooms with counts**
  - **Validates: Requirements 7.2**

- [ ]* 7.2 Write property test for users command
  - **Property 21: Users command shows active users**
  - **Validates: Requirements 7.3**

- [ ]* 7.3 Write property test for invalid commands
  - **Property 22: Invalid commands return error**
  - **Validates: Requirements 7.5**

- [x] 8. Implement WebSocket endpoint and message handling





  - Create WebSocket endpoint at /ws with token authentication
  - Implement token validation on connection
  - Implement welcome message on successful connection
  - Implement message routing (chat_message, command, join_room types)
  - Implement automatic user placement in Lobby on connect
  - Implement user removal from rooms on disconnect
  - Implement session state preservation for 30 seconds after disconnect
  - Implement reconnection logic to restore previous room
  - _Requirements: 4.2, 5.1, 5.2, 6.1, 6.2, 8.1, 8.3, 8.4, 8.5_

- [ ]* 8.1 Write property test for user added to active list
  - **Property 15: User added to active list on connection**
  - **Validates: Requirements 6.1**

- [ ]* 8.2 Write property test for user removed on disconnect
  - **Property 16: User removed from active list on disconnection**
  - **Validates: Requirements 6.2**

- [ ]* 8.3 Write property test for active list broadcast
  - **Property 17: Active list changes broadcast to all**
  - **Validates: Requirements 6.3**

- [ ]* 8.4 Write property test for active list format
  - **Property 18: Active list shows username and room**
  - **Validates: Requirements 6.4**

- [ ]* 8.5 Write property test for room change updates active list
  - **Property 19: Room changes update active list**
  - **Validates: Requirements 6.5**

- [ ]* 8.6 Write property test for welcome message on connect
  - **Property 23: Connection sends welcome message**
  - **Validates: Requirements 8.1**

- [ ]* 8.7 Write property test for session state preservation
  - **Property 25: Disconnection preserves session state**
  - **Validates: Requirements 8.3**

- [ ]* 8.8 Write property test for reconnection restores room
  - **Property 26: Reconnection restores previous room**
  - **Validates: Requirements 8.4**

- [ ]* 8.9 Write property test for session expiration cleanup
  - **Property 27: Session expiration removes user**
  - **Validates: Requirements 8.5**

- [x] 9. Checkpoint - Ensure all backend tests pass





  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Create frontend HTML structure





  - Create frontend/index.html with semantic structure
  - Add meta tags for charset and viewport
  - Create terminal-screen container div
  - Create chat-display area for messages
  - Create command-line-bar section at bottom
  - Add input field with blinking cursor
  - Include optional Tailwind CSS via CDN if needed for layout
  - _Requirements: 3.3, 7.4, 9.1_

- [x] 11. Implement CSS for CRT terminal effects





  - Create frontend/css/terminal.css
  - Implement CRT curvature using perspective transform
  - Implement scanlines using linear-gradient overlay
  - Implement phosphor glow using text-shadow (green #33ff33)
  - Implement flicker animation with subtle opacity changes
  - Implement green monochrome color scheme
  - Add retro terminal font (e.g., VT323, Courier New)
  - Style command line bar with fixed bottom position
  - Style blinking cursor animation
  - _Requirements: 3.1, 3.2, 3.4, 3.5_

- [x] 12. Implement command line bar component





  - Create frontend/js/commandBar.js
  - Implement CommandLineBar class
  - Implement input event handling
  - Implement command history with up/down arrow navigation
  - Implement Enter key to submit input
  - Implement input clearing after submission
  - Implement cursor blinking animation
  - Distinguish between commands (starting with /) and regular messages
  - _Requirements: 3.3, 3.4, 5.4, 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 12.1 Write property test for input cleared after send
  - **Property 13: Message submission clears input**
  - **Validates: Requirements 5.4**

- [x] 13. Implement chat display component





  - Create frontend/js/chatDisplay.js
  - Implement ChatDisplay class
  - Implement addMessage() to append new messages
  - Implement message formatting with timestamp and username
  - Implement auto-scroll to latest message
  - Implement different styling for system messages
  - Implement clear() function for /clear command
  - Format timestamps as [HH:MM:SS]
  - Format messages as "[HH:MM:SS] <username> message"
  - _Requirements: 5.3, 7.4, 9.2, 9.4, 9.5_

- [x] 14. Implement WebSocket client





  - Create frontend/js/websocket.js
  - Implement WebSocketClient class
  - Implement connect() with JWT token from localStorage
  - Implement disconnect() to close connection
  - Implement send() to send JSON messages
  - Implement onMessage() callback registration
  - Implement automatic reconnection with exponential backoff
  - Implement connection status notifications
  - Handle connection errors with retry (up to 3 times)
  - _Requirements: 5.1, 5.5, 8.2_

- [ ]* 14.1 Write property test for WebSocket reconnection
  - **Property 14: WebSocket reconnection on interruption**
  - **Validates: Requirements 5.5**

- [ ]* 14.2 Write property test for connection retry
  - **Property 24: Connection failure triggers retry**
  - **Validates: Requirements 8.2**

- [x] 15. Implement main application logic





  - Create frontend/js/main.js
  - Initialize WebSocketClient with token
  - Initialize CommandLineBar with message/command handlers
  - Initialize ChatDisplay
  - Implement message handler to route incoming WebSocket messages
  - Implement chat_message handler to display messages
  - Implement system message handler
  - Implement user_list handler to update active users display
  - Implement room_list handler for /rooms command
  - Implement error handler to display errors
  - Connect command bar submission to WebSocket send
  - _Requirements: 5.1, 5.2, 5.3, 6.3, 6.4, 7.1, 7.2, 7.3, 7.5, 9.3_

- [x] 16. Create login/registration UI






  - Create frontend/auth.html for login/registration page
  - Implement dial-up connection sequence animation with ASCII art
  - Create login form with username and password fields
  - Create registration form with username and password fields
  - Style forms with terminal aesthetic
  - Implement form submission handlers
  - Call /api/auth/login or /api/auth/register endpoints
  - Store JWT token in localStorage on success
  - Redirect to main terminal UI (index.html) after authentication
  - Display error messages for failed attempts
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 17. Implement rate limiting





  - Add rate limiting middleware to FastAPI
  - Implement message rate limit: 10 messages per 10 seconds per user
  - Implement command rate limit: 5 commands per 5 seconds per user
  - Send warning message on first violation
  - Implement temporary mute (30 seconds) on repeated violations
  - Disconnect user on persistent abuse
  - _Requirements: 5.1_

- [ ] 18. Add CORS configuration
  - Configure CORS middleware in FastAPI
  - Allow origins from environment variable
  - Allow credentials for WebSocket connections
  - Set appropriate headers for development and production
  - _Requirements: All (infrastructure)_

- [ ] 19. Create static file serving
  - Configure FastAPI to serve static files from frontend directory
  - Mount /static route for CSS, JS, and assets
  - Serve index.html at root path /
  - Serve auth.html at /auth path
  - _Requirements: All (infrastructure)_

- [ ] 20. Implement configuration management
  - Create config.py for environment variable loading
  - Load DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_HOURS
  - Load CORS_ORIGINS from environment
  - Provide sensible defaults for development
  - Add validation for required configuration
  - _Requirements: All (infrastructure)_

- [ ] 21. Final checkpoint - Integration testing
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 21.1 Write integration test for full authentication flow
  - Test register → login → WebSocket connect sequence
  - Verify token generation and validation
  - Verify user placement in Lobby
  - _Requirements: 1.6, 2.2, 4.2, 8.1_

- [ ]* 21.2 Write integration test for room switching
  - Test joining different rooms
  - Verify message isolation between rooms
  - Verify active user list updates
  - _Requirements: 4.3, 4.5, 6.5_

- [ ]* 21.3 Write integration test for multi-user chat
  - Test multiple users in same room
  - Verify message broadcasting
  - Verify active user list synchronization
  - _Requirements: 5.2, 6.3_

- [ ]* 21.4 Write integration test for command execution
  - Test /help, /rooms, /users, /clear commands
  - Verify correct responses
  - Verify invalid command handling
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 21.5 Write integration test for connection handling
  - Test disconnect and reconnect flow
  - Verify session state preservation
  - Verify room restoration
  - _Requirements: 8.3, 8.4, 8.5_

- [ ] 22. Create README documentation
  - Document project overview and features
  - Document installation instructions
  - Document how to run the application
  - Document environment variable configuration
  - Document API endpoints
  - Document WebSocket message format
  - Document available commands
  - _Requirements: All (documentation)_

- [ ] 23. Create example environment file
  - Create .env.example with all required variables
  - Add comments explaining each variable
  - Provide example values for development
  - Document production considerations
  - _Requirements: All (infrastructure)_
