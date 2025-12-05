# Project Structure

## Root Directory

```
obsidian-bbs/
├── backend/              # Python backend application
├── frontend/             # Vanilla JS/HTML/CSS frontend
├── chroma_data/          # ChromaDB vector storage (generated)
├── .env                  # Environment configuration (not in git)
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
├── start_server.py       # Server startup script
├── start_chromadb.bat    # ChromaDB startup helper
└── obsidian_bbs.db       # SQLite database (generated)
```

## Backend Structure

```
backend/
├── main.py               # FastAPI app entry point, WebSocket handler
├── config.py             # Centralized configuration management
├── database.py           # SQLAlchemy models and DB connection
├── rate_limiter.py       # Rate limiting middleware
│
├── auth/                 # Authentication service
│   ├── service.py        # Password hashing, JWT, user validation
│   └── __init__.py
│
├── rooms/                # Room management
│   ├── service.py        # Room operations, user tracking
│   ├── models.py         # Room data models
│   └── __init__.py
│
├── websocket/            # WebSocket connection management
│   ├── manager.py        # Connection pool, broadcasting
│   └── __init__.py
│
├── commands/             # Terminal command handling
│   ├── handler.py        # Command parser and executor
│   └── __init__.py
│
├── instant_answer/       # AI knowledge system (Techline only)
│   ├── service.py        # Main orchestrator
│   ├── classifier.py     # Message type classification
│   ├── tagger.py         # Auto-tagging with topics/keywords
│   ├── search_engine.py  # Semantic vector search
│   ├── summary_generator.py  # AI summary generation
│   ├── storage.py        # ChromaDB storage operations
│   ├── indexer.py        # Historical message indexing
│   ├── chroma_client.py  # ChromaDB client initialization
│   ├── config.py         # Instant answer configuration
│   ├── retry_utils.py    # Retry logic for API calls
│   └── ARCHITECTURE.md   # Detailed architecture docs
│
├── support/              # Empathetic support bot
│   ├── bot.py            # AI bot conversation logic
│   ├── sentiment.py      # Sentiment analysis and crisis detection
│   ├── hotlines.py       # Crisis hotline information
│   ├── room_service.py   # Support room management
│   ├── logger.py         # Support interaction logging
│   └── SUPPORT_BOT_OVERVIEW.md
│
├── vecna/                # Gemini AI integration
│   ├── gemini_service.py # Gemini API wrapper
│   ├── sentiment.py      # Sentiment analysis via Gemini
│   └── user_profile.py   # User profile tracking
│
├── sysop/                # Message routing brain
│   ├── brain.py          # Intelligent message routing
│   └── __init__.py
│
└── tests/                # Test suite
    ├── test_auth_service.py
    ├── test_instant_answer_service.py
    ├── test_support_bot.py
    └── ...               # 30+ test files
```

## Frontend Structure

```
frontend/
├── index.html            # Main terminal interface
├── auth.html             # Login/registration page
├── debug.html            # Debug/testing page
│
├── css/
│   └── terminal.css      # CRT effects, terminal styling
│
├── js/
│   ├── main.js           # Application entry point
│   ├── websocket.js      # WebSocket client
│   ├── commandBar.js     # Command line input handler
│   ├── chatDisplay.js    # Message rendering
│   ├── sidePanel.js      # User/room list sidebar
│   ├── instantAnswerHandler.js  # Instant answer UI
│   ├── supportHandler.js # Support bot UI
│   ├── gameManager.js    # Game launcher
│   ├── snake.js          # Snake game
│   ├── tetris.js         # Tetris game
│   ├── breakout.js       # Breakout game
│   └── README-*.md       # Component documentation
│
└── assets/               # Static assets (images, fonts)
```

## Key File Responsibilities

### Backend Entry Points

**`backend/main.py`**: FastAPI application
- HTTP endpoints: `/api/auth/register`, `/api/auth/login`
- WebSocket endpoint: `/ws?token={jwt}`
- Lifespan management (startup/shutdown)
- Message routing to instant answer and support bot services

**`backend/config.py`**: Configuration
- Loads and validates environment variables
- Provides `get_config()` singleton
- Validates JWT, CORS, Gemini, ChromaDB settings

**`backend/database.py`**: Database models
- User, Session, Message, Room models
- SQLAlchemy setup and connection management

### Service Modules

**`backend/auth/service.py`**: Authentication
- Password hashing with bcrypt
- JWT token generation and validation
- User registration and login
- Session management

**`backend/rooms/service.py`**: Room management
- Create/join/leave rooms
- Track users per room
- Message history storage
- Default room creation (Lobby, Techline, Arcade Hall)

**`backend/websocket/manager.py`**: WebSocket connections
- Connection pool management
- Broadcasting to rooms or all users
- User presence tracking

**`backend/instant_answer/service.py`**: Instant answer orchestrator
- Coordinates classification → tagging → storage → search → summary
- Room filtering (Techline only)
- Error handling with graceful degradation

**`backend/support/bot.py`**: Support bot
- Empathetic response generation
- Context-aware conversations
- Crisis detection and hotline provision

### Frontend Entry Points

**`frontend/js/main.js`**: Application initialization
- WebSocket connection setup
- Message routing to handlers
- Command execution
- User authentication check

**`frontend/js/websocket.js`**: WebSocket client
- Connection management
- Automatic reconnection
- Message sending/receiving
- Event handling

**`frontend/js/chatDisplay.js`**: Message rendering
- Timestamp formatting
- Username display
- System message styling
- Instant answer formatting

## Module Dependencies

### Backend Dependencies
- `main.py` → all service modules
- `instant_answer/service.py` → classifier, tagger, search_engine, summary_generator, storage
- `support/bot.py` → vecna/gemini_service, sentiment, hotlines
- All services → `config.py`, `database.py`

### Frontend Dependencies
- `main.js` → websocket, commandBar, chatDisplay, sidePanel
- `instantAnswerHandler.js` → chatDisplay
- `supportHandler.js` → chatDisplay
- All modules → No external dependencies (vanilla JS)

## Configuration Files

**`.env`**: Environment variables (not in git)
- Database URL, JWT secret, CORS origins
- Gemini API key and model settings
- ChromaDB connection details
- Feature flags (instant answer, support bot)

**`requirements.txt`**: Python dependencies
- Pinned versions for reproducibility
- Includes dev dependencies (pytest, hypothesis)

## Documentation Locations

**User Guides**:
- `USER_GUIDE_INSTANT_ANSWER.md` - How to use instant answers
- `USER_GUIDE_SUPPORT_BOT.md` - Support bot usage

**Architecture Docs**:
- `backend/instant_answer/ARCHITECTURE.md` - Instant answer system design
- `backend/support/SUPPORT_BOT_OVERVIEW.md` - Support bot design
- `backend/websocket/IMPLEMENTATION_SUMMARY.md` - WebSocket implementation

**Component READMEs**:
- `frontend/js/README-*.md` - Frontend component docs
- `backend/*/DOCUMENTATION_INDEX.md` - Feature documentation indexes

## Naming Conventions

**Python**:
- Modules: `snake_case.py`
- Classes: `PascalCase`
- Functions/methods: `snake_case()`
- Constants: `UPPER_SNAKE_CASE`

**JavaScript**:
- Files: `camelCase.js`
- Classes: `PascalCase`
- Functions: `camelCase()`
- Constants: `UPPER_SNAKE_CASE`

**Database**:
- Tables: `snake_case` (auto-generated from model names)
- Columns: `snake_case`

## Import Patterns

**Backend**: Absolute imports from `backend.*`
```python
from backend.auth.service import AuthService
from backend.config import get_config
```

**Frontend**: ES6 modules with relative paths
```javascript
import { WebSocketClient } from './websocket.js';
import { CommandLineBar } from './commandBar.js';
```

## Testing Organization

Tests mirror the source structure:
- `backend/tests/test_auth_service.py` tests `backend/auth/service.py`
- `backend/tests/test_instant_answer_service.py` tests `backend/instant_answer/service.py`
- Integration tests use `test_*_integration.py` naming
