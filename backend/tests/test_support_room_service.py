"""
Tests for support room service functionality.

This module tests the SupportRoomService class for managing dedicated support rooms.
"""

import pytest
from backend.support.room_service import SupportRoomService
from backend.rooms.service import RoomService
from backend.database import User


class TestSupportRoomService:
    """Tests for the SupportRoomService class."""
    
    def test_initialization(self):
        """Test that SupportRoomService initializes correctly."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        assert support_service.room_service is room_service
        assert isinstance(support_service.active_support_rooms, dict)
        assert len(support_service.active_support_rooms) == 0
        assert isinstance(support_service.previous_rooms, dict)
        assert len(support_service.previous_rooms) == 0
        assert support_service._room_counter == 0
    
    def test_create_support_room(self):
        """Test that a support room can be created for a user."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        user = User(username="testuser", password_hash="hash")
        user.id = 1
        
        room_name = support_service.create_support_room(user)
        
        # Check room name format
        assert room_name.startswith("support-testuser-")
        
        # Check room was created in room service
        assert room_name in room_service.rooms
        
        # Check room is tracked as active
        assert support_service.active_support_rooms[user.id] == room_name
        
        # Check room description
        room = room_service.get_room(room_name)
        assert room is not None
        assert "testuser" in room.description
        assert "Private support room" in room.description
    
    def test_create_support_room_with_previous_room(self):
        """Test that previous room is stored when creating support room."""
        room_service = RoomService()
        room_service.create_default_rooms()
        support_service = SupportRoomService(room_service)
        
        user = User(username="testuser", password_hash="hash")
        user.id = 1
        
        room_name = support_service.create_support_room(user, previous_room="Lobby")
        
        # Check previous room is stored
        assert support_service.previous_rooms[user.id] == "Lobby"
    
    def test_unique_room_naming(self):
        """Test that multiple support rooms have unique names."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        user1 = User(username="user1", password_hash="hash")
        user1.id = 1
        user2 = User(username="user2", password_hash="hash")
        user2.id = 2
        user3 = User(username="user1", password_hash="hash")  # Same username as user1
        user3.id = 3
        
        room1 = support_service.create_support_room(user1)
        room2 = support_service.create_support_room(user2)
        room3 = support_service.create_support_room(user3)
        
        # All room names should be unique
        assert room1 != room2
        assert room1 != room3
        assert room2 != room3
        
        # All rooms should exist
        assert room1 in room_service.rooms
        assert room2 in room_service.rooms
        assert room3 in room_service.rooms
    
    def test_get_support_room(self):
        """Test that get_support_room retrieves the correct room."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        user = User(username="testuser", password_hash="hash")
        user.id = 1
        
        created_room = support_service.create_support_room(user)
        retrieved_room = support_service.get_support_room(user.id)
        
        assert retrieved_room == created_room
    
    def test_get_support_room_nonexistent(self):
        """Test that get_support_room returns None for user without support room."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        result = support_service.get_support_room(999)
        
        assert result is None
    
    def test_is_support_room(self):
        """Test that is_support_room correctly identifies support rooms."""
        room_service = RoomService()
        room_service.create_default_rooms()
        support_service = SupportRoomService(room_service)
        
        user = User(username="testuser", password_hash="hash")
        user.id = 1
        
        support_room = support_service.create_support_room(user)
        
        # Support room should be identified
        assert support_service.is_support_room(support_room) is True
        
        # Regular rooms should not be identified as support rooms
        assert support_service.is_support_room("Lobby") is False
        assert support_service.is_support_room("Techline") is False
    
    def test_get_previous_room(self):
        """Test that get_previous_room retrieves stored previous room."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        user = User(username="testuser", password_hash="hash")
        user.id = 1
        
        support_service.create_support_room(user, previous_room="Techline")
        
        previous = support_service.get_previous_room(user.id)
        
        assert previous == "Techline"
    
    def test_get_previous_room_none(self):
        """Test that get_previous_room returns None when no previous room stored."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        user = User(username="testuser", password_hash="hash")
        user.id = 1
        
        support_service.create_support_room(user)
        
        previous = support_service.get_previous_room(user.id)
        
        assert previous is None
    
    def test_close_support_session(self):
        """Test that close_support_session removes from active tracking but preserves room."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        user = User(username="testuser", password_hash="hash")
        user.id = 1
        
        room_name = support_service.create_support_room(user)
        
        # Close session
        support_service.close_support_session(user.id)
        
        # Should be removed from active tracking
        assert user.id not in support_service.active_support_rooms
        
        # But room should still exist
        assert room_name in room_service.rooms
    
    def test_cleanup_support_room(self):
        """Test that cleanup_support_room fully removes room and tracking."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        user = User(username="testuser", password_hash="hash")
        user.id = 1
        
        room_name = support_service.create_support_room(user, previous_room="Lobby")
        
        # Cleanup
        support_service.cleanup_support_room(user.id)
        
        # Should be removed from all tracking
        assert user.id not in support_service.active_support_rooms
        assert user.id not in support_service.previous_rooms
        
        # Room should be deleted
        assert room_name not in room_service.rooms
    
    def test_cleanup_support_room_nonexistent(self):
        """Test that cleanup_support_room handles nonexistent user gracefully."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        # Should not raise an error
        support_service.cleanup_support_room(999)
    
    def test_room_counter_increments(self):
        """Test that room counter increments for uniqueness."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        user = User(username="testuser", password_hash="hash")
        user.id = 1
        
        initial_counter = support_service._room_counter
        
        support_service.create_support_room(user)
        
        assert support_service._room_counter == initial_counter + 1
    
    def test_multiple_support_sessions(self):
        """Test that multiple users can have concurrent support sessions."""
        room_service = RoomService()
        support_service = SupportRoomService(room_service)
        
        user1 = User(username="user1", password_hash="hash")
        user1.id = 1
        user2 = User(username="user2", password_hash="hash")
        user2.id = 2
        user3 = User(username="user3", password_hash="hash")
        user3.id = 3
        
        room1 = support_service.create_support_room(user1, previous_room="Lobby")
        room2 = support_service.create_support_room(user2, previous_room="Techline")
        room3 = support_service.create_support_room(user3, previous_room="Arcade Hall")
        
        # All sessions should be tracked
        assert len(support_service.active_support_rooms) == 3
        assert support_service.active_support_rooms[1] == room1
        assert support_service.active_support_rooms[2] == room2
        assert support_service.active_support_rooms[3] == room3
        
        # All previous rooms should be tracked
        assert support_service.previous_rooms[1] == "Lobby"
        assert support_service.previous_rooms[2] == "Techline"
        assert support_service.previous_rooms[3] == "Arcade Hall"
        
        # All rooms should exist
        assert room1 in room_service.rooms
        assert room2 in room_service.rooms
        assert room3 in room_service.rooms
