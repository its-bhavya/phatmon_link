"""
Tests for room service functionality.

This module tests the RoomService class and Room model.
"""

import pytest
from backend.rooms import Room, RoomService
from backend.database import User


class TestRoomModel:
    """Tests for the Room model."""
    
    def test_room_creation(self):
        """Test that a room can be created with name and description."""
        room = Room(name="Test Room", description="A test room")
        
        assert room.name == "Test Room"
        assert room.description == "A test room"
        assert len(room.users) == 0
        assert room.created_at is not None
    
    def test_room_users_is_set(self):
        """Test that room.users is a set."""
        room = Room(name="Test", description="Test")
        
        assert isinstance(room.users, set)


class TestRoomService:
    """Tests for the RoomService class."""
    
    def test_initialization(self):
        """Test that RoomService initializes with empty rooms dict."""
        service = RoomService()
        
        assert isinstance(service.rooms, dict)
        assert len(service.rooms) == 0
    
    def test_create_default_rooms(self):
        """Test that default rooms are created correctly."""
        service = RoomService()
        service.create_default_rooms()
        
        # Check that all 5 default rooms exist (Lobby, Techline, Arcade Hall, Archives, Support)
        assert len(service.rooms) == 5
        assert "Lobby" in service.rooms
        assert "Techline" in service.rooms
        assert "Arcade Hall" in service.rooms
        assert "Archives" in service.rooms
        assert "Support" in service.rooms
        
        # Check room properties
        lobby = service.rooms["Lobby"]
        assert lobby.name == "Lobby"
        assert "gathering space" in lobby.description.lower()
        assert len(lobby.users) == 0
    
    def test_create_default_rooms_idempotent(self):
        """Test that calling create_default_rooms multiple times doesn't create duplicates."""
        service = RoomService()
        service.create_default_rooms()
        service.create_default_rooms()
        
        assert len(service.rooms) == 5
    
    def test_get_rooms(self):
        """Test that get_rooms returns list of all rooms."""
        service = RoomService()
        service.create_default_rooms()
        
        rooms = service.get_rooms()
        
        assert isinstance(rooms, list)
        assert len(rooms) == 5
        assert all(isinstance(room, Room) for room in rooms)
    
    def test_get_room(self):
        """Test that get_room retrieves a specific room."""
        service = RoomService()
        service.create_default_rooms()
        
        lobby = service.get_room("Lobby")
        
        assert lobby is not None
        assert lobby.name == "Lobby"
    
    def test_get_room_nonexistent(self):
        """Test that get_room returns None for nonexistent room."""
        service = RoomService()
        service.create_default_rooms()
        
        room = service.get_room("Nonexistent")
        
        assert room is None
    
    def test_join_room(self):
        """Test that a user can join a room."""
        service = RoomService()
        service.create_default_rooms()
        
        # Create a mock user
        user = User(username="testuser", password_hash="hash")
        
        result = service.join_room(user, "Lobby")
        
        assert result is True
        assert "testuser" in service.rooms["Lobby"].users
    
    def test_join_nonexistent_room(self):
        """Test that joining a nonexistent room returns False."""
        service = RoomService()
        service.create_default_rooms()
        
        user = User(username="testuser", password_hash="hash")
        
        result = service.join_room(user, "Nonexistent")
        
        assert result is False
    
    def test_leave_room(self):
        """Test that a user can leave a room."""
        service = RoomService()
        service.create_default_rooms()
        
        user = User(username="testuser", password_hash="hash")
        
        # Join then leave
        service.join_room(user, "Lobby")
        result = service.leave_room(user, "Lobby")
        
        assert result is True
        assert "testuser" not in service.rooms["Lobby"].users
    
    def test_leave_room_not_in(self):
        """Test that leaving a room the user isn't in returns False."""
        service = RoomService()
        service.create_default_rooms()
        
        user = User(username="testuser", password_hash="hash")
        
        result = service.leave_room(user, "Lobby")
        
        assert result is False
    
    def test_leave_nonexistent_room(self):
        """Test that leaving a nonexistent room returns False."""
        service = RoomService()
        service.create_default_rooms()
        
        user = User(username="testuser", password_hash="hash")
        
        result = service.leave_room(user, "Nonexistent")
        
        assert result is False
    
    def test_get_users_in_room(self):
        """Test that get_users_in_room returns list of usernames."""
        service = RoomService()
        service.create_default_rooms()
        
        user1 = User(username="user1", password_hash="hash")
        user2 = User(username="user2", password_hash="hash")
        
        service.join_room(user1, "Lobby")
        service.join_room(user2, "Lobby")
        
        users = service.get_users_in_room("Lobby")
        
        assert isinstance(users, list)
        assert len(users) == 2
        assert "user1" in users
        assert "user2" in users
    
    def test_get_users_in_empty_room(self):
        """Test that get_users_in_room returns empty list for empty room."""
        service = RoomService()
        service.create_default_rooms()
        
        users = service.get_users_in_room("Lobby")
        
        assert users == []
    
    def test_get_users_in_nonexistent_room(self):
        """Test that get_users_in_room returns empty list for nonexistent room."""
        service = RoomService()
        service.create_default_rooms()
        
        users = service.get_users_in_room("Nonexistent")
        
        assert users == []
    
    def test_get_room_count(self):
        """Test that get_room_count returns correct count."""
        service = RoomService()
        service.create_default_rooms()
        
        user1 = User(username="user1", password_hash="hash")
        user2 = User(username="user2", password_hash="hash")
        
        service.join_room(user1, "Lobby")
        service.join_room(user2, "Lobby")
        
        count = service.get_room_count("Lobby")
        
        assert count == 2
    
    def test_get_room_count_empty(self):
        """Test that get_room_count returns 0 for empty room."""
        service = RoomService()
        service.create_default_rooms()
        
        count = service.get_room_count("Lobby")
        
        assert count == 0
    
    def test_get_room_count_nonexistent(self):
        """Test that get_room_count returns 0 for nonexistent room."""
        service = RoomService()
        service.create_default_rooms()
        
        count = service.get_room_count("Nonexistent")
        
        assert count == 0
    
    def test_get_user_room(self):
        """Test that get_user_room finds which room a user is in."""
        service = RoomService()
        service.create_default_rooms()
        
        user = User(username="testuser", password_hash="hash")
        service.join_room(user, "Techline")
        
        room_name = service.get_user_room("testuser")
        
        assert room_name == "Techline"
    
    def test_get_user_room_not_in_any(self):
        """Test that get_user_room returns None if user isn't in any room."""
        service = RoomService()
        service.create_default_rooms()
        
        room_name = service.get_user_room("testuser")
        
        assert room_name is None
    
    def test_move_user(self):
        """Test that move_user moves a user between rooms."""
        service = RoomService()
        service.create_default_rooms()
        
        user = User(username="testuser", password_hash="hash")
        
        # Join Lobby
        service.join_room(user, "Lobby")
        assert "testuser" in service.rooms["Lobby"].users
        
        # Move to Techline
        result = service.move_user(user, "Lobby", "Techline")
        
        assert result is True
        assert "testuser" not in service.rooms["Lobby"].users
        assert "testuser" in service.rooms["Techline"].users
    
    def test_move_user_from_none(self):
        """Test that move_user works when from_room is None."""
        service = RoomService()
        service.create_default_rooms()
        
        user = User(username="testuser", password_hash="hash")
        
        result = service.move_user(user, None, "Lobby")
        
        assert result is True
        assert "testuser" in service.rooms["Lobby"].users
    
    def test_multiple_users_in_different_rooms(self):
        """Test that multiple users can be in different rooms simultaneously."""
        service = RoomService()
        service.create_default_rooms()
        
        user1 = User(username="user1", password_hash="hash")
        user2 = User(username="user2", password_hash="hash")
        user3 = User(username="user3", password_hash="hash")
        
        service.join_room(user1, "Lobby")
        service.join_room(user2, "Techline")
        service.join_room(user3, "Lobby")
        
        assert service.get_room_count("Lobby") == 2
        assert service.get_room_count("Techline") == 1
        assert service.get_room_count("Arcade Hall") == 0
        assert service.get_room_count("Archives") == 0
