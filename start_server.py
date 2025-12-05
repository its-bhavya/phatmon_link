"""
Start the Obsidian BBS server for testing.
This script runs the full backend with authentication and WebSocket support.
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    print("=" * 70)
    print("🖥️  Obsidian BBS - Full Server")
    print("=" * 70)
    print("\n📡 Starting server at: http://localhost:8000")
    print("\n✨ Available pages:")
    print("   • http://localhost:8000/auth.html - Login/Registration")
    print("   • http://localhost:8000/index.html - Main Terminal (requires login)")
    print("   • http://localhost:8000/ - Redirects to auth page")
    print("\n🔧 API Endpoints:")
    print("   • POST /api/auth/register - Register new user")
    print("   • POST /api/auth/login - Login existing user")
    print("   • WS /ws?token=<jwt> - WebSocket connection")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    print("=" * 70)
    
    # Set environment variables if not already set
    if not os.getenv("DATABASE_URL"):
        os.environ["DATABASE_URL"] = "sqlite:///./obsidian_bbs.db"
    if not os.getenv("JWT_SECRET_KEY"):
        os.environ["JWT_SECRET_KEY"] = "dev-secret-key-change-in-production"
    if not os.getenv("CORS_ORIGINS"):
        os.environ["CORS_ORIGINS"] = "http://localhost:8000,http://127.0.0.1:8000"
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
