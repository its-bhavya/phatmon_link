"""
Automatic Room Router for Agent Hooks.

This module provides easy-to-use functions for agent hooks to automatically
route users to appropriate rooms based on message content.

Usage with Agent Hooks:
    1. On message send: Check if message fits current room
    2. If not: Suggest and move to better room
    3. Periodically: Check if new room should be created

Example Agent Hook Configuration:
    Trigger: On message send
    Action: Run auto_route_user(user, message, current_room, room_service, gemini_service)
"""

import logging
from typing import Dict, Any, Optional, List
from backend.vecna.gemini_service import GeminiService
from backend.rooms.service import RoomService
from backend.database import User

logger = logging.getLogger(__name__)


async def auto_route_user(
    user: User,
    message: str,
    current_room: str,
    room_service: RoomService,
    gemini_service: GeminiService,
    confidence_threshold: float = 0.7
) -> Dict[str, Any]:
    """
    Automatically route user to appropriate room based on message content.
    
    This function:
    1. Analyzes if message fits current room
    2. If not, suggests best alternative room
    3. Moves user if confidence is high enough
    4. Returns routing decision for notification
    
    Args:
        user: User object
        message: User's message
        current_room: Current room name
        room_service: RoomService instance
        gemini_service: GeminiService instance
        confidence_threshold: Minimum confidence to auto-move (default: 0.7)
    
    Returns:
        Dict with:
            - moved (bool): Whether user was moved
            - from_room (str): Original room
            - to_room (str): New room (if moved)
            - reason (str): Explanation
            - confidence (float): Confidence score
            - notification (str): Message to show user
    
    Example:
        result = await auto_route_user(
            user, 
            "How do I fix this Python bug?",
            "Lobby",
            room_service,
            gemini_service
        )
        if result['moved']:
            await send_notification(user, result['notification'])
    """
    try:
        # Get current room info
        room = room_service.get_room(current_room)
        if not room:
            return {
                "moved": False,
                "from_room": current_room,
                "to_room": current_room,
                "reason": "Room not found",
                "confidence": 0.0,
                "notification": ""
            }
        
        # Step 1: Check if message fits current room
        relevance = await gemini_service.analyze_message_relevance(
            message,
            current_room,
            room.description
        )
        
        # If message fits current room well, no need to move
        if relevance['is_relevant'] and relevance['confidence'] >= confidence_threshold:
            return {
                "moved": False,
                "from_room": current_room,
                "to_room": current_room,
                "reason": "Message fits current room",
                "confidence": relevance['confidence'],
                "notification": ""
            }
        
        # Step 2: Message doesn't fit - suggest better room
        available_rooms = {
            r.name: r.description 
            for r in room_service.get_rooms()
            if r.name != current_room
        }
        
        suggestion = await gemini_service.suggest_best_room(
            message,
            available_rooms,
            user_profile=None  # Could pass user profile here if available
        )
        
        # Step 3: Move user if confidence is high enough
        if suggestion['confidence'] >= confidence_threshold:
            suggested_room = suggestion['suggested_room']
            
            # Move user to suggested room
            success = room_service.move_user(user, current_room, suggested_room)
            
            if success:
                notification = (
                    f"[SYSOP] Your message seems to be about {suggestion['reason']}. "
                    f"Moving you to {suggested_room}."
                )
                
                return {
                    "moved": True,
                    "from_room": current_room,
                    "to_room": suggested_room,
                    "reason": suggestion['reason'],
                    "confidence": suggestion['confidence'],
                    "notification": notification
                }
        
        # Confidence too low or move failed
        return {
            "moved": False,
            "from_room": current_room,
            "to_room": current_room,
            "reason": f"Low confidence ({suggestion['confidence']:.2f})",
            "confidence": suggestion['confidence'],
            "notification": ""
        }
    
    except Exception as e:
        logger.error(f"Auto-routing failed: {e}")
        return {
            "moved": False,
            "from_room": current_room,
            "to_room": current_room,
            "reason": f"Error: {e}",
            "confidence": 0.0,
            "notification": ""
        }


async def check_and_create_room(
    recent_messages: List[Dict[str, str]],
    room_service: RoomService,
    gemini_service: GeminiService,
    message_threshold: int = 5,
    confidence_threshold: float = 0.75
) -> Dict[str, Any]:
    """
    Check if a new room should be created based on message patterns.
    
    This function should be called periodically (e.g., every 10 messages)
    to detect when multiple users are discussing a topic that needs its own room.
    
    Args:
        recent_messages: List of recent messages with 'user', 'message', 'room'
        room_service: RoomService instance
        gemini_service: GeminiService instance
        message_threshold: Min messages about topic to create room (default: 5)
        confidence_threshold: Min confidence to create room (default: 0.75)
    
    Returns:
        Dict with:
            - created (bool): Whether room was created
            - room_name (str): Name of new room (if created)
            - description (str): Room description
            - reason (str): Explanation
            - affected_users (list): Users who should be notified
            - notification (str): Message to show users
    
    Example:
        # Call this every 10 messages or on a timer
        result = await check_and_create_room(
            recent_messages,
            room_service,
            gemini_service
        )
        if result['created']:
            for username in result['affected_users']:
                await notify_user(username, result['notification'])
    """
    try:
        # Get available rooms
        available_rooms = {
            r.name: r.description 
            for r in room_service.get_rooms()
        }
        
        # Analyze if new room is needed
        analysis = await gemini_service.should_create_new_room(
            recent_messages,
            available_rooms,
            threshold=message_threshold
        )
        
        # Create room if confidence is high enough
        if analysis['should_create'] and analysis['confidence'] >= confidence_threshold:
            topic = analysis['topic']
            
            # Check if room already exists
            if topic in available_rooms:
                return {
                    "created": False,
                    "room_name": topic,
                    "description": "",
                    "reason": "Room already exists",
                    "affected_users": [],
                    "notification": ""
                }
            
            # Create new room
            description = f"Discussion about {topic}"
            room_service.rooms[topic] = type('Room', (), {
                'name': topic,
                'description': description,
                'users': set()
            })()
            
            notification = (
                f"[SYSOP] New room '{topic}' created based on recent discussions. "
                f"Type /join {topic} to participate!"
            )
            
            logger.info(f"Auto-created room: {topic} (confidence: {analysis['confidence']:.2f})")
            
            return {
                "created": True,
                "room_name": topic,
                "description": description,
                "reason": analysis['reason'],
                "affected_users": analysis['affected_users'],
                "notification": notification
            }
        
        # Not enough confidence or shouldn't create
        return {
            "created": False,
            "room_name": "",
            "description": "",
            "reason": analysis['reason'],
            "affected_users": [],
            "notification": ""
        }
    
    except Exception as e:
        logger.error(f"Room creation check failed: {e}")
        return {
            "created": False,
            "room_name": "",
            "description": "",
            "reason": f"Error: {e}",
            "affected_users": [],
            "notification": ""
        }


# ============================================================================
# Simple wrapper functions for agent hooks
# ============================================================================

async def on_message_hook(
    user: User,
    message: str,
    current_room: str,
    room_service: RoomService,
    gemini_service: GeminiService
) -> str:
    """
    Simple hook function for agent hooks: Auto-route on message send.
    
    Returns notification message to show user (empty if no routing).
    
    Usage in agent hook:
        notification = await on_message_hook(user, message, room, room_service, gemini_service)
        if notification:
            send_to_user(notification)
    """
    result = await auto_route_user(user, message, current_room, room_service, gemini_service)
    return result['notification']


async def periodic_room_check_hook(
    recent_messages: List[Dict[str, str]],
    room_service: RoomService,
    gemini_service: GeminiService
) -> Optional[str]:
    """
    Simple hook function for agent hooks: Periodic room creation check.
    
    Returns notification message if room was created (None otherwise).
    
    Usage in agent hook (call every N messages):
        notification = await periodic_room_check_hook(messages, room_service, gemini_service)
        if notification:
            broadcast_to_all(notification)
    """
    result = await check_and_create_room(recent_messages, room_service, gemini_service)
    return result['notification'] if result['created'] else None
