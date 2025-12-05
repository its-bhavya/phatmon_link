"""
Room models for Obsidian BBS.

This module defines the Room data structure for managing chat rooms.
"""

from datetime import datetime
from typing import Set, List, Dict, Any
from collections import deque


class Room:
    """
    Room model representing a chat space in the BBS.
    
    Attributes:
        name: Unique room name
        description: Room description
        created_at: Timestamp when room was created
        users: Set of usernames currently in the room
        message_history: Recent message history (last 50 messages)
    """
    
    def __init__(self, name: str, description: str, max_history: int = 50):
        """
        Initialize a new room.
        
        Args:
            name: Room name
            description: Room description
            max_history: Maximum number of messages to keep in history
        """
        self.name = name
        self.description = description
        self.created_at = datetime.utcnow()
        self.users: Set[str] = set()
        self.message_history: deque = deque(maxlen=max_history)
    
    def add_message(self, message: Dict[str, Any]) -> None:
        """
        Add a message to the room's history.
        
        Args:
            message: Message dict with type, username, content, timestamp
        """
        self.message_history.append(message)
    
    def get_recent_messages(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent messages from the room history.
        
        Args:
            limit: Maximum number of messages to return
        
        Returns:
            List of recent messages (oldest first)
        """
        # Return last N messages
        messages = list(self.message_history)
        return messages[-limit:] if len(messages) > limit else messages
    
    def __repr__(self):
        return f"<Room(name='{self.name}', users={len(self.users)})>"
