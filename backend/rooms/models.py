"""
Room models for Phantom Link BBS.

This module defines the Room data structure for managing chat rooms.
"""

from datetime import datetime
from typing import Set


class Room:
    """
    Room model representing a chat space in the BBS.
    
    Attributes:
        name: Unique room name
        description: Room description
        created_at: Timestamp when room was created
        users: Set of usernames currently in the room
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize a new room.
        
        Args:
            name: Room name
            description: Room description
        """
        self.name = name
        self.description = description
        self.created_at = datetime.utcnow()
        self.users: Set[str] = set()
    
    def __repr__(self):
        return f"<Room(name='{self.name}', users={len(self.users)})>"
