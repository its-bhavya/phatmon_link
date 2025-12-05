"""
Diagnostic script to check why instant answer isn't working.
"""

import os
from dotenv import load_dotenv
import chromadb

load_dotenv()

print("=" * 60)
print("INSTANT ANSWER DIAGNOSTIC")
print("=" * 60)
print()

# Check environment variables
print("1. Environment Variables:")
print(f"   INSTANT_ANSWER_ENABLED: {os.getenv('INSTANT_ANSWER_ENABLED')}")
print(f"   INSTANT_ANSWER_TARGET_ROOM: {os.getenv('INSTANT_ANSWER_TARGET_ROOM')}")
print(f"   GEMINI_API_KEY: {'Set' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
print(f"   CHROMADB_HOST: {os.getenv('CHROMADB_HOST', 'localhost')}")
print(f"   CHROMADB_PORT: {os.getenv('CHROMADB_PORT', '8001')}")
print()

# Check ChromaDB connection
print("2. ChromaDB Connection:")
try:
    chromadb_host = os.getenv("CHROMADB_HOST", "localhost")
    chromadb_port = int(os.getenv("CHROMADB_PORT", "8001"))
    
    client = chromadb.HttpClient(host=chromadb_host, port=chromadb_port)
    client.heartbeat()
    print(f"   ✓ ChromaDB is running at {chromadb_host}:{chromadb_port}")
    
    # Check collection
    collection_name = os.getenv("CHROMADB_COLLECTION_NAME", "techline_messages")
    try:
        collection = client.get_collection(name=collection_name)
        count = collection.count()
        print(f"   ✓ Collection '{collection_name}' exists with {count} messages")
    except Exception as e:
        print(f"   ⚠ Collection '{collection_name}' does not exist yet (will be created)")
    
except Exception as e:
    print(f"   ✗ ChromaDB connection failed: {e}")
    print(f"   Make sure ChromaDB is running:")
    print(f"   > start_chromadb.bat")
print()

# Check if instant answer is enabled
print("3. Configuration Check:")
enabled = os.getenv("INSTANT_ANSWER_ENABLED", "false").lower() == "true"
if enabled:
    print("   ✓ Instant Answer is ENABLED")
else:
    print("   ✗ Instant Answer is DISABLED")
    print("   Set INSTANT_ANSWER_ENABLED=true in .env")
print()

# Summary
print("=" * 60)
print("SUMMARY")
print("=" * 60)

issues = []

if not os.getenv('GEMINI_API_KEY'):
    issues.append("GEMINI_API_KEY not set")

if not enabled:
    issues.append("INSTANT_ANSWER_ENABLED is false")

try:
    client = chromadb.HttpClient(
        host=os.getenv("CHROMADB_HOST", "localhost"),
        port=int(os.getenv("CHROMADB_PORT", "8001"))
    )
    client.heartbeat()
except:
    issues.append("ChromaDB not running")

if issues:
    print("❌ Issues found:")
    for issue in issues:
        print(f"   - {issue}")
    print()
    print("Fix these issues and restart the server.")
else:
    print("✓ All checks passed!")
    print()
    print("If you still don't see logs:")
    print("1. Restart the server: python start_server.py")
    print("2. Make sure you're posting to 'Techline' room")
    print("3. Watch the terminal where start_server.py is running")
