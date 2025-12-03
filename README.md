# Phantom Link BBS

A modern reimagining of the 1980s Bulletin Board System (BBS) that combines retro terminal aesthetics with real-time chat capabilities. Experience the nostalgia of classic BBS systems with modern web technologies, featuring CRT effects, multi-room chat, and real-time communication.

## Features

- **Retro Terminal UI**: Authentic CRT monitor effects including scanlines, phosphor glow, and subtle flicker
- **Multi-Room Chat**: Navigate between different themed rooms (Lobby, Techline, Arcade Hall, Archives)
- **Real-Time Communication**: WebSocket-based instant messaging with sub-100ms latency
- **User Authentication**: Secure registration and login with JWT tokens and bcrypt password hashing
- **Command System**: Terminal-style commands for navigation and system interaction
- **Active User Tracking**: See who's online and which room they're in
- **Session Persistence**: Automatic reconnection with session state preservation
- **Rate Limiting**: Built-in protection against message flooding and spam

## Technology Stack

**Backend:**
- Python 3.11+
- FastAPI for HTTP and WebSocket endpoints
- Uvicorn ASGI server
- SQLite database with SQLAlchemy ORM
- Passlib (bcrypt) for password hashing
- Python-jose for JWT token management

**Frontend:**
- Vanilla HTML5, CSS3, and JavaScript (ES6+)
- WebSocket client for real-time communication
- CSS-based CRT effects (no heavy frameworks)

## Project Structure

```
phantom-link/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Configuration and environment variables
│   ├── database.py             # Database connection and models
│   ├── rate_limiter.py         # Rate limiting middleware
│   ├── auth/
│   │   ├── service.py          # Authentication service
│   │   └── __init__.py
│   ├── commands/
│   │   ├── handler.py          # Command handler
│   │   └── __init__.py
│   ├── rooms/
│   │   ├── service.py          # Room management service
│   │   ├── models.py           # Room data models
│   │   └── __init__.py
│   ├── websocket/
│   │   ├── manager.py          # WebSocket connection manager
│   │   └── __init__.py
│   └── tests/                  # Backend test suite
│       ├── test_auth_service.py
│       ├── test_command_handler.py
│       ├── test_room_service.py
│       ├── test_websocket.py
│       └── ...
├── frontend/
│   ├── index.html              # Main terminal UI
│   ├── auth.html               # Login/registration page
│   ├── css/
│   │   └── terminal.css        # CRT effects and terminal styling
│   ├── js/
│   │   ├── main.js             # Application entry point
│   │   ├── websocket.js        # WebSocket client
│   │   ├── commandBar.js       # Command line input handler
│   │   └── chatDisplay.js      # Message display component
│   └── assets/                 # Static assets
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variables template
├── start_server.py             # Server startup script
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd phantom-link
```

### 2. Create Python Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy `.env.example` to `.env`:

**Windows:**
```bash
copy .env.example .env
```

**Linux/Mac:**
```bash
cp .env.example .env
```

Edit `.env` and update the values as needed. **Important:** Change `JWT_SECRET_KEY` in production!

```bash
# Generate a secure secret key:
python -c "import secrets; print(secrets.token_hex(32))"
```

## Running the Application

### Start the Server

```bash
python start_server.py
```

Or use uvicorn directly:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`

### Access the Application

1. Open your browser and navigate to `http://localhost:8000`
2. You'll be redirected to the authentication page
3. Register a new account or login with existing credentials
4. Start chatting in the retro terminal interface!

## Environment Variables

Configure these variables in your `.env` file:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `ENVIRONMENT` | Environment mode (development/production) | `development` | No |
| `DATABASE_URL` | SQLite database file path | `sqlite:///./phantom_link.db` | Yes |
| `JWT_SECRET_KEY` | Secret key for JWT token signing | - | Yes |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` | Yes |
| `JWT_EXPIRATION_HOURS` | Token expiration time in hours | `1` | Yes |
| `CORS_ORIGINS` | Comma-separated list of allowed origins | `http://localhost:3000,http://localhost:8000` | Yes |
| `HOST` | Server host address | `0.0.0.0` | No |
| `PORT` | Server port number | `8000` | No |

## API Endpoints

### HTTP Endpoints

#### Authentication

**Register New User**
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "string",  // 3-20 characters, unique
  "password": "string"   // minimum 8 characters
}

Response: 200 OK
{
  "token": "string",
  "user": {
    "id": 1,
    "username": "string",
    "created_at": "2025-12-01T12:00:00Z"
  }
}
```

**Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}

Response: 200 OK
{
  "token": "string",
  "user": {
    "id": 1,
    "username": "string",
    "created_at": "2025-12-01T12:00:00Z"
  },
  "last_login": "2025-12-01T11:00:00Z"
}
```

#### Static Files

```http
GET /                    # Main terminal UI (index.html)
GET /auth                # Authentication page (auth.html)
GET /static/*            # Static assets (CSS, JS, fonts)
```

### WebSocket Endpoint

**Connect to Chat**
```
WS /ws?token={jwt_token}
```

Connection requires a valid JWT token obtained from login/registration.

## WebSocket Message Format

### Client → Server Messages

**Send Chat Message**
```json
{
  "type": "chat_message",
  "content": "Hello world",
  "room": "lobby"
}
```

**Execute Command**
```json
{
  "type": "command",
  "command": "rooms"
}
```

**Join Room**
```json
{
  "type": "join_room",
  "room": "techline"
}
```

### Server → Client Messages

**Chat Message**
```json
{
  "type": "chat_message",
  "username": "user123",
  "content": "Hello world",
  "timestamp": "2025-12-01T12:34:56Z",
  "room": "lobby"
}
```

**System Message**
```json
{
  "type": "system",
  "content": "Welcome to Phantom Link BBS"
}
```

**User List Update**
```json
{
  "type": "user_list",
  "users": [
    { "username": "user123", "room": "lobby" },
    { "username": "user456", "room": "techline" }
  ]
}
```

**Room List**
```json
{
  "type": "room_list",
  "rooms": [
    { "name": "Lobby", "count": 5, "description": "Main gathering space" },
    { "name": "Techline", "count": 2, "description": "Tech discussions" }
  ]
}
```

**Error Message**
```json
{
  "type": "error",
  "content": "Invalid command"
}
```

## Available Commands

Commands are prefixed with `/` and entered in the command line bar:

| Command | Description | Example |
|---------|-------------|---------|
| `/help` | Display list of available commands | `/help` |
| `/rooms` | Show all rooms with user counts | `/rooms` |
| `/users` | Display active users and their rooms | `/users` |
| `/join <room>` | Switch to a different room | `/join techline` |
| `/clear` | Clear the terminal display | `/clear` |
| `/logout` | Disconnect and return to login screen | `/logout` |

### Default Rooms

- **Lobby**: Main gathering space, default entry point for all users
- **Techline**: Technology and programming discussions
- **Arcade Hall**: Gaming and entertainment
- **Archives**: Historical BBS content and nostalgia

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Files

```bash
pytest backend/tests/test_auth_service.py
pytest backend/tests/test_room_service.py
pytest backend/tests/test_websocket.py
```

### Run with Coverage

```bash
pytest --cov=backend --cov-report=html
```

### Test Types

- **Unit Tests**: Test individual components (auth, rooms, commands)
- **Property-Based Tests**: Use Hypothesis to test properties across many inputs
- **Integration Tests**: Test full flows (register → login → chat)

## Security Features

- **Password Hashing**: Bcrypt with cost factor 12
- **JWT Authentication**: Secure token-based authentication with 1-hour expiration
- **Input Validation**: Username (3-20 chars), password (8+ chars)
- **Rate Limiting**: 
  - Messages: 10 per 10 seconds
  - Commands: 5 per 5 seconds
- **SQL Injection Protection**: Parameterized queries via SQLAlchemy
- **XSS Prevention**: HTML escaping in message display
- **Session Management**: 30-second grace period for reconnection

## Rate Limiting

The system implements rate limiting to prevent abuse:

**Message Rate Limit:**
- Limit: 10 messages per 10 seconds per user
- On violation: Warning message, then 30-second temporary mute
- Persistent abuse: User disconnection

**Command Rate Limit:**
- Limit: 5 commands per 5 seconds per user
- On violation: Error message, excess commands ignored

## Troubleshooting

### Database Issues

**Error: "database is locked"**
- SQLite doesn't handle high concurrency well
- For production, consider PostgreSQL or MySQL

**Reset Database:**
```bash
# Delete the database file
rm phantom_link.db

# Restart the server (database will be recreated)
python start_server.py
```

### Connection Issues

**WebSocket connection fails:**
- Check that JWT token is valid and not expired
- Verify CORS_ORIGINS includes your client URL
- Check browser console for error messages

**Can't connect to server:**
- Ensure server is running on correct host/port
- Check firewall settings
- Verify no other service is using port 8000

### Authentication Issues

**"Invalid credentials" error:**
- Verify username and password are correct
- Check that user exists in database
- Maximum 3 failed attempts before disconnection

**Token expired:**
- Tokens expire after 1 hour (configurable)
- Re-login to get a new token

## Development

### Project Dependencies

See `requirements.txt` for full list:
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4
- sqlalchemy==2.0.23
- aiosqlite==0.19.0
- hypothesis==6.92.1 (for property-based testing)
- pytest==7.4.3

### Code Structure

- **Backend**: Modular architecture with separate services for auth, rooms, websocket, and commands
- **Frontend**: Vanilla JavaScript with component-based structure
- **Database**: SQLAlchemy ORM with SQLite (easily swappable)
- **Testing**: pytest with Hypothesis for property-based testing

### Adding New Features

1. Update requirements in `.kiro/specs/core-terminal-chat/requirements.md`
2. Update design in `.kiro/specs/core-terminal-chat/design.md`
3. Add tasks to `.kiro/specs/core-terminal-chat/tasks.md`
4. Implement features following the task list
5. Write tests (unit + property-based)
6. Update this README

## Performance Considerations

**Current Limitations:**
- Single server instance with in-memory state
- SQLite database (not ideal for high concurrency)
- Typical limit: ~10,000 concurrent WebSocket connections per server

**Future Scaling Options:**
- Redis for shared state across multiple servers
- PostgreSQL/MySQL for better concurrent write performance
- Load balancer for horizontal scaling
- Message queue (RabbitMQ/Redis) for high-traffic scenarios

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

(To be determined)

## Acknowledgments

Inspired by the classic BBS systems of the 1980s and 1990s, bringing that nostalgic experience to the modern web.
