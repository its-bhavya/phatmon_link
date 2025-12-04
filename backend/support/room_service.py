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
        Create a dedicated support room for a user.
        
        This method:
        1. Generates a unique room name
        2. Creates the room in the room service
        3. Tracks the support session
        4. Stores the user's previous room for return
        
        Args:
            user: User object for whom to create the support room
            previous_room: Optional name of room user was in before support
            
        Returns:
            Room name for the created support room
            
        Requirements:
        - 2.1: Create dedicated support room
        - 2.2: Ensure unique room naming
        - 2.5: Mark room as private
        """
        # Generate unique room name
        room_name = self._generate_unique_room_name(user)
        
        # Create the room with support-specific description
        description = f"Private support room for {user.username}"
        room = Room(name=room_name, description=description)
        
        # Add room to room service
        self.room_service.rooms[room_name] = room
        
        # Track the support session
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
        return room_name.startswith("support-")
    
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
        Fully cleanup a support room and all associated data.
        
        This should be called when a support room is no longer needed
        (e.g., user explicitly closes it or after extended inactivity).
        
        Args:
            user_id: User ID whose support room to cleanup
        """
        # Get room name before removing from tracking
        room_name = self.active_support_rooms.get(user_id)
        
        # Remove from tracking
        if user_id in self.active_support_rooms:
            del self.active_support_rooms[user_id]
        
        if user_id in self.previous_rooms:
            del self.previous_rooms[user_id]
        
        # Remove room from room service
        if room_name and room_name in self.room_service.rooms:
            del self.room_service.rooms[room_name]
    
    def _generate_unique_room_name(self, user: User) -> str:
        """
        Generate a unique room name for a support room.
        
        Format: support-{username}-{timestamp}-{counter}
        
        Args:
            user: User object for whom to generate room name
            
        Returns:
            Unique room name string
            
        Requirements:
        - 2.2: Ensure unique room naming
        """
        # Increment counter for uniqueness
        self._room_counter += 1
        
        # Use timestamp and counter for uniqueness
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        
        # Generate room name
        room_name = f"support-{user.username}-{timestamp}-{self._room_counter}"
        
        # Ensure uniqueness (should never happen with timestamp + counter, but be safe)
        while room_name in self.room_service.rooms:
            self._room_counter += 1
            room_name = f"support-{user.username}-{timestamp}-{self._room_counter}"
        
        return room_name
