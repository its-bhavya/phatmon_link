"""
Tests for command handler functionality.

This module tests the CommandHandler class.
"""

import pytest
from backend.commands.handler import CommandHandler
from backend.rooms import RoomService
from backend.websocket.manager import WebSocketManager
from backend.database import User


class TestCommandHandler:
    """Tests for the CommandHandler class."""
    
    @pytest.fixture
    def room_service(self):
        """Create a RoomService instance with default rooms."""
        service = RoomService()
        service.create_default_rooms()
        return service
    
    @pytest.fixture
    def websocket_manager(self):
        """Create a WebSocketManager instance."""
        return WebSocketManager()
    
    @pytest.fixture
    def command_handler(self, room_service, websocket_manager):
        """Create a CommandHandler instance."""
        return CommandHandler(room_service, websocket_manager)
    
    @pytest.fixture
    def test_user(self):
        """Create a test user."""
        return User(username="testuser", password_hash="hash")
    
    def test_initialization(self, room_service, websocket_manager):
        """Test that CommandHandler initializes correctly."""
        handler = CommandHandler(room_service, websocket_manager)
        
        assert handler.room_service is room_service
        assert handler.websocket_manager is websocket_manager
        assert isinstance(handler.commands, dict)
        assert "help" in handler.commands
        assert "rooms" in handler.commands
        assert "users" in handler.commands
        assert "clear" in handler.commands
        assert "join" in handler.commands
    
    def test_help_command(self, command_handler, test_user):
        """Test that help command returns list of available commands."""
        response = command_handler.help_command(test_user)
        
        assert response["type"] == "system"
        assert "content" in response
        assert "/help" in response["content"]
        assert "/rooms" in response["content"]
        assert "/users" in response["content"]
        assert "/join" in response["content"]
        assert "/clear" in response["content"]
    
    def test_rooms_command(self, command_handler, test_user):
        """Test that rooms command returns room list with counts."""
        response = command_handler.rooms_command(test_user)
        
        assert response["type"] == "room_list"
        assert "content" in response
        assert "rooms" in response
        assert isinstance(response["rooms"], list)
        assert len(response["rooms"]) == 4
        
        # Check that all default rooms are present
        room_names = [room["name"] for room in response["rooms"]]
        assert "Lobby" in room_names
        assert "Techline" in room_names
        assert "Arcade Hall" in room_names
        assert "Support" in room_names
        
        # Check room structure
        for room in response["rooms"]:
            assert "name" in room
            assert "count" in room
            assert "description" in room
    
    def test_rooms_command_with_users(self, command_handler, test_user, room_service):
        """Test that rooms command shows correct user counts."""
        # Add users to rooms
        user1 = User(username="user1", password_hash="hash")
        user2 = User(username="user2", password_hash="hash")
        
        room_service.join_room(user1, "Lobby")
        room_service.join_room(user2, "Lobby")
        room_service.join_room(test_user, "Techline")
        
        response = command_handler.rooms_command(test_user)
        
        # Find Lobby and Techline in response
        rooms_dict = {room["name"]: room for room in response["rooms"]}
        
        assert rooms_dict["Lobby"]["count"] == 2
        assert rooms_dict["Techline"]["count"] == 1
        assert rooms_dict["Arcade Hall"]["count"] == 0
        assert rooms_dict["Support"]["count"] == 0
    
    def test_users_command_no_users(self, command_handler, test_user):
        """Test that users command returns empty list when no users connected."""
        response = command_handler.users_command(test_user)
        
        assert response["type"] == "user_list"
        assert "content" in response
        assert "users" in response
        assert isinstance(response["users"], list)
        assert len(response["users"]) == 0
        assert "No users currently online" in response["content"]
    
    def test_users_command_with_users(self, command_handler, test_user, websocket_manager):
        """Test that users command returns list of active users."""
        # Mock some active users by directly manipulating the manager
        # In real usage, this would be done through WebSocket connections
        from unittest.mock import Mock
        
        ws1 = Mock()
        ws2 = Mock()
        
        user1 = User(username="user1", password_hash="hash")
        user2 = User(username="user2", password_hash="hash")
        
        # Manually add to active connections for testing
        from backend.websocket.manager import ActiveUser
        websocket_manager.active_connections[ws1] = ActiveUser(ws1, user1, "Lobby")
        websocket_manager.active_connections[ws2] = ActiveUser(ws2, user2, "Techline")
        
        response = command_handler.users_command(test_user)
        
        assert response["type"] == "user_list"
        assert "users" in response
        assert len(response["users"]) == 2
        
        # Check user structure
        usernames = [user["username"] for user in response["users"]]
        assert "user1" in usernames
        assert "user2" in usernames
        
        # Check content includes usernames and rooms
        assert "user1" in response["content"]
        assert "user2" in response["content"]
        assert "Lobby" in response["content"]
        assert "Techline" in response["content"]
    
    def test_clear_command(self, command_handler, test_user):
        """Test that clear command returns clear signal."""
        response = command_handler.clear_command(test_user)
        
        assert response["type"] == "clear"
        assert "content" in response
    
    def test_join_command_success(self, command_handler, test_user, websocket_manager):
        """Test that join command returns success for valid room."""
        # Set user's current room
        from unittest.mock import Mock
        ws = Mock()
        from backend.websocket.manager import ActiveUser
        websocket_manager.active_connections[ws] = ActiveUser(ws, test_user, "Lobby")
        websocket_manager.user_websockets[test_user.username] = ws
        
        response = command_handler.join_command(test_user, "Techline")
        
        assert response["type"] == "join_room"
        assert response["room"] == "Techline"
        assert response["from_room"] == "Lobby"
        assert "room_description" in response
    
    def test_join_command_no_room_name(self, command_handler, test_user):
        """Test that join command returns error when no room name provided."""
        response = command_handler.join_command(test_user, None)
        
        assert response["type"] == "error"
        assert "specify a room name" in response["content"].lower()
    
    def test_join_command_empty_room_name(self, command_handler, test_user):
        """Test that join command returns error for empty room name."""
        response = command_handler.join_command(test_user, "   ")
        
        assert response["type"] == "error"
        assert "specify a room name" in response["content"].lower()
    
    def test_join_command_nonexistent_room(self, command_handler, test_user):
        """Test that join command returns error for nonexistent room."""
        response = command_handler.join_command(test_user, "Nonexistent")
        
        assert response["type"] == "error"
        assert "not found" in response["content"].lower()
        assert "Nonexistent" in response["content"]
    
    def test_join_command_already_in_room(self, command_handler, test_user, websocket_manager):
        """Test that join command returns error when already in target room."""
        # Set user's current room to Lobby
        from unittest.mock import Mock
        ws = Mock()
        from backend.websocket.manager import ActiveUser
        websocket_manager.active_connections[ws] = ActiveUser(ws, test_user, "Lobby")
        websocket_manager.user_websockets[test_user.username] = ws
        
        response = command_handler.join_command(test_user, "Lobby")
        
        assert response["type"] == "error"
        assert "already in" in response["content"].lower()
    
    def test_handle_command_help(self, command_handler, test_user):
        """Test that handle_command routes to help command."""
        response = command_handler.handle_command("help", test_user)
        
        assert response["type"] == "system"
        assert "/help" in response["content"]
    
    def test_handle_command_rooms(self, command_handler, test_user):
        """Test that handle_command routes to rooms command."""
        response = command_handler.handle_command("rooms", test_user)
        
        assert response["type"] == "room_list"
        assert "rooms" in response
    
    def test_handle_command_users(self, command_handler, test_user):
        """Test that handle_command routes to users command."""
        response = command_handler.handle_command("users", test_user)
        
        assert response["type"] == "user_list"
        assert "users" in response
    
    def test_handle_command_clear(self, command_handler, test_user):
        """Test that handle_command routes to clear command."""
        response = command_handler.handle_command("clear", test_user)
        
        assert response["type"] == "clear"
    
    def test_handle_command_join(self, command_handler, test_user, websocket_manager):
        """Test that handle_command routes to join command with args."""
        # Set user's current room
        from unittest.mock import Mock
        ws = Mock()
        from backend.websocket.manager import ActiveUser
        websocket_manager.active_connections[ws] = ActiveUser(ws, test_user, "Lobby")
        websocket_manager.user_websockets[test_user.username] = ws
        
        response = command_handler.handle_command("join", test_user, "Techline")
        
        assert response["type"] == "join_room"
        assert response["room"] == "Techline"
    
    def test_handle_command_invalid(self, command_handler, test_user):
        """Test that handle_command returns error for invalid command."""
        response = command_handler.handle_command("invalid", test_user)
        
        assert response["type"] == "error"
        assert "invalid command" in response["content"].lower()
        assert "/invalid" in response["content"]
    
    def test_handle_command_case_insensitive(self, command_handler, test_user):
        """Test that handle_command is case insensitive."""
        response1 = command_handler.handle_command("HELP", test_user)
        response2 = command_handler.handle_command("Help", test_user)
        response3 = command_handler.handle_command("help", test_user)
        
        assert response1["type"] == "system"
        assert response2["type"] == "system"
        assert response3["type"] == "system"
    
    def test_handle_command_with_whitespace(self, command_handler, test_user):
        """Test that handle_command handles whitespace in command."""
        response = command_handler.handle_command("  help  ", test_user)
        
        assert response["type"] == "system"
        assert "/help" in response["content"]
    
    def test_play_command_success_snake(self, command_handler, test_user, websocket_manager):
        """Test that play command launches snake game in Arcade Hall."""
        # Set user's current room to Arcade Hall
        from unittest.mock import Mock
        ws = Mock()
        from backend.websocket.manager import ActiveUser
        websocket_manager.active_connections[ws] = ActiveUser(ws, test_user, "Arcade Hall")
        websocket_manager.user_websockets[test_user.username] = ws
        
        response = command_handler.play_command(test_user, "snake")
        
        assert response["type"] == "launch_game"
        assert response["game"] == "snake"
        assert "Snake" in response["content"]
    
    def test_play_command_success_tetris(self, command_handler, test_user, websocket_manager):
        """Test that play command launches tetris game in Arcade Hall."""
        # Set user's current room to Arcade Hall
        from unittest.mock import Mock
        ws = Mock()
        from backend.websocket.manager import ActiveUser
        websocket_manager.active_connections[ws] = ActiveUser(ws, test_user, "Arcade Hall")
        websocket_manager.user_websockets[test_user.username] = ws
        
        response = command_handler.play_command(test_user, "tetris")
        
        assert response["type"] == "launch_game"
        assert response["game"] == "tetris"
        assert "Tetris" in response["content"]
    
    def test_play_command_success_breakout(self, command_handler, test_user, websocket_manager):
        """Test that play command launches breakout game in Arcade Hall."""
        # Set user's current room to Arcade Hall
        from unittest.mock import Mock
        ws = Mock()
        from backend.websocket.manager import ActiveUser
        websocket_manager.active_connections[ws] = ActiveUser(ws, test_user, "Arcade Hall")
        websocket_manager.user_websockets[test_user.username] = ws
        
        response = command_handler.play_command(test_user, "breakout")
        
        assert response["type"] == "launch_game"
        assert response["game"] == "breakout"
        assert "Breakout" in response["content"]
    
    def test_play_command_wrong_room(self, command_handler, test_user, websocket_manager):
        """Test that play command returns error when not in Arcade Hall."""
        # Set user's current room to Lobby
        from unittest.mock import Mock
        ws = Mock()
        from backend.websocket.manager import ActiveUser
        websocket_manager.active_connections[ws] = ActiveUser(ws, test_user, "Lobby")
        websocket_manager.user_websockets[test_user.username] = ws
        
        response = command_handler.play_command(test_user, "snake")
        
        assert response["type"] == "error"
        assert "only available in the Arcade Room" in response["content"]
    
    def test_play_command_invalid_game(self, command_handler, test_user, websocket_manager):
        """Test that play command returns error for invalid game name."""
        # Set user's current room to Arcade Hall
        from unittest.mock import Mock
        ws = Mock()
        from backend.websocket.manager import ActiveUser
        websocket_manager.active_connections[ws] = ActiveUser(ws, test_user, "Arcade Hall")
        websocket_manager.user_websockets[test_user.username] = ws
        
        response = command_handler.play_command(test_user, "pong")
        
        assert response["type"] == "error"
        assert "Unknown game" in response["content"]
        assert "pong" in response["content"]
        assert "snake" in response["content"]
        assert "tetris" in response["content"]
        assert "breakout" in response["content"]
    
    def test_play_command_no_game_name(self, command_handler, test_user):
        """Test that play command returns error when no game name provided."""
        response = command_handler.play_command(test_user, None)
        
        assert response["type"] == "error"
        assert "specify a game name" in response["content"].lower()
        assert "snake" in response["content"]
        assert "tetris" in response["content"]
        assert "breakout" in response["content"]
    
    def test_play_command_empty_game_name(self, command_handler, test_user):
        """Test that play command returns error for empty game name."""
        response = command_handler.play_command(test_user, "   ")
        
        assert response["type"] == "error"
        assert "specify a game name" in response["content"].lower()
    
    def test_play_command_case_insensitive(self, command_handler, test_user, websocket_manager):
        """Test that play command handles game names case insensitively."""
        # Set user's current room to Arcade Hall
        from unittest.mock import Mock
        ws = Mock()
        from backend.websocket.manager import ActiveUser
        websocket_manager.active_connections[ws] = ActiveUser(ws, test_user, "Arcade Hall")
        websocket_manager.user_websockets[test_user.username] = ws
        
        response1 = command_handler.play_command(test_user, "SNAKE")
        response2 = command_handler.play_command(test_user, "Snake")
        response3 = command_handler.play_command(test_user, "snake")
        
        assert response1["type"] == "launch_game"
        assert response2["type"] == "launch_game"
        assert response3["type"] == "launch_game"
        assert response1["game"] == "snake"
        assert response2["game"] == "snake"
        assert response3["game"] == "snake"
    
    def test_exit_game_command(self, command_handler, test_user):
        """Test that exit_game command returns exit signal."""
        response = command_handler.exit_game_command(test_user)
        
        assert response["type"] == "exit_game"
        assert "content" in response
    
    def test_handle_command_play(self, command_handler, test_user, websocket_manager):
        """Test that handle_command routes to play command with args."""
        # Set user's current room to Arcade Hall
        from unittest.mock import Mock
        ws = Mock()
        from backend.websocket.manager import ActiveUser
        websocket_manager.active_connections[ws] = ActiveUser(ws, test_user, "Arcade Hall")
        websocket_manager.user_websockets[test_user.username] = ws
        
        response = command_handler.handle_command("play", test_user, "snake")
        
        assert response["type"] == "launch_game"
        assert response["game"] == "snake"
    
    def test_handle_command_exit_game(self, command_handler, test_user):
        """Test that handle_command routes to exit_game command."""
        response = command_handler.handle_command("exit_game", test_user)
        
        assert response["type"] == "exit_game"
    
    def test_help_command_includes_game_commands(self, command_handler, test_user):
        """Test that help command includes game commands."""
        response = command_handler.help_command(test_user)
        
        assert response["type"] == "system"
        assert "/play" in response["content"]
        assert "/exit_game" in response["content"]
