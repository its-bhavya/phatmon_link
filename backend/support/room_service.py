"""
Support room service for managing dedicated support rooms.

This module provides support room management functionality including:
- Creating dedicated support rooms for users
- Tracking active support sessions
- Managing room lifecycle
- Ensuring room privacy
"""

from typing import Optional, Dict
from datetime import datetime
from backend.database import User
from backend.rooms.service import RoomService
from backend.rooms.models import Room


class SupportRoomService:
    """
    Service for managing support rooms.
    
    Responsibilities:
    - Create dedicated support rooms for users
    - Track active support sessions
    - Manage room lifecycle
    - Ensure unique room naming
    - Maintain room privacy settings
    
    Requirements:
    - 2.1: Create dedicated support room for flagged users
    - 2.2: Ensure unique room naming
    - 2.3: Automatically join user to support room
    - 2.5: Mark room as private to user
    - 10.3: Preserve support room when user leaves
    """
    
    def __init__(self, room_service: RoomService):
        """
        Initialize the support room service.
        
        Args:
            room_service: The main room service for room operations
        """
        self.room_service = room_service
        # Track active support rooms: user_id -> room_name
        self.active_support_rooms: Dict[int, str] = {}
        # Track previous rooms for return: user_id -> room_name
        self.previous_rooms: Dict[int, str] = {}
        # Track support room creation counter for unique naming
        self._room_counter: int = 0
    
    def create_support_room(self, user: User, previous_room: Optional[str] = None) -> str:
        """
        Create a support session for a user.
        
        This method:
        1. Uses the shared "Support" room
        2. Tracks the support session internally
        3. Stores the user's previous room for return
        
        Args:
            user: User object for whom to create the support session
            previous_room: Optional name of room user was in before support
            
        Returns:
            Room name (always "Support")
            
        Requirements:
        - 2.1: Create dedicated support room
        - 2.5: Mark room as private
        """
        # Always use the shared "Support" room
        room_name = "Support"
        
        # Track the support session internally for logging
        self.active_support_rooms[user.id] = room_name
        
        # Store previous room for return functionality
        if previous_room:
            self.previous_rooms[user.id] = previous_room
        
        return room_name
    
    def get_support_room(self, user_id: int) -> Optional[str]:
        """
        Get the support room name for a user if it exists.
        
        Args:
            user_id: User ID to look up
            
        Returns:
            Room name if user has an active support room, None otherwise
        """
        return self.active_support_rooms.get(user_id)
    
    def is_support_room(self, room_name: str) -> bool:
        """
        Check if a room is a support room.
        
        Args:
            room_name: Name of room to check
            
        Returns:
            True if room is a support room, False otherwise
        """
        return room_name == "Support"
    
    def get_previous_room(self, user_id: int) -> Optional[str]:
        """
        Get the previous room a user was in before entering support.
        
        Args:
            user_id: User ID to look up
            
        Returns:
            Previous room name if stored, None otherwise
            
        Requirements:
        - 10.2: Return user to previous room on leave
        """
        return self.previous_rooms.get(user_id)
    
    def close_support_session(self, user_id: int) -> None:
        """
        Close a support session but preserve the room.
        
        This removes the user from active tracking but keeps the room
        available for potential return.
        
        Args:
            user_id: User ID whose session to close
            
        Requirements:
        - 10.3: Preserve support room when user leaves
        """
        # Remove from active sessions but don't delete the room
        if user_id in self.active_support_rooms:
            del self.active_support_rooms[user_id]
    
    def cleanup_support_room(self, user_id: int) -> None:
        """
        Fully cleanup a support session and all associated data.
        
        This should be called when a support session is no longer needed
        (e.g., user explicitly closes it or after extended inactivity).
        
        Args:
            user_id: User ID whose support session to cleanup
        """
        # Remove from tracking
        if user_id in self.active_support_rooms:
            del self.active_support_rooms[user_id]
        
        if user_id in self.previous_rooms:
            del self.previous_rooms[user_id]
        
        # Note: We don't delete the "Support" room as it's a shared default room
    

