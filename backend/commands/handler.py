"""
Command handler for Phantom Link BBS.

This module provides command parsing and execution for user commands.
Commands are prefixed with "/" and trigger system actions.
"""

from typing import Dict, Optional
from backend.database import User
from backend.rooms.service import RoomService
from backend.websocket.manager import WebSocketManager


class CommandHandler:
    """
    Command handler for processing user commands.
    
    This handler provides:
    - Command routing and execution
    - Help command listing available commands
    - Rooms command showing room list with user counts
    - Users command showing active users
    - Clear command for clearing terminal display
    - Join command for room switching
    - Error handling for invalid commands
    
    Attributes:
        room_service: RoomService instance for room operations
        websocket_manager: WebSocketManager instance for user queries
    """
    
    def __init__(self, room_service: RoomService, websocket_manager: WebSocketManager):
        """
        Initialize the command handler.
        
        Args:
            room_service: RoomService instance
            websocket_manager: WebSocketManager instance
        """
        self.room_service = room_service
        self.websocket_manager = websocket_manager
        
        # Command routing table
        self.commands = {
            "help": self.help_command,
            "status": self.status_command,
            "rooms": self.rooms_command,
            "users": self.users_command,
            "clear": self.clear_command,
            "join": self.join_command,
            "leave": self.leave_command,
            "play": self.play_command,
            "exit_game": self.exit_game_command,
            "replay": self.replay_command,
        }
    
    def handle_command(self, command: str, user: User, args: Optional[str] = None) -> dict:
        """
        Route and execute a command.
        
        Args:
            command: Command name (without the "/" prefix)
            user: User object executing the command
            args: Optional command arguments
            
        Returns:
            Response dictionary with type and content
            
        Requirements: 7.1, 7.5
        """
        # Normalize command to lowercase
        command = command.lower().strip()
        
        # Check if command exists
        if command not in self.commands:
            return self._error_response(f"Invalid command: /{command}. Type /help for available commands.")
        
        # Execute the command
        try:
            # Some commands need arguments (like join and play), others don't
            if command in ["join", "play"]:
                return self.commands[command](user, args)
            else:
                return self.commands[command](user)
        except Exception as e:
            return self._error_response(f"Error executing command: {str(e)}")
    
    def help_command(self, user: User) -> dict:
        """
        Return list of available commands with descriptions.
        
        Args:
            user: User object requesting help
            
        Returns:
            Response dictionary with command list
            
        Requirements: 7.1
        """
        help_text = """Available Commands:
  - /help          - Show this help message
  - /status        - Show your current room and connection info
  - /rooms         - List all available rooms with user counts
  - /users         - Show all active users and their current rooms
  - /join <room>   - Join a different room (e.g., /join Techline)
  - /leave         - Leave current support room and return to previous room
  - /clear         - Clear the terminal display
  - /play <game>   - Launch a game in Arcade Room (snake, tetris, breakout)
  - /exit_game     - Exit the current game and return to chat
  - /replay        - Replay the current game
  - /logout        - Disconnect and return to login screen
"""
        
        return {
            "type": "system",
            "content": help_text
        }
    
    def status_command(self, user: User) -> dict:
        """
        Show user's current status and room.
        
        Args:
            user: User object requesting status
            
        Returns:
            Response dictionary with status information
        """
        current_room = self.websocket_manager.get_user_room(user.username)
        active_users = self.websocket_manager.get_active_users()
        
        status_text = f"""Your Status:
  Username: {user.username}
  Current Room: {current_room}
  Total Active Users: {len(active_users)}
  """
        
        return {
            "type": "system",
            "content": status_text
        }
    
    def rooms_command(self, user: User) -> dict:
        """
        Return room list with user counts.
        
        Args:
            user: User object requesting room list
            
        Returns:
            Response dictionary with room list and counts
            
        Requirements: 7.2
        """
        rooms = self.room_service.get_rooms()
        
        # Build room list text
        room_lines = ["Available Rooms:"]
        for room in rooms:
            count = self.room_service.get_room_count(room.name)
            room_lines.append(f"  - {room.name} ({count} users) - {room.description}")
        
        return {
            "type": "room_list",
            "content": "\n".join(room_lines),
            "rooms": [
                {
                    "name": room.name,
                    "count": self.room_service.get_room_count(room.name),
                    "description": room.description
                }
                for room in rooms
            ]
        }
    
    def users_command(self, user: User) -> dict:
        """
        Return active users list with room assignments.
        
        Args:
            user: User object requesting user list
            
        Returns:
            Response dictionary with active users list
            
        Requirements: 7.3
        """
        active_users = self.websocket_manager.get_active_users()
        
        # Build user list text
        if not active_users:
            user_text = "No users currently online."
        else:
            user_lines = [f"Active Users ({len(active_users)}):"]
            for active_user in active_users:
                user_lines.append(f"  - {active_user['username']} - in {active_user['room']}")
            user_text = "\n".join(user_lines)
        
        return {
            "type": "user_list",
            "content": user_text,
            "users": active_users
        }
    
    def clear_command(self, user: User) -> dict:
        """
        Return clear signal to clear terminal display.
        
        Args:
            user: User object requesting clear
            
        Returns:
            Response dictionary with clear signal
            
        Requirements: 7.4
        """
        return {
            "type": "clear",
            "content": "Terminal cleared."
        }
    
    def join_command(self, user: User, room_name: Optional[str] = None) -> dict:
        """
        Handle room switching for a user.
        
        Args:
            user: User object requesting room change
            room_name: Name of room to join
            
        Returns:
            Response dictionary with success or error message
            
        Requirements: 7.2, 7.5
        """
        # Check if room name was provided
        if not room_name or not room_name.strip():
            return self._error_response("Please specify a room name. Usage: /join <room>")
        
        room_name = room_name.strip()
        
        # Check if room exists
        room = self.room_service.get_room(room_name)
        if not room:
            available_rooms = [r.name for r in self.room_service.get_rooms()]
            return self._error_response(
                f"Room '{room_name}' not found. Available rooms: {', '.join(available_rooms)}"
            )
        
        # Get user's current room
        current_room = self.websocket_manager.get_user_room(user.username)
        
        # Check if user is already in that room
        if current_room == room_name:
            return self._error_response(f"You are already in {room_name}.")
        
        # Return success response with room change info
        # The actual room change will be handled by the WebSocket endpoint
        return {
            "type": "join_room",
            "content": f"Joining {room_name}...",
            "room": room_name,
            "from_room": current_room,
            "room_description": room.description
        }
    
    def leave_command(self, user: User) -> dict:
        """
        Handle leaving a support room and returning to previous room.
        
        This command is specifically for leaving support rooms. Users can
        return to their previous room before entering support.
        
        Args:
            user: User object requesting to leave
            
        Returns:
            Response dictionary with leave_support_room signal
            
        Requirements: 10.1, 10.2, 10.3, 10.4
        """
        # Get user's current room
        current_room = self.websocket_manager.get_user_room(user.username)
        
        # Check if user is in a room
        if not current_room:
            return self._error_response("You are not currently in any room.")
        
        # The actual support room check and previous room retrieval
        # will be handled by the WebSocket endpoint which has access
        # to the support_room_service
        return {
            "type": "leave_support_room",
            "content": "Leaving support room...",
            "current_room": current_room
        }
    
    def play_command(self, user: User, game_name: Optional[str] = None) -> dict:
        """
        Handle game launch command.
        
        This command launches a game in the Arcade Room. Games can only be
        launched when the user is in the Arcade Room (Arcade Hall).
        
        Args:
            user: User object requesting to play a game
            game_name: Name of the game to launch (snake, tetris, breakout)
            
        Returns:
            Response dictionary with launch_game signal or error
            
        Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
        """
        # Check if game name was provided
        if not game_name or not game_name.strip():
            return self._error_response(
                "Please specify a game name. Usage: /play <game>\n"
                "Available games: snake, tetris, breakout"
            )
        
        game_name = game_name.strip().lower()
        
        # Get user's current room
        current_room = self.websocket_manager.get_user_room(user.username)
        
        # Check if user is in Arcade Room (Arcade Hall)
        if current_room != "Arcade Hall":
            return self._error_response(
                "Games are only available in the Arcade Room. "
                "Use /join Arcade Hall to access games."
            )
        
        # Validate game name
        valid_games = ["snake", "tetris", "breakout"]
        if game_name not in valid_games:
            return self._error_response(
                f"Unknown game: {game_name}. Available games: {', '.join(valid_games)}"
            )
        
        # Return success response with game launch info
        return {
            "type": "launch_game",
            "content": f"Launching {game_name.capitalize()}...",
            "game": game_name
        }
    
    def exit_game_command(self, user: User) -> dict:
        """
        Handle game exit command.
        
        This command exits the current game and returns the user to the
        Arcade Room chat interface.
        
        Args:
            user: User object requesting to exit game
            
        Returns:
            Response dictionary with exit_game signal
            
        Requirements: 4.2
        """
        # Return exit game signal
        # The frontend will handle the actual game termination
        return {
            "type": "exit_game",
            "content": "Exiting game..."
        }
    
    def replay_command(self, user: User) -> dict:
        """
        Handle game replay command.
        
        This command replays the current game by restarting it.
        
        Args:
            user: User object requesting to replay game
            
        Returns:
            Response dictionary with replay_game signal
        """
        # Return replay game signal
        # The frontend will handle restarting the game
        return {
            "type": "replay_game",
            "content": "Replaying game..."
        }
    
    def _error_response(self, message: str) -> dict:
        """
        Create an error response dictionary.
        
        Args:
            message: Error message
            
        Returns:
            Error response dictionary
        """
        return {
            "type": "error",
            "content": message
        }
