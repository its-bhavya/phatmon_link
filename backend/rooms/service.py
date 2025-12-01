"""
Room service for Phantom Link BBS.

This module provides room management functionality including:
- Creating and managing chat rooms
- User-room associations
- Room state management
"""

from typing import Dict, List, Optional, Set
from backend.rooms.models import Room
from backend.database import User


class RoomService:
    """
    Room service handling room creation, user assignments, and room state.
    
    This service provides:
    - Default room creation (Lobby, Techline, Arcade Hall, Archives)
    - Room listing and retrieval
    - User joining and leaving rooms
    - Room member queries
    """
    
    def __init__(self):
        """
        Initialize the room service with empty room dictionary.
        """
        self.rooms: Dict[str, Room] = {}
    
    def create_default_rooms(self) -> None:
        """
        Create the four default rooms for the BBS.
        
        Default rooms:
        - Lobby: Main gathering space, default entry point
        - Techline: Technology and programming discussions
        - Arcade Hall: Gaming and entertainment
        - Archives: Historical BBS content and nostalgia
        
        This method is idempotent - calling it multiple times won't create duplicates.
        """
        default_rooms = [
            ("Lobby", "Main gathering space - Welcome to Gatekeeper!"),
            ("Techline", "Technology and programming discussions"),
            ("Arcade Hall", "Gaming and entertainment zone"),
            ("Archives", "Historical BBS content and nostalgia")
        ]
        
        for name, description in default_rooms:
            if name not in self.rooms:
                self.rooms[name] = Room(name=name, description=description)
    
    def get_rooms(self) -> List[Room]:
        """
        Get a list of all available rooms.
        
        Returns:
            List of Room objects
        """
        return list(self.rooms.values())
    
    def get_room(self, name: str) -> Optional[Room]:
        """
        Get a specific room by name.
        
        Args:
            name: Room name to retrieve
            
        Returns:
            Room object if found, None otherwise
        """
        return self.rooms.get(name)
    
    def join_room(self, user: User, room_name: str) -> bool:
        """
        Add a user to a room.
        
        Args:
            user: User object to add to room
            room_name: Name of room to join
            
        Returns:
            True if successful, False if room doesn't exist
        """
        room = self.get_room(room_name)
        if not room:
            return False
        
        room.users.add(user.username)
        return True
    
    def leave_room(self, user: User, room_name: str) -> bool:
        """
        Remove a user from a room.
        
        Args:
            user: User object to remove from room
            room_name: Name of room to leave
            
        Returns:
            True if successful, False if room doesn't exist or user wasn't in room
        """
        room = self.get_room(room_name)
        if not room:
            return False
        
        if user.username in room.users:
            room.users.remove(user.username)
            return True
        
        return False
    
    def get_users_in_room(self, room_name: str) -> List[str]:
        """
        Get list of usernames currently in a room.
        
        Args:
            room_name: Name of room to query
            
        Returns:
            List of usernames in the room, empty list if room doesn't exist
        """
        room = self.get_room(room_name)
        if not room:
            return []
        
        return list(room.users)
    
    def get_room_count(self, room_name: str) -> int:
        """
        Get the number of users currently in a room.
        
        Args:
            room_name: Name of room to query
            
        Returns:
            Number of users in the room, 0 if room doesn't exist
        """
        room = self.get_room(room_name)
        if not room:
            return 0
        
        return len(room.users)
    
    def get_user_room(self, username: str) -> Optional[str]:
        """
        Find which room a user is currently in.
        
        Args:
            username: Username to search for
            
        Returns:
            Room name if user is found, None otherwise
        """
        for room in self.rooms.values():
            if username in room.users:
                return room.name
        
        return None
    
    def move_user(self, user: User, from_room: str, to_room: str) -> bool:
        """
        Move a user from one room to another.
        
        This is a convenience method that combines leave_room and join_room.
        
        Args:
            user: User object to move
            from_room: Name of room to leave
            to_room: Name of room to join
            
        Returns:
            True if successful, False if either room doesn't exist
        """
        # Leave current room (if in one)
        if from_room:
            self.leave_room(user, from_room)
        
        # Join new room
        return self.join_room(user, to_room)
