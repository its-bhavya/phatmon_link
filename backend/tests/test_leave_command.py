"""
Tests for support room leave functionality.

This module tests the /leave command and support room leave handling.
"""

import pytest
from backend.commands.handler import CommandHandler
from backend.rooms.service import RoomService
from backend.support.room_service import SupportRoomService
from backend.websocket.manager import WebSocketManager
from backend.database import User


class TestLeaveCommand:
    """Test suite for /leave command functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.room_service = RoomService()
        self.room_service.create_default_rooms()
        self.websocket_manager = WebSocketManager()
        self.command_handler = CommandHandler(self.room_service, self.websocket_manager)
        self.support_room_service = SupportRoomService(self.room_service)
        
        # Create test user
        self.user = User(id=1, username="testuser", password_hash="hash")
    
    def test_leave_command_exists(self):
        """Test that leave command is registered."""
        assert "leave" in self.command_handler.commands
    
    def test_leave_command_returns_correct_type(self):
        """Test that leave command returns leave_support_room type."""
        # Mock a websocket connection
        from unittest.mock import MagicMock
        mock_websocket = MagicMock()
        
        # Add user to a room first
        self.room_service.join_room(self.user, "Lobby")
        
        # Simulate user connection in websocket manager
        from backend.websocket.manager import ActiveUser
        active_user = ActiveUser(
            websocket=mock_websocket,
            user=self.user,
            current_room="Lobby"
        )
        self.websocket_manager.active_connections[mock_websocket] = active_user
        self.websocket_manager.user_websockets[self.user.username] = mock_websocket
        
        result = self.command_handler.leave_command(self.user)
        
        assert result["type"] == "leave_support_room"
        assert "current_room" in result
        assert result["current_room"] == "Lobby"
    
    def test_leave_command_when_not_in_room(self):
        """Test leave command when user is not in any room."""
        result = self.command_handler.leave_command(self.user)
        
        assert result["type"] == "error"
        assert "not currently in any room" in result["content"]
    
    def test_help_command_includes_leave(self):
        """Test that help command includes /leave."""
        result = self.command_handler.help_command(self.user)
        
        assert "/leave" in result["content"]
        assert "Leave current support room" in result["content"]


class TestSupportRoomLeaveFlow:
    """Test suite for complete support room leave flow."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.room_service = RoomService()
        self.room_service.create_default_rooms()
        self.support_room_service = SupportRoomService(self.room_service)
        
        # Create test user
        self.user = User(id=1, username="testuser", password_hash="hash")
    
    def test_create_support_room_stores_previous_room(self):
        """Test that creating support room stores previous room."""
        # User starts in Lobby
        self.room_service.join_room(self.user, "Lobby")
        
        # Create support room
        support_room = self.support_room_service.create_support_room(
            self.user, 
            previous_room="Lobby"
        )
        
        # Verify previous room is stored
        assert self.support_room_service.get_previous_room(self.user.id) == "Lobby"
        assert self.support_room_service.is_support_room(support_room)
    
    def test_close_support_session_preserves_room(self):
        """Test that closing session preserves the room."""
        # Create support room
        support_room = self.support_room_service.create_support_room(
            self.user,
            previous_room="Lobby"
        )
        
        # Close session
        self.support_room_service.close_support_session(self.user.id)
        
        # Verify room still exists
        assert self.room_service.get_room(support_room) is not None
        
        # Verify user is no longer in active sessions
        assert self.support_room_service.get_support_room(self.user.id) is None
    
    def test_support_room_preserves_conversation_history(self):
        """Test that support room maintains conversation history."""
        # Create support room
        support_room_name = self.support_room_service.create_support_room(
            self.user,
            previous_room="Lobby"
        )
        
        # Get the room
        room = self.room_service.get_room(support_room_name)
        
        # Add messages to history
        room.add_message({
            "type": "support",
            "username": "Support Bot",
            "content": "Hello, I'm here to help.",
            "timestamp": "2024-01-01T00:00:00"
        })
        
        room.add_message({
            "type": "chat_message",
            "username": "testuser",
            "content": "I'm feeling sad.",
            "timestamp": "2024-01-01T00:01:00"
        })
        
        # Close session
        self.support_room_service.close_support_session(self.user.id)
        
        # Verify history is preserved
        room = self.room_service.get_room(support_room_name)
        messages = room.get_recent_messages()
        
        assert len(messages) == 2
        assert messages[0]["content"] == "Hello, I'm here to help."
        assert messages[1]["content"] == "I'm feeling sad."
    
    def test_user_can_return_to_support_room(self):
        """Test that user can return to support room after leaving."""
        # Create support room
        support_room_name = self.support_room_service.create_support_room(
            self.user,
            previous_room="Lobby"
        )
        
        # Add user to support room
        self.room_service.join_room(self.user, support_room_name)
        
        # Add a message
        room = self.room_service.get_room(support_room_name)
        room.add_message({
            "type": "support",
            "username": "Support Bot",
            "content": "How are you feeling?",
            "timestamp": "2024-01-01T00:00:00"
        })
        
        # User leaves support room
        self.room_service.leave_room(self.user, support_room_name)
        self.support_room_service.close_support_session(self.user.id)
        
        # User returns to Lobby
        self.room_service.join_room(self.user, "Lobby")
        
        # User returns to support room
        self.room_service.leave_room(self.user, "Lobby")
        self.room_service.join_room(self.user, support_room_name)
        
        # Verify room still exists with history
        room = self.room_service.get_room(support_room_name)
        assert room is not None
        messages = room.get_recent_messages()
        assert len(messages) == 1
        assert messages[0]["content"] == "How are you feeling?"
    
    def test_get_previous_room_returns_none_when_not_set(self):
        """Test that get_previous_room returns None when not set."""
        result = self.support_room_service.get_previous_room(999)
        assert result is None
    
    def test_is_support_room_identifies_support_rooms(self):
        """Test that is_support_room correctly identifies support rooms."""
        # Create support room
        support_room = self.support_room_service.create_support_room(self.user)
        
        # Test identification
        assert self.support_room_service.is_support_room(support_room) is True
        assert self.support_room_service.is_support_room("Lobby") is False
        assert self.support_room_service.is_support_room("Techline") is False
