"""
Example usage of automatic room routing with Gemini AI.

This script demonstrates how to use the auto-routing features
in your application or with agent hooks.
"""

import asyncio
from unittest.mock import Mock, patch
from backend.vecna.gemini_service import GeminiService
from backend.vecna.auto_router import auto_route_user, check_and_create_room
from backend.rooms.service import RoomService
from backend.database import User


async def example_1_analyze_message_relevance():
    """Example 1: Check if a message fits the current room."""
    print("\n" + "="*70)
    print("EXAMPLE 1: Analyze Message Relevance")
    print("="*70)
    
    with patch('backend.vecna.gemini_service.genai'):
        gemini = GeminiService('fake-key')
        
        # Simulate analyzing a technical question in the Lobby
        result = await gemini.analyze_message_relevance(
            message="How do I fix this Python import error?",
            current_room="Lobby",
            room_description="Main gathering space for general chat"
        )
        
        print(f"\nMessage: 'How do I fix this Python import error?'")
        print(f"Current Room: Lobby (general chat)")
        print(f"\nAnalysis:")
        print(f"  Relevant: {result['is_relevant']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Reason: {result['reason']}")


async def example_2_suggest_best_room():
    """Example 2: Suggest the best room for a message."""
    print("\n" + "="*70)
    print("EXAMPLE 2: Suggest Best Room")
    print("="*70)
    
    with patch('backend.vecna.gemini_service.genai'):
        gemini = GeminiService('fake-key')
        
        available_rooms = {
            "Lobby": "Main gathering space for general chat",
            "Techline": "Technology and programming discussions",
            "Arcade Hall": "Gaming and entertainment zone",
            "Archives": "Historical BBS content and nostalgia"
        }
        
        result = await gemini.suggest_best_room(
            message="Anyone know about React hooks?",
            available_rooms=available_rooms
        )
        
        print(f"\nMessage: 'Anyone know about React hooks?'")
        print(f"\nAvailable Rooms:")
        for name, desc in available_rooms.items():
            print(f"  - {name}: {desc}")
        
        print(f"\nSuggestion:")
        print(f"  Best Room: {result['suggested_room']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Reason: {result['reason']}")
        print(f"  Create New: {result['should_create_new']}")
        if result['new_room_topic']:
            print(f"  New Topic: {result['new_room_topic']}")


async def example_3_auto_route_user():
    """Example 3: Automatically route a user to a better room."""
    print("\n" + "="*70)
    print("EXAMPLE 3: Auto-Route User")
    print("="*70)
    
    with patch('backend.vecna.gemini_service.genai'):
        # Setup
        gemini = GeminiService('fake-key')
        room_service = RoomService()
        room_service.create_default_rooms()
        
        # Create mock user
        user = Mock(spec=User)
        user.username = "alice"
        user.id = 1
        
        # User is in Lobby but asks technical question
        room_service.join_room(user, "Lobby")
        
        result = await auto_route_user(
            user=user,
            message="How do I fix this Python import error?",
            current_room="Lobby",
            room_service=room_service,
            gemini_service=gemini,
            confidence_threshold=0.7
        )
        
        print(f"\nUser: {user.username}")
        print(f"Message: 'How do I fix this Python import error?'")
        print(f"Current Room: Lobby")
        
        print(f"\nRouting Decision:")
        print(f"  Moved: {result['moved']}")
        if result['moved']:
            print(f"  From: {result['from_room']}")
            print(f"  To: {result['to_room']}")
            print(f"  Reason: {result['reason']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"\n  Notification:")
            print(f"  {result['notification']}")
        else:
            print(f"  Reason: {result['reason']}")


async def example_4_check_room_creation():
    """Example 4: Check if a new room should be created."""
    print("\n" + "="*70)
    print("EXAMPLE 4: Check for New Room Creation")
    print("="*70)
    
    with patch('backend.vecna.gemini_service.genai'):
        gemini = GeminiService('fake-key')
        room_service = RoomService()
        room_service.create_default_rooms()
        
        # Simulate multiple users discussing React
        recent_messages = [
            {"user": "alice", "message": "Anyone know about React hooks?", "room": "Lobby"},
            {"user": "bob", "message": "Yeah, useEffect is confusing", "room": "Lobby"},
            {"user": "charlie", "message": "I'm struggling with useState", "room": "Lobby"},
            {"user": "dave", "message": "React context is hard", "room": "Lobby"},
            {"user": "eve", "message": "Need help with React Router", "room": "Lobby"},
            {"user": "frank", "message": "React hooks are tricky", "room": "Lobby"},
        ]
        
        result = await check_and_create_room(
            recent_messages=recent_messages,
            room_service=room_service,
            gemini_service=gemini,
            message_threshold=5,
            confidence_threshold=0.75
        )
        
        print(f"\nRecent Messages ({len(recent_messages)} messages):")
        for msg in recent_messages:
            print(f"  [{msg['user']}]: {msg['message']}")
        
        print(f"\nRoom Creation Decision:")
        print(f"  Should Create: {result['created']}")
        if result['created']:
            print(f"  Room Name: {result['room_name']}")
            print(f"  Description: {result['description']}")
            print(f"  Reason: {result['reason']}")
            print(f"  Affected Users: {', '.join(result['affected_users'])}")
            print(f"\n  Notification:")
            print(f"  {result['notification']}")
        else:
            print(f"  Reason: {result['reason']}")


async def example_5_complete_workflow():
    """Example 5: Complete workflow with multiple messages."""
    print("\n" + "="*70)
    print("EXAMPLE 5: Complete Workflow")
    print("="*70)
    
    with patch('backend.vecna.gemini_service.genai'):
        gemini = GeminiService('fake-key')
        room_service = RoomService()
        room_service.create_default_rooms()
        
        # Create mock users
        users = {
            "alice": Mock(spec=User, username="alice", id=1),
            "bob": Mock(spec=User, username="bob", id=2),
            "charlie": Mock(spec=User, username="charlie", id=3),
        }
        
        # All users start in Lobby
        for user in users.values():
            room_service.join_room(user, "Lobby")
        
        print("\nSimulating conversation...")
        print("-" * 70)
        
        # Message 1: Alice asks technical question
        print("\n[Alice in Lobby]: How do I fix this Python import error?")
        result = await auto_route_user(
            users["alice"], 
            "How do I fix this Python import error?",
            "Lobby",
            room_service,
            gemini,
            confidence_threshold=0.7
        )
        if result['moved']:
            print(f"  → {result['notification']}")
        
        # Message 2: Bob talks about games
        print("\n[Bob in Lobby]: Anyone playing the new Zelda game?")
        result = await auto_route_user(
            users["bob"],
            "Anyone playing the new Zelda game?",
            "Lobby",
            room_service,
            gemini,
            confidence_threshold=0.7
        )
        if result['moved']:
            print(f"  → {result['notification']}")
        
        # Message 3: Charlie asks about BBS history
        print("\n[Charlie in Lobby]: What were BBSes like in the 80s?")
        result = await auto_route_user(
            users["charlie"],
            "What were BBSes like in the 80s?",
            "Lobby",
            room_service,
            gemini,
            confidence_threshold=0.7
        )
        if result['moved']:
            print(f"  → {result['notification']}")
        
        print("\n" + "-" * 70)
        print("\nFinal Room Distribution:")
        for room in room_service.get_rooms():
            users_in_room = room_service.get_users_in_room(room.name)
            if users_in_room:
                print(f"  {room.name}: {', '.join(users_in_room)}")


async def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("AUTOMATIC ROOM ROUTING EXAMPLES")
    print("="*70)
    print("\nThese examples demonstrate how the auto-routing system works.")
    print("In production, these would use real Gemini API calls.")
    
    await example_1_analyze_message_relevance()
    await example_2_suggest_best_room()
    await example_3_auto_route_user()
    await example_4_check_room_creation()
    await example_5_complete_workflow()
    
    print("\n" + "="*70)
    print("Examples complete!")
    print("="*70)
    print("\nTo use in your application:")
    print("1. See backend/vecna/AGENT_HOOKS_GUIDE.md for integration guide")
    print("2. Configure GEMINI_API_KEY in your .env file")
    print("3. Set up agent hooks as described in the guide")
    print()


if __name__ == "__main__":
    asyncio.run(main())
