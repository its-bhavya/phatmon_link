# Technology Stack

## Backend

**Framework**: FastAPI (Python 3.11+)
- ASGI server: Uvicorn with WebSocket support
- ORM: SQLAlchemy 2.0
- Database: SQLite (development), PostgreSQL-ready for production
- Authentication: python-jose (JWT), passlib with bcrypt
- Async: Native Python asyncio

**AI Services**:
- Google Gemini API (gemini-2.0-flash model)
- ChromaDB for vector storage and semantic search
- Embedding model: models/embedding-001 (768 dimensions)

**Key Libraries**:
- `fastapi==0.104.1` - Web framework
- `uvicorn[standard]==0.24.0` - ASGI server
- `sqlalchemy==2.0.23` - Database ORM
- `python-jose[cryptography]==3.3.0` - JWT tokens
- `passlib[bcrypt]==1.7.4` - Password hashing
- `google-generativeai==0.3.2` - Gemini API
- `chromadb==0.4.22` - Vector database
- `python-dotenv>=1.1.1` - Environment variables

## Frontend

**Pure Vanilla Stack**: No frameworks, no build process
- HTML5, CSS3, JavaScript (ES6+)
- WebSocket API for real-time communication
- CSS-based CRT effects (scanlines, phosphor glow)
- ES6 modules for code organization

## Testing

**Framework**: pytest with async support
- `pytest==7.4.3` - Test runner
- `pytest-asyncio==0.21.1` - Async test support
- `hypothesis==6.92.1` - Property-based testing
- `httpx==0.25.2` - HTTP client for testing

**Test Types**:
- Unit tests with mocks
- Integration tests with real services
- Property-based tests (100+ iterations per property)
- WebSocket integration tests

## Development Environment

**Configuration**: Environment variables via `.env` file
- See `.env.example` for all configuration options
- Critical: JWT_SECRET_KEY, GEMINI_API_KEY, CHROMADB settings

**Database**: SQLite for development (file-based)
- Location: `obsidian_bbs.db` in project root
- Migrations: SQLAlchemy declarative models (auto-create on startup)

## Common Commands

### Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

### Running

```bash
# Start ChromaDB (required for Instant Answer)
start_chromadb.bat  # Windows
docker run -d -p 8001:8000 chromadb/chroma  # Docker

# Start main server
python start_server.py

# Or use uvicorn directly
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest backend/tests/test_auth_service.py

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test pattern
pytest -k "test_instant_answer"
```

### Database

```bash
# Reset database (delete and recreate)
del obsidian_bbs.db  # Windows
rm obsidian_bbs.db   # Linux/Mac
python start_server.py  # Auto-creates on startup
```

### Diagnostics

```bash
# Check instant answer configuration
python diagnose_instant_answer.py

# Verify real-time indexing
python verify_realtime_indexing.py

# Test instant answer flow
python test_instant_answer_flow.py
```

## Architecture Patterns

**Modular Services**: Each feature is a self-contained service module
- `backend/auth/` - Authentication
- `backend/rooms/` - Room management
- `backend/websocket/` - WebSocket connections
- `backend/instant_answer/` - AI knowledge system
- `backend/support/` - Empathetic support bot
- `backend/vecna/` - Gemini AI integration
- `backend/sysop/` - Message routing brain

**Error Handling Philosophy**: Graceful degradation
- AI failures never prevent message delivery
- Classification errors default to safe fallbacks
- Storage failures are logged but don't block processing
- Retry logic with exponential backoff for API calls

**Configuration Management**: Centralized in `backend/config.py`
- Single source of truth for all settings
- Validation on startup with clear error messages
- Type conversion and sensible defaults
- Environment-aware (development vs production)

**Testing Strategy**: Comprehensive coverage
- Unit tests with mocked dependencies
- Integration tests with real services
- Property-based tests for universal properties
- 80%+ code coverage target
