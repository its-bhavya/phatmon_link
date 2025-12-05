# Design Document: Core Terminal Chat + Rooms

## Overview

Obsidian BBS's Core Terminal Chat + Rooms feature provides a modern BBS experience with retro aesthetics. The system uses a FastAPI backend for real-time WebSocket communication and user management, paired with a vanilla HTML/CSS/JS frontend (with optional Tailwind for layout utilities) that renders an authentic terminal interface with CRT effects.

The architecture separates concerns into three main layers:
1. **Frontend**: Terminal UI rendering, user input handling, WebSocket client
2. **Backend**: FastAPI server with WebSocket support, authentication, room management
3. **Data Layer**: User accounts, sessions, chat history, room state

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser Client                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Terminal UI (HTML/CSS/JS)                             │ │
│  │  - CRT Effects & ANSI Rendering                        │ │
│  │  - Command Line Bar                                    │ │
│  │  - Chat Display                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                           │                                  │
│                           │ WebSocket                        │
│                           ▼                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                    FastAPI Backend                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  WebSocket Manager                                     │ │
│  │  - Connection handling                                 │ │
│  │  - Message broadcasting                                │ │
│  │  - Room management                                     │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Authentication Service                                │ │
│  │  - User registration                                   │ │
│  │  - Login validation                                    │ │
│  │  - Session management                                  │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Room Service                                          │ │
│  │  - Room state management                               │ │
│  │  - User-room associations                              │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Data Layer                              │
│  - SQLite database (users, sessions)                        │
│  - In-memory state (active connections, rooms)              │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- HTML5 for structure
- CSS3 for CRT effects (scanlines, glow, curvature)
- Vanilla JavaScript for logic and WebSocket client
- Optional: Tailwind CSS for layout utilities only
- No heavy frameworks (React, Vue, etc.)

**Backend:**
- Python 3.11+
- FastAPI for HTTP and WebSocket endpoints
- Uvicorn as ASGI server
- SQLite for persistent storage
- Passlib for password hashing (bcrypt)
- Python-jose for JWT tokens

**Communication:**
- WebSocket for real-time bidirectional messaging
- JSON for message serialization

## Components and Interfaces

### Frontend Components

#### 1. Terminal UI Renderer
Responsible for rendering the retro terminal aesthetic with CRT effects.

**Key Features:**
- ANSI-style text rendering with green monochrome theme
- CRT monitor emulation: slight curvature, scanlines, subtle flicker, phosphor glow
- Optional screen distortion for "haunted events" (color inversion, static overlays)
- Responsive canvas or CSS-based rendering

**CSS Effects:**
```css
/* CRT curvature using perspective */
.terminal-screen {
  perspective: 1000px;
  transform: rotateX(1deg);
}

/* Scanlines overlay */
.scanlines {
  background: linear-gradient(
    transparent 50%,
    rgba(0, 0, 0, 0.25) 50%
  );
  background-size: 100% 4px;
}

/* Phosphor glow */
.terminal-text {
  color: #33ff33;
  text-shadow: 0 0 5px #33ff33, 0 0 10px #33ff33;
}

/* Flicker animation */
@keyframes flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.97; }
}
```

#### 2. Command Line Bar
Fixed at the bottom of the screen, accepts user input.

**Features:**
- Blinking cursor animation
- Command history (up/down arrow keys)
- Auto-complete for commands
- Visual feedback on input
- Supports both commands (/) and regular messages

**Interface:**
```javascript
class CommandLineBar {
  constructor(onSubmit, onCommand);
  handleInput(event);
  clearInput();
  showCursor();
  addToHistory(text);
  getHistory();
}
```

#### 3. Chat Display
Renders messages with timestamps and usernames.

**Features:**
- Auto-scroll to latest message
- Message formatting with ANSI colors
- Timestamp display
- Username highlighting
- System message styling (different color)

**Message Format:**
```
[HH:MM:SS] <username> message text
[HH:MM:SS] * SYSTEM: system message
```

#### 4. WebSocket Client
Manages connection to backend and message handling.

**Interface:**
```javascript
class WebSocketClient {
  constructor(url);
  connect();
  disconnect();
  send(message);
  onMessage(callback);
  onConnect(callback);
  onDisconnect(callback);
  reconnect();
}
```

**Message Types:**
```javascript
// Client -> Server
{
  type: "chat_message",
  content: "Hello world",
  room: "lobby"
}

{
  type: "command",
  command: "rooms"
}

{
  type: "join_room",
  room: "techline"
}

// Server -> Client
{
  type: "chat_message",
  username: "user123",
  content: "Hello world",
  timestamp: "2025-11-30T12:34:56Z",
  room: "lobby"
}

{
  type: "user_list",
  users: [
    { username: "user123", room: "lobby" },
    { username: "user456", room: "techline" }
  ]
}

{
  type: "room_list",
  rooms: [
    { name: "Lobby", count: 5 },
    { name: "Techline", count: 2 }
  ]
}

{
  type: "system",
  content: "Welcome to Obsidian BBS"
}

{
  type: "error",
  content: "Invalid command"
}
```

### Backend Components

#### 1. Authentication Service
Handles user registration, login, and session management.

**Interface:**
```python
class AuthService:
    def register_user(username: str, password: str) -> User
    def authenticate_user(username: str, password: str) -> Optional[User]
    def create_session(user: User) -> str  # Returns JWT token
    def validate_session(token: str) -> Optional[User]
    def hash_password(password: str) -> str
    def verify_password(plain: str, hashed: str) -> bool
```

**User Model:**
```python
class User:
    id: int
    username: str
    password_hash: str
    created_at: datetime
    last_login: datetime
```

#### 2. WebSocket Manager
Manages WebSocket connections, message routing, and broadcasting.

**Interface:**
```python
class WebSocketManager:
    def connect(websocket: WebSocket, user: User) -> None
    def disconnect(websocket: WebSocket) -> None
    def broadcast_to_room(room: str, message: dict) -> None
    def broadcast_to_all(message: dict) -> None
    def send_to_user(websocket: WebSocket, message: dict) -> None
    def get_active_users() -> List[ActiveUser]
    def handle_message(websocket: WebSocket, message: dict) -> None
```

**Connection State:**
```python
class ActiveUser:
    websocket: WebSocket
    user: User
    current_room: str
    connected_at: datetime
```

#### 3. Room Service
Manages room state and user-room associations.

**Interface:**
```python
class RoomService:
    def create_default_rooms() -> None
    def get_rooms() -> List[Room]
    def get_room(name: str) -> Optional[Room]
    def join_room(user: User, room_name: str) -> None
    def leave_room(user: User, room_name: str) -> None
    def get_users_in_room(room_name: str) -> List[User]
    def get_room_count(room_name: str) -> int
```

**Room Model:**
```python
class Room:
    name: str
    description: str
    created_at: datetime
    users: Set[str]  # Set of usernames
```

**Default Rooms:**
- **Lobby**: Main gathering space, default entry point
- **Techline**: Technology and programming discussions
- **Arcade Hall**: Gaming and entertainment

#### 4. Command Handler
Processes user commands and returns appropriate responses.

**Interface:**
```python
class CommandHandler:
    def handle_command(command: str, user: User) -> dict
    def help_command() -> dict
    def rooms_command() -> dict
    def users_command() -> dict
    def clear_command() -> dict
    def join_command(room_name: str, user: User) -> dict
```

### FastAPI Endpoints

#### HTTP Endpoints

```python
# Authentication
POST /api/auth/register
  Body: { username: str, password: str }
  Returns: { token: str, user: User }

POST /api/auth/login
  Body: { username: str, password: str }
  Returns: { token: str, user: User, last_login: datetime }

# Static files
GET /
  Returns: index.html (main terminal UI)

GET /static/*
  Returns: CSS, JS, assets
```

#### WebSocket Endpoint

```python
WS /ws
  Query params: token (JWT)
  
  # Connection flow:
  1. Client connects with JWT token
  2. Server validates token
  3. Server adds user to active connections
  4. Server sends welcome message
  5. Server broadcasts user join to room
  6. Bidirectional message exchange begins
  7. On disconnect, server removes user and broadcasts leave
```

## Data Models

### Database Schema (SQLite)

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Sessions table (optional, for persistent sessions)
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    token TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Indexes
CREATE INDEX idx_username ON users(username);
CREATE INDEX idx_token ON sessions(token);
```

### In-Memory State

```python
# Active connections
active_connections: Dict[WebSocket, ActiveUser] = {}

# Room state
rooms: Dict[str, Room] = {
    "lobby": Room(name="Lobby", description="Main gathering space", users=set()),
    "techline": Room(name="Techline", description="Tech discussions", users=set()),
    "arcade_hall": Room(name="Arcade Hall", description="Gaming zone", users=set())
}

# User to WebSocket mapping
user_websockets: Dict[str, WebSocket] = {}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Username validation
*For any* registration attempt, the system should accept usernames that are unique and between 3 and 20 characters, and reject all others.
**Validates: Requirements 1.4**

### Property 2: Password validation
*For any* password submission during registration, the system should accept passwords that are at least 8 characters long and reject shorter passwords.
**Validates: Requirements 1.5**

### Property 3: Successful registration creates account and session
*For any* valid registration credentials (unique username 3-20 chars, password 8+ chars), the system should create a user account and establish an authenticated session.
**Validates: Requirements 1.6**

### Property 4: Valid credentials authenticate successfully
*For any* user with valid stored credentials, submitting those credentials should result in successful authentication and session establishment.
**Validates: Requirements 2.2**

### Property 5: Invalid credentials allow retry
*For any* invalid credential submission, the system should display an error and allow retry, up to a maximum of 3 attempts.
**Validates: Requirements 2.3**

### Property 6: Welcome message contains required information
*For any* successful authentication, the welcome message should contain the username and last login timestamp.
**Validates: Requirements 2.5**

### Property 7: Authenticated users start in Lobby
*For any* authenticated user entering the system, the user should be placed in the Lobby room.
**Validates: Requirements 4.2**

### Property 8: Room changes update user location
*For any* authenticated user requesting to change to a valid room, the system should move the user to that room and notify other users in both the old and new rooms.
**Validates: Requirements 4.3**

### Property 9: Room entry displays room information
*For any* authenticated user entering a room, the system should display the room name and description.
**Validates: Requirements 4.4**

### Property 10: Message isolation by room
*For any* authenticated user in a specific room, the user should only receive messages sent to that room, not messages from other rooms.
**Validates: Requirements 4.5**

### Property 11: Messages broadcast to room members
*For any* chat message received by the server, the system should broadcast that message to all authenticated users currently in the same room.
**Validates: Requirements 5.2**

### Property 12: Message format includes required fields
*For any* displayed chat message, the message should include the sender username, timestamp, and message content.
**Validates: Requirements 5.3, 9.2**

### Property 13: Message submission clears input
*For any* authenticated user sending a chat message, the command line bar should be cleared after submission.
**Validates: Requirements 5.4**

### Property 14: WebSocket reconnection on interruption
*For any* WebSocket connection interruption, the system should attempt to reconnect automatically and notify the user of connection status.
**Validates: Requirements 5.5**

### Property 15: User added to active list on connection
*For any* authenticated user connecting to the system, the user should be added to the Active Users List.
**Validates: Requirements 6.1**

### Property 16: User removed from active list on disconnection
*For any* authenticated user disconnecting from the system, the user should be removed from the Active Users List.
**Validates: Requirements 6.2**

### Property 17: Active list changes broadcast to all
*For any* change to the Active Users List, the updated list should be broadcast to all connected authenticated users.
**Validates: Requirements 6.3**

### Property 18: Active list shows username and room
*For any* entry in the Active Users List, the entry should display the username and current room.
**Validates: Requirements 6.4**

### Property 19: Room changes update active list
*For any* authenticated user changing rooms, the Active Users List should be updated to reflect the new room assignment.
**Validates: Requirements 6.5**

### Property 20: Rooms command shows all rooms with counts
*For any* authenticated user executing the "/rooms" command, the system should display all available rooms with their current user counts.
**Validates: Requirements 7.2**

### Property 21: Users command shows active users
*For any* authenticated user executing the "/users" command, the system should display the Active Users List with usernames and room assignments.
**Validates: Requirements 7.3**

### Property 22: Invalid commands return error
*For any* unrecognized command entered by an authenticated user, the system should display an error message indicating the command is invalid.
**Validates: Requirements 7.5**

### Property 23: Connection sends welcome message
*For any* authenticated user establishing a WebSocket connection, the system should send a welcome message to that user.
**Validates: Requirements 8.1**

### Property 24: Connection failure triggers retry
*For any* WebSocket connection failure, the system should display an error message and retry up to 3 times.
**Validates: Requirements 8.2**

### Property 25: Disconnection preserves session state
*For any* authenticated user whose WebSocket connection drops, the system should maintain the user's session state for 30 seconds to allow reconnection.
**Validates: Requirements 8.3**

### Property 26: Reconnection restores previous room
*For any* authenticated user reconnecting within the timeout period, the system should restore the user to their previous room.
**Validates: Requirements 8.4**

### Property 27: Session expiration removes user
*For any* authenticated user whose session expires, the system should remove the user from all rooms and the Active Users List.
**Validates: Requirements 8.5**

## Error Handling

### Authentication Errors

**Invalid Credentials:**
- Return 401 Unauthorized with clear error message
- Track failed attempts per connection
- Disconnect after 3 failed attempts

**Duplicate Username:**
- Return 400 Bad Request with specific error
- Suggest alternative usernames (optional enhancement)

**Validation Errors:**
- Return 400 Bad Request with field-specific errors
- Username: "Username must be 3-20 characters"
- Password: "Password must be at least 8 characters"

### WebSocket Errors

**Connection Failures:**
- Client-side: Display error overlay with retry countdown
- Automatic retry with exponential backoff (1s, 2s, 4s)
- After 3 failures, prompt user to refresh

**Invalid Token:**
- Close WebSocket with code 4001
- Redirect to login screen
- Clear local session data

**Message Parsing Errors:**
- Log error server-side
- Send error message to client
- Continue connection (don't disconnect)

**Room Not Found:**
- Send error message: "Room '{name}' does not exist"
- Keep user in current room
- Suggest available rooms

### Rate Limiting

**Message Flooding:**
- Limit: 10 messages per 10 seconds per user
- On exceed: Send warning, then temporary mute (30 seconds)
- Persistent abuse: Disconnect user

**Command Spam:**
- Limit: 5 commands per 5 seconds per user
- On exceed: Send error message, ignore excess commands

### Database Errors

**Connection Failures:**
- Log error with full context
- Return 503 Service Unavailable
- Retry with exponential backoff

**Constraint Violations:**
- Catch unique constraint errors (duplicate username)
- Return user-friendly error messages
- Don't expose internal database details

## Testing Strategy

### Unit Testing

**Framework:** pytest for Python backend

**Coverage Areas:**
- Authentication service: password hashing, validation, token generation
- Room service: room creation, user assignment, state management
- Command handler: command parsing, response generation
- Message formatting: timestamp formatting, username display

**Example Unit Tests:**
```python
def test_password_hashing():
    """Test that passwords are hashed and can be verified"""
    service = AuthService()
    hashed = service.hash_password("testpass123")
    assert service.verify_password("testpass123", hashed)
    assert not service.verify_password("wrongpass", hashed)

def test_username_validation():
    """Test username length validation"""
    service = AuthService()
    assert service.validate_username("abc")  # 3 chars, valid
    assert service.validate_username("a" * 20)  # 20 chars, valid
    assert not service.validate_username("ab")  # 2 chars, invalid
    assert not service.validate_username("a" * 21)  # 21 chars, invalid

def test_room_user_assignment():
    """Test that users are correctly assigned to rooms"""
    room_service = RoomService()
    user = User(id=1, username="test")
    room_service.join_room(user, "lobby")
    assert "test" in room_service.get_users_in_room("lobby")
```

### Property-Based Testing

**Framework:** Hypothesis for Python

**Configuration:** Each property test should run a minimum of 100 iterations.

**Test Tagging:** Each property-based test must include a comment with the format:
`# Feature: core-terminal-chat, Property {number}: {property_text}`

**Coverage Areas:**

1. **Authentication Properties:**
   - Property 1: Username validation
   - Property 2: Password validation
   - Property 3: Successful registration
   - Property 4: Valid credentials authenticate
   - Property 5: Invalid credentials allow retry
   - Property 6: Welcome message format

2. **Room Management Properties:**
   - Property 7: Users start in Lobby
   - Property 8: Room changes update location
   - Property 9: Room entry displays info
   - Property 10: Message isolation by room
   - Property 19: Room changes update active list

3. **Messaging Properties:**
   - Property 11: Messages broadcast to room
   - Property 12: Message format
   - Property 13: Input cleared after send

4. **Connection Properties:**
   - Property 14: Reconnection on interruption
   - Property 15: User added to active list
   - Property 16: User removed on disconnect
   - Property 17: Active list changes broadcast
   - Property 23: Welcome message on connect
   - Property 24: Retry on connection failure
   - Property 25: Session state preserved
   - Property 26: Reconnection restores room
   - Property 27: Expiration removes user

5. **Command Properties:**
   - Property 20: Rooms command output
   - Property 21: Users command output
   - Property 22: Invalid command errors

**Example Property Tests:**
```python
from hypothesis import given, strategies as st

# Feature: core-terminal-chat, Property 1: Username validation
@given(st.text(min_size=3, max_size=20))
def test_valid_username_accepted(username):
    """For any username 3-20 chars, validation should pass"""
    service = AuthService()
    assert service.validate_username(username)

# Feature: core-terminal-chat, Property 1: Username validation
@given(st.one_of(
    st.text(max_size=2),
    st.text(min_size=21)
))
def test_invalid_username_rejected(username):
    """For any username outside 3-20 chars, validation should fail"""
    service = AuthService()
    assert not service.validate_username(username)

# Feature: core-terminal-chat, Property 10: Message isolation by room
@given(
    st.text(min_size=1, max_size=100),  # message content
    st.sampled_from(["lobby", "techline", "arcade_hall"])  # rooms
)
def test_message_isolation(message_content, target_room):
    """For any message sent to a room, only users in that room receive it"""
    # Setup: Create users in different rooms
    manager = WebSocketManager()
    user_in_room = create_test_user("user1", target_room)
    user_in_other = create_test_user("user2", "other_room")
    
    # Send message to target room
    manager.broadcast_to_room(target_room, {
        "type": "chat_message",
        "content": message_content
    })
    
    # Verify only user in target room received it
    assert user_in_room.received_message(message_content)
    assert not user_in_other.received_message(message_content)
```

### Integration Testing

**Framework:** pytest with FastAPI TestClient

**Coverage Areas:**
- Full authentication flow (register → login → WebSocket connect)
- Room switching with message isolation
- Multi-user chat scenarios
- Connection drop and reconnection
- Command execution end-to-end

**Example Integration Test:**
```python
def test_full_chat_flow():
    """Test complete flow: register, login, join room, send message"""
    client = TestClient(app)
    
    # Register user
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    token = response.json()["token"]
    
    # Connect via WebSocket
    with client.websocket_connect(f"/ws?token={token}") as websocket:
        # Receive welcome message
        data = websocket.receive_json()
        assert data["type"] == "system"
        assert "Welcome" in data["content"]
        
        # Send chat message
        websocket.send_json({
            "type": "chat_message",
            "content": "Hello world"
        })
        
        # Receive own message back
        data = websocket.receive_json()
        assert data["type"] == "chat_message"
        assert data["content"] == "Hello world"
        assert data["username"] == "testuser"
```

### Frontend Testing

**Manual Testing Focus:**
- CRT visual effects render correctly
- Scanlines and phosphor glow appear
- Command line cursor blinks
- Keyboard shortcuts work
- Mouse interactions function
- Responsive layout on different screen sizes

**Automated Testing (Optional):**
- Playwright or Cypress for E2E tests
- Test command execution
- Test message display
- Test room switching

## Implementation Notes

### Security Considerations

1. **Password Storage:**
   - Use bcrypt with cost factor 12
   - Never log or transmit plain passwords
   - Implement password strength requirements

2. **JWT Tokens:**
   - Short expiration (1 hour)
   - Include user ID and username in payload
   - Sign with strong secret key (environment variable)
   - Validate on every WebSocket message

3. **Input Validation:**
   - Sanitize all user inputs
   - Prevent SQL injection (use parameterized queries)
   - Prevent XSS (escape HTML in messages)
   - Rate limit to prevent abuse

4. **WebSocket Security:**
   - Validate token before accepting connection
   - Implement message size limits
   - Timeout idle connections (5 minutes)
   - Prevent message injection attacks

### Performance Considerations

1. **WebSocket Scaling:**
   - Current design: Single server, in-memory state
   - Future: Redis for shared state across servers
   - Consider WebSocket connection limits (typically 10k per server)

2. **Database Optimization:**
   - Index on username for fast lookups
   - Connection pooling for concurrent requests
   - Consider caching active user data

3. **Message Broadcasting:**
   - Current: Iterate and send to each connection
   - Optimization: Batch messages when possible
   - Consider message queue for high traffic

### Development Workflow

1. **Phase 1: Backend Core**
   - Set up FastAPI project structure
   - Implement authentication service
   - Create database models and migrations
   - Build WebSocket manager

2. **Phase 2: Room Management**
   - Implement room service
   - Add room switching logic
   - Build command handler

3. **Phase 3: Frontend UI**
   - Create HTML structure
   - Implement CSS for CRT effects
   - Build command line bar component
   - Add chat display

4. **Phase 4: Integration**
   - Connect frontend to WebSocket
   - Implement message handling
   - Add command execution
   - Test full flow

5. **Phase 5: Polish**
   - Refine CRT effects
   - Add animations
   - Improve error messages
   - Performance optimization

### File Structure

```
obsidian-bbs/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration and environment variables
│   ├── database.py             # Database connection and models
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── service.py          # AuthService
│   │   └── models.py           # User model
│   ├── websocket/
│   │   ├── __init__.py
│   │   ├── manager.py          # WebSocketManager
│   │   └── handlers.py         # Message handlers
│   ├── rooms/
│   │   ├── __init__.py
│   │   ├── service.py          # RoomService
│   │   └── models.py           # Room model
│   ├── commands/
│   │   ├── __init__.py
│   │   └── handler.py          # CommandHandler
│   └── tests/
│       ├── test_auth.py
│       ├── test_rooms.py
│       ├── test_websocket.py
│       └── test_commands.py
├── frontend/
│   ├── index.html              # Main HTML file
│   ├── css/
│   │   ├── terminal.css        # CRT effects and terminal styling
│   │   └── layout.css          # Layout and structure
│   ├── js/
│   │   ├── main.js             # Application entry point
│   │   ├── websocket.js        # WebSocket client
│   │   ├── terminal.js         # Terminal UI renderer
│   │   ├── commandBar.js       # Command line bar
│   │   └── chatDisplay.js      # Chat message display
│   └── assets/
│       ├── fonts/              # Retro terminal fonts
│       └── sounds/             # Dial-up sounds (optional)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
└── README.md                   # Project documentation
```

### Environment Variables

```bash
# .env
DATABASE_URL=sqlite:///./obsidian_bbs.db
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=1
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Dependencies

**Backend (requirements.txt):**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
sqlalchemy==2.0.23
aiosqlite==0.19.0
hypothesis==6.92.1
pytest==7.4.3
pytest-asyncio==0.21.1
```

**Frontend:**
- No build step required
- Optional: Tailwind CSS via CDN for layout utilities
- Vanilla JavaScript (ES6+)
