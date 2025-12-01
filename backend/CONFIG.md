# Configuration Management

The Phantom Link BBS application uses environment variables for configuration management. All configuration is centralized in `backend/config.py`.

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
  - Default: `sqlite:///./phantom_link.db`
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
   DATABASE_URL=sqlite:///./phantom_link.db
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
export DATABASE_URL="sqlite:///./phantom_link.db"
```

**Windows (PowerShell):**
```powershell
$env:JWT_SECRET_KEY="your-secret-key-here"
$env:DATABASE_URL="sqlite:///./phantom_link.db"
```

**Windows (CMD):**
```cmd
set JWT_SECRET_KEY=your-secret-key-here
set DATABASE_URL=sqlite:///./phantom_link.db
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
6. Consider using a secrets management service (AWS Secrets Manager, HashiCorp Vault, etc.)

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
