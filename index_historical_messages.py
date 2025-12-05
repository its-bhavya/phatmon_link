"""
Script to index historical messages into ChromaDB for instant answer system.

This script processes all historical messages from the Techline room and stores
them in ChromaDB with embeddings, classifications, and tags.

Usage:
    python index_historical_messages.py [--fast] [--room ROOM_NAME] [--limit N]

Options:
    --fast          Use fast parallel indexing (recommended for large datasets)
    --room          Room name to index (default: Techline)
    --limit         Maximum number of messages to index (default: 1000)
"""

import asyncio
import sys
import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.config import get_config
from backend.database import get_db
from backend.vecna.gemini_service import GeminiService
from backend.instant_answer.config import InstantAnswerConfig
from backend.instant_answer.service import InstantAnswerService
from backend.instant_answer.indexer import index_historical_messages
from backend.instant_answer.fast_indexer import fast_index_historical_messages

import chromadb
import google.generativeai as genai


async def main():
    """Main indexing function."""
    parser = argparse.ArgumentParser(description='Index historical messages into ChromaDB')
    parser.add_argument('--fast', action='store_true', help='Use fast parallel indexing')
    parser.add_argument('--room', default='Techline', help='Room name to index')
    parser.add_argument('--limit', type=int, default=1000, help='Max messages to index')
    args = parser.parse_args()
    
    print("=" * 60)
    print("HISTORICAL MESSAGE INDEXING")
    print("=" * 60)
    print()
    
    # Check environment
    print("1. Checking environment...")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("   ✗ GEMINI_API_KEY not set!")
        return
    print("   ✓ GEMINI_API_KEY: Set")
    
    chromadb_host = os.getenv("CHROMADB_HOST", "localhost")
    chromadb_port = int(os.getenv("CHROMADB_PORT", "8001"))
    print(f"   ✓ ChromaDB: {chromadb_host}:{chromadb_port}")
    print()
    
    # Initialize services
    print("2. Initializing services...")
    
    # Configure Gemini
    genai.configure(api_key=gemini_key)
    gemini_service = GeminiService(api_key=gemini_key)
    print("   ✓ GeminiService initialized")
    
    # Connect to ChromaDB
    try:
        chroma_client = chromadb.HttpClient(
            host=chromadb_host,
            port=chromadb_port
        )
        # Test connection
        chroma_client.heartbeat()
        print("   ✓ ChromaDB connected")
    except Exception as e:
        print(f"   ✗ ChromaDB connection failed: {e}")
        print("   Make sure ChromaDB server is running:")
        print("   > start_chromadb.bat")
        return
    
    # Get or create collection
    collection_name = "techline_messages"
    try:
        collection = chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        existing_count = collection.count()
        print(f"   ✓ Collection '{collection_name}' ready (existing: {existing_count} messages)")
    except Exception as e:
        print(f"   ✗ Failed to get collection: {e}")
        return
    
    # Initialize InstantAnswerService
    ia_config = InstantAnswerConfig()
    instant_answer_service = InstantAnswerService(
        gemini_service=gemini_service,
        chroma_collection=collection,
        config=ia_config
    )
    print("   ✓ InstantAnswerService initialized")
    
    # Initialize RoomService
    from backend.database import init_database
    from backend.rooms.service import RoomService as RoomsRoomService
    config = get_config()
    init_database(config.DATABASE_URL)
    room_service = RoomsRoomService()
    room_service.create_default_rooms()
    print("   ✓ RoomService initialized")
    print()
    
    # Get room and messages
    print(f"3. Loading messages from room '{args.room}'...")
    room = room_service.get_room(args.room)
    if not room:
        print(f"   ✗ Room '{args.room}' not found!")
        return
    
    messages = room.get_recent_messages(limit=args.limit)
    print(f"   ✓ Found {len(messages)} messages to index")
    print()
    
    if not messages:
        print("   No messages to index. Exiting.")
        return
    
    # Index messages
    print(f"4. Indexing messages ({'FAST mode' if args.fast else 'standard mode'})...")
    print()
    
    try:
        if args.fast:
            # Use fast parallel indexing
            stats = await fast_index_historical_messages(
                instant_answer_service=instant_answer_service,
                room_service=room_service,
                target_room=args.room,
                embedding_batch_size=12,
                max_workers=10
            )
        else:
            # Use standard indexing
            stats = await index_historical_messages(
                instant_answer_service=instant_answer_service,
                room_service=room_service,
                target_room=args.room,
                batch_size=10
            )
        
        print()
        print("=" * 60)
        print("INDEXING COMPLETE")
        print("=" * 60)
        print(f"Processed: {stats['processed']}")
        print(f"Stored:    {stats['stored']}")
        print(f"Failed:    {stats['failed']}")
        print()
        
        # Show final collection count
        final_count = collection.count()
        print(f"Total messages in ChromaDB: {final_count}")
        print()
        
        if stats['stored'] > 0:
            print("✓ Messages successfully indexed!")
            print("  The instant answer system can now search these messages.")
        else:
            print("⚠ No messages were stored. Check the logs for errors.")
    
    except Exception as e:
        print(f"✗ Indexing failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
