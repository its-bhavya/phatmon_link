"""
Simple test server to view the terminal CSS effects.
Run this to preview the frontend without full backend setup.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()

# Mount static files
app.mount("/css", StaticFiles(directory="frontend/css"), name="css")
app.mount("/js", StaticFiles(directory="frontend/js"), name="js")
app.mount("/assets", StaticFiles(directory="frontend/assets"), name="assets")

@app.get("/")
async def root():
    """Serve the main HTML file."""
    return FileResponse("frontend/index.html")

@app.get("/auth.html")
async def auth():
    """Serve the authentication page."""
    return FileResponse("frontend/auth.html")

@app.get("/index.html")
async def index():
    """Serve the main HTML file."""
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    print("=" * 60)
    print("🖥️  Phantom Link BBS - Terminal Preview Server")
    print("=" * 60)
    print("\n📡 Server starting at: http://localhost:8000")
    print("\n✨ You should see:")
    print("   • Green phosphor glow on text")
    print("   • Scanlines across the screen")
    print("   • Subtle CRT flicker effect")
    print("   • Blinking cursor")
    print("   • VT323 retro font")
    print("\n🛑 Press Ctrl+C to stop the server\n")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
