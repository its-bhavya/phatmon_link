# Configuration Management

The Obsidian BBS application uses environment variables for configuration management. All configuration is centralized in `backend/config.py`.

## Environment Variables

### Required Variables

- **JWT_SECRET_KEY**: Secret key for JWT token signing
  - **Development**: A default is provided with a warning
  - **Production**: MUST be set to a secure random string (at least 16 characters)
  - Generate with: `python -c "import secrets; print(secrets.token_hex(32))"`

### Optional Variables (with defaults)

- **ENVIRONMENT**: Environment mode (`development` or `production`)
  - Default: `development`
  - Affects validation strictness

- **DATABASE_URL**: SQLAlchemy database connection string
  - Default: `sqlite:///./obsidian_bbs.db`
  - Example: `postgresql://user:pass@localhost/dbname`

- **JWT_ALGORITHM**: Algorithm for JWT token signing
  - Default: `HS256`
  - Valid options: `HS256`, `HS384`, `HS512`, `RS256`, `RS384`, `RS512`

- **JWT_EXPIRATION_HOURS**: Token expiration time in hours
  - Default: `1`
  - Must be a positive integer

- **CORS_ORIGINS**: Comma-separated list of allowed CORS origins
  - Default: `http://localhost:3000,http://localhost:8000`
  - Example: `https://example.com,https://app.example.com`

- **HOST**: Server bind address
  - Default: `0.0.0.0` (all interfaces)
  - Example: `127.0.0.1` (localhost only)

- **PORT**: Server port number
  - Default: `8000`
  - Must be between 1 and 65535

### Gemini AI Configuration

- **GEMINI_API_KEY**: API key for Google Gemini AI service
  - Default: None (must be set)
  - Get your API key from: https://makersuite.google.com/app/apikey

- **GEMINI_MODEL**: Gemini model to use
  - Default: `gemini-2.0-flash`
  - Example: `gemini-pro`, `gemini-2.0-flash`

- **GEMINI_TEMPERATURE**: Temperature for AI generation (controls randomness)
  - Default: `0.5`
  - Must be between 0.0 and 2.0
  - Lower values = more deterministic, Higher values = more creative

- **GEMINI_MAX_TOKENS**: Maximum tokens for AI responses
  - Default: `500`
  - Must be a positive integer

### Profile Tracking Configuration

- **PROFILE_RETENTION_DAYS**: Days to retain user profile data
  - Default: `30`
  - Must be a positive integer

- **PROFILE_CACHE_TTL_SECONDS**: Cache TTL for profile data in seconds
  - Default: `300` (5 minutes)
  - Must be non-negative

### Support Bot Configuration

- **SUPPORT_BOT_ENABLED**: Enable/disable the empathetic support bot
  - Default: `true`
  - Valid values: `true`, `false`, `1`, `0`, `yes`, `no`

- **SUPPORT_SENTIMENT_THRESHOLD**: Sentiment threshold for support bot activation
  - Default: `0.6`
  - Must be between 0.0 and 1.0
  - Lower values = more sensitive to negative sentiment

- **SUPPORT_CRISIS_DETECTION_ENABLED**: Enable/disable crisis detection
  - Default: `true`
  - Valid values: `true`, `false`, `1`, `0`, `yes`, `no`

### Instant Answer Recall Configuration

The Instant Answer Recall system provides AI-powered contextual help by searching historical conversations in the Techline room.

- **INSTANT_ANSWER_ENABLED**: Enable/disable the instant answer system
  - Default: `true`
  - Valid values: `true`, `false`, `1`, `0`, `yes`, `no`
  - When disabled, messages are processed normally without instant answers

- **INSTANT_ANSWER_MIN_SIMILARITY**: Minimum similarity threshold for search results
  - Default: `0.7`
  - Must be between 0.0 and 1.0
  - Higher values = more strict matching (fewer but more relevant results)
  - Lower values = more lenient matching (more results but potentially less relevant)
  - Recommended range: 0.6 - 0.8

- **INSTANT_ANSWER_MAX_RESULTS**: Maximum number of search results to use for summary
  - Default: `5`
  - Must be a positive integer
  - Higher values = more comprehensive summaries but slower generation
  - Lower values = faster but potentially less complete summaries
  - Recommended range: 3 - 10

- **INSTANT_ANSWER_CONFIDENCE_THRESHOLD**: Minimum confidence for message classification
  - Default: `0.6`
  - Must be between 0.0 and 1.0
  - Higher values = only high-confidence classifications trigger instant answers
  - Lower values = more messages may trigger instant answers
  - Recommended range: 0.5 - 0.7

- **INSTANT_ANSWER_MAX_SUMMARY_TOKENS**: Maximum tokens for AI-generated summaries
  - Default: `300`
  - Must be a positive integer
  - Higher values = longer, more detailed summaries
  - Lower values = shorter, more concise summaries
  - Recommended range: 200 - 500

- **CHROMADB_HOST**: ChromaDB server hostname
  - Default: `localhost`
  - Example: `chromadb.example.com`
  - Used for vector database connection

- **CHROMADB_PORT**: ChromaDB server port
  - Default: `8001`
  - Must be between 1 and 65535
  - Standard ChromaDB port is 8000, but 8001 avoids conflict with FastAPI

- **CHROMADB_COLLECTION_NAME**: Name of the ChromaDB collection for messages
  - Default: `techline_messages`
  - Must be non-empty
  - Collection is created automatically if it doesn't exist

- **INSTANT_ANSWER_TARGET_ROOM**: Room where instant answers are active
  - Default: `Techline`
  - Must be non-empty
  - Only messages in this room trigger instant answer processing

- **INSTANT_ANSWER_AUTO_INDEX_ON_STARTUP**: Auto-index historical messages on startup
  - Default: `false`
  - Valid values: `true`, `false`, `1`, `0`, `yes`, `no`
  - When enabled, indexes all historical Techline messages on application startup
  - Warning: Can be slow for large message histories

## Usage

### Loading Configuration

```python
from backend.config import get_config

# Get the global configuration instance
config = get_config()

# Access configuration values
database_url = config.DATABASE_URL
jwt_secret = config.JWT_SECRET_KEY
cors_origins = config.CORS_ORIGINS
```

### Setting Environment Variables

#### Using .env file (recommended for development)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```bash
   ENVIRONMENT=development
   DATABASE_URL=sqlite:///./obsidian_bbs.db
   JWT_SECRET_KEY=your-secret-key-here
   ```

3. Load environment variables (automatic with python-dotenv):
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

#### Using system environment variables

**Linux/Mac:**
```bash
export JWT_SECRET_KEY="your-secret-key-here"
export DATABASE_URL="sqlite:///./obsidian_bbs.db"
```

**Windows (PowerShell):**
```powershell
$env:JWT_SECRET_KEY="your-secret-key-here"
$env:DATABASE_URL="sqlite:///./obsidian_bbs.db"
```

**Windows (CMD):**
```cmd
set JWT_SECRET_KEY=your-secret-key-here
set DATABASE_URL=sqlite:///./obsidian_bbs.db
```

## Validation

The configuration module validates all settings on startup:

- **Type checking**: Ensures integers are integers, lists are lists, etc.
- **Range validation**: Checks PORT is 1-65535, JWT_EXPIRATION_HOURS is positive
- **Algorithm validation**: Ensures JWT_ALGORITHM is a supported value
- **Required fields**: In production, JWT_SECRET_KEY must be set and at least 16 characters

### Validation Errors

If configuration is invalid, the application will fail to start with a clear error message:

```
ConfigurationError: Configuration validation failed:
  - JWT_SECRET_KEY is required in production. Set the JWT_SECRET_KEY environment variable.
  - PORT must be between 1 and 65535, got: 70000
```

## Instant Answer System Tuning

The instant answer system can be tuned for different use cases:

### High Precision (Fewer but more relevant results)
```bash
INSTANT_ANSWER_MIN_SIMILARITY=0.8
INSTANT_ANSWER_CONFIDENCE_THRESHOLD=0.7
INSTANT_ANSWER_MAX_RESULTS=3
```

### Balanced (Recommended for most cases)
```bash
INSTANT_ANSWER_MIN_SIMILARITY=0.7
INSTANT_ANSWER_CONFIDENCE_THRESHOLD=0.6
INSTANT_ANSWER_MAX_RESULTS=5
```

### High Recall (More results, potentially less precise)
```bash
INSTANT_ANSWER_MIN_SIMILARITY=0.6
INSTANT_ANSWER_CONFIDENCE_THRESHOLD=0.5
INSTANT_ANSWER_MAX_RESULTS=8
```

### ChromaDB Setup

The instant answer system requires ChromaDB to be running. You can start ChromaDB using Docker:

```bash
docker run -d -p 8001:8000 chromadb/chroma
```

Or install and run locally:

```bash
pip install chromadb
chroma run --host localhost --port 8001
```

## Production Deployment

For production deployment:

1. Set `ENVIRONMENT=production`
2. Generate a secure JWT_SECRET_KEY:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. Set all required environment variables
4. Use a production-grade database (PostgreSQL recommended)
5. Configure CORS_ORIGINS to only include your production domains
6. Set up ChromaDB with persistent storage for instant answer system
7. Consider using a secrets management service (AWS Secrets Manager, HashiCorp Vault, etc.)

## Security Considerations

- **Never commit .env files** to version control (already in .gitignore)
- **Never log or expose JWT_SECRET_KEY** (the config __repr__ hides it)
- **Use strong, random JWT_SECRET_KEY** in production (at least 32 characters)
- **Rotate JWT_SECRET_KEY** periodically in production
- **Use HTTPS** in production to protect tokens in transit
- **Restrict CORS_ORIGINS** to only trusted domains

## Testing

For testing, you can reload configuration:

```python
from backend.config import reload_config
import os

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-key-1234567890"

# Reload configuration
config = reload_config()
```

## Troubleshooting

### "JWT_SECRET_KEY not set" warning

This is normal in development. The application will use a default key. In production, you MUST set this variable.

### "Configuration validation failed"

Check the error message for specific validation failures. Common issues:
- Invalid PORT number
- Invalid JWT_ALGORITHM
- Missing required variables in production

### Configuration not updating

If you change environment variables while the application is running, you need to restart the application. The configuration is loaded once at startup.

### ChromaDB connection errors

If you see errors about ChromaDB connection:
- Ensure ChromaDB is running on the configured host and port
- Check `CHROMADB_HOST` and `CHROMADB_PORT` are correct
- Verify network connectivity to ChromaDB server
- Check ChromaDB logs for errors

### Instant answers not appearing

If instant answers are not being generated:
- Verify `INSTANT_ANSWER_ENABLED=true`
- Check that you're in the configured `INSTANT_ANSWER_TARGET_ROOM` (default: Techline)
- Ensure `GEMINI_API_KEY` is set and valid
- Check that ChromaDB is running and accessible
- Review application logs for classification or search errors
- Try lowering `INSTANT_ANSWER_MIN_SIMILARITY` threshold
- Try lowering `INSTANT_ANSWER_CONFIDENCE_THRESHOLD`

### Too many or irrelevant instant answers

If instant answers are too frequent or not relevant:
- Increase `INSTANT_ANSWER_MIN_SIMILARITY` (try 0.75 or 0.8)
- Increase `INSTANT_ANSWER_CONFIDENCE_THRESHOLD` (try 0.7)
- Reduce `INSTANT_ANSWER_MAX_RESULTS` to focus on top matches
- Check that historical messages are properly indexed

### Slow instant answer generation

If instant answers are taking too long:
- Reduce `INSTANT_ANSWER_MAX_RESULTS` (try 3)
- Reduce `INSTANT_ANSWER_MAX_SUMMARY_TOKENS` (try 200)
- Check ChromaDB performance and indexing
- Verify network latency to Gemini API
- Consider using a faster Gemini model
