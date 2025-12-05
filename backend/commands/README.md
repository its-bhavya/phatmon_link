# Command Handler Module

## Overview

The Command Handler module provides command parsing, routing, and execution for user commands in the Obsidian BBS system. Commands are prefixed with `/` and trigger system actions such as navigation, information display, and session management.

## Module: `backend/commands/handler.py`

### Class: `CommandHandler`

The main class responsible for processing and executing user commands.

#### Constructor

```python
def __init__(self, room_service: RoomService, websocket_manager: WebSocketManager)
```

**Parameters:**
- `room_service` (RoomService): Instance of RoomService for room operations
- `websocket_manager` (WebSocketManager): Instance of WebSocketManager for user queries

**Description:**
Initializes the command handler with required service dependencies and sets up the command routing table.

**Example:**
```python
from backend.rooms.service import RoomService
from backend.websocket.manager import WebSocketManager
from backend.commands.handler import CommandHandler

room_service = RoomService()
websocket_manager = WebSocketManager()
command_handler = CommandHandler(room_service, websocket_manager)
```

---

### Methods

#### `handle_command(command: str, user: User, args: Optional[str] = None) -> dict`

Routes and executes a command.

**Parameters:**
- `command` (str): Command name without the "/" prefix (e.g., "help", "rooms")
- `user` (User): User object executing the command
- `args` (Optional[str]): Optional command arguments (e.g., room name for /join)

**Returns:**
- `dict`: Response dictionary with the following structure:
  ```python
  {
      "type": str,      # Message type: "system", "error", "room_list", etc.
      "content": str,   # Response content to display
      # Additional fields depending on command type
  }
  ```

**Raises:**
- Returns error response dict if command is invalid or execution fails

**Requirements:** 7.1, 7.5

**Example:**
```python
from backend.database import User

user = User(id=1, username="testuser")

# Execute help command
response = command_handler.handle_command("help", user)
print(response["content"])  # Displays help text

# Execute join command with arguments
response = command_handler.handle_command("join", user, "Techline")
print(response["room"])  # "Techline"

# Invalid command
response = command_handler.handle_command("invalid", user)
print(response["type"])  # "error"
```

---

#### `help_command(user: User) -> dict`

Returns list of available commands with descriptions.

**Parameters:**
- `user` (User): User object requesting help

**Returns:**
- `dict`: Response dictionary containing:
  ```python
  {
      "type": "system",
      "content": str  # Formatted help text with all commands
  }
  ```

**Requirements:** 7.1

**Example:**
```python
response = command_handler.help_command(user)
print(response["content"])
# Output:
# Available Commands:
#
#   /help          - Show this help message
#   /rooms         - List all available rooms with user counts
#   /users         - Show all active users and their current rooms
#   /join <room>   - Join a different room (e.g., /join Techline)
#   /clear         - Clear the terminal display
#   /logout        - Disconnect and return to login screen
```

---

#### `rooms_command(user: User) -> dict`

Returns room list with user counts.

**Parameters:**
- `user` (User): User object requesting room list

**Returns:**
- `dict`: Response dictionary containing:
  ```python
  {
      "type": "room_list",
      "content": str,  # Formatted room list text
      "rooms": [       # Structured room data
          {
              "name": str,
              "count": int,
              "description": str
          },
          ...
      ]
  }
  ```

**Requirements:** 7.2

**Example:**
```python
response = command_handler.rooms_command(user)
print(response["content"])
# Output:
# Available Rooms:
#   Lobby (3 users) - Main gathering space
#   Techline (1 users) - Technology discussions
#   Arcade Hall (0 users) - Gaming and entertainment

# Access structured data
for room in response["rooms"]:
    print(f"{room['name']}: {room['count']} users")
```

---

#### `users_command(user: User) -> dict`

Returns active users list with room assignments.

**Parameters:**
- `user` (User): User object requesting user list

**Returns:**
- `dict`: Response dictionary containing:
  ```python
  {
      "type": "user_list",
      "content": str,  # Formatted user list text
      "users": [       # Structured user data
          {
              "username": str,
              "room": str
          },
          ...
      ]
  }
  ```

**Requirements:** 7.3

**Example:**
```python
response = command_handler.users_command(user)
print(response["content"])
# Output:
# Active Users (3):
#   alice - in Lobby
#   bob - in Techline
#   charlie - in Lobby

# Access structured data
for active_user in response["users"]:
    print(f"{active_user['username']} is in {active_user['room']}")
```

---

#### `clear_command(user: User) -> dict`

Returns clear signal to clear terminal display.

**Parameters:**
- `user` (User): User object requesting clear

**Returns:**
- `dict`: Response dictionary containing:
  ```python
  {
      "type": "clear",
      "content": "Terminal cleared."
  }
  ```

**Requirements:** 7.4

**Example:**
```python
response = command_handler.clear_command(user)
# Frontend should clear the terminal display when receiving type="clear"
```

---

#### `join_command(user: User, room_name: Optional[str] = None) -> dict`

Handles room switching for a user.

**Parameters:**
- `user` (User): User object requesting room change
- `room_name` (Optional[str]): Name of room to join

**Returns:**
- `dict`: Response dictionary containing:
  ```python
  {
      "type": "join_room",
      "content": str,              # Status message
      "room": str,                 # Target room name
      "from_room": str,            # Current room name
      "room_description": str      # Description of target room
  }
  ```
  
  Or error response if room doesn't exist or no room name provided:
  ```python
  {
      "type": "error",
      "content": str  # Error message
  }
  ```

**Requirements:** 7.2, 7.5

**Example:**
```python
# Successful room join
response = command_handler.join_command(user, "Techline")
print(response["type"])  # "join_room"
print(response["room"])  # "Techline"
print(response["from_room"])  # "Lobby"

# Missing room name
response = command_handler.join_command(user, None)
print(response["type"])  # "error"
print(response["content"])  # "Please specify a room name..."

# Invalid room
response = command_handler.join_command(user, "NonExistent")
print(response["type"])  # "error"
print(response["content"])  # "Room 'NonExistent' not found..."

# Already in room
response = command_handler.join_command(user, "Lobby")
print(response["type"])  # "error"
print(response["content"])  # "You are already in Lobby."
```

---

## Command Routing Table

The CommandHandler maintains an internal routing table that maps command names to handler methods:

```python
self.commands = {
    "help": self.help_command,
    "rooms": self.rooms_command,
    "users": self.users_command,
    "clear": self.clear_command,
    "join": self.join_command,
}
```

Commands are case-insensitive and automatically normalized to lowercase.

---

## Usage in WebSocket Handler

The CommandHandler is typically used within the WebSocket message handling loop:

```python
from backend.commands.handler import CommandHandler

# In WebSocket endpoint
command_handler = app.state.command_handler

# When receiving a command message
if message_type == "command":
    command = data.get("command")
    args = data.get("args")
    
    # Execute command
    response = command_handler.handle_command(command, user, args)
    
    # Send response back to user
    await websocket_manager.send_to_user(websocket, response)
```

---

## Available Commands

### `/help`
Displays a list of all available commands with descriptions.

**Usage:** `/help`

**Response Type:** `system`

**Example Output:**
```
Available Commands:

  /help          - Show this help message
  /rooms         - List all available rooms with user counts
  /users         - Show all active users and their current rooms
  /join <room>   - Join a different room (e.g., /join Techline)
  /clear         - Clear the terminal display
  /logout        - Disconnect and return to login screen
```

---

### `/rooms`
Lists all available rooms with current user counts and descriptions.

**Usage:** `/rooms`

**Response Type:** `room_list`

**Example Output:**
```
Available Rooms:
  Lobby (5 users) - Main gathering space
  Techline (2 users) - Technology discussions
  Arcade Hall (0 users) - Gaming and entertainment
  Support (0 users) - Private space for emotional support
```

---

### `/users`
Shows all active users and their current room assignments.

**Usage:** `/users`

**Response Type:** `user_list`

**Example Output:**
```
Active Users (7):
  alice - in Lobby
  bob - in Techline
  charlie - in Lobby
  eve - in Lobby
  frank - in Techline
  grace - in Arcade Hall
  henry - in Lobby
```

---

### `/join <room>`
Switches the user to a different room.

**Usage:** `/join <room_name>`

**Arguments:**
- `room_name` (required): Name of the room to join (case-sensitive)

**Response Type:** `join_room` (success) or `error` (failure)

**Examples:**
```
/join Techline          # Join the Techline room
/join Arcade Hall       # Join the Arcade Hall room
/join Lobby             # Return to the Lobby
```

**Error Cases:**
- No room name provided: "Please specify a room name. Usage: /join <room>"
- Room doesn't exist: "Room 'XYZ' not found. Available rooms: Lobby, Techline, ..."
- Already in room: "You are already in Lobby."

---

### `/clear`
Clears the terminal display.

**Usage:** `/clear`

**Response Type:** `clear`

**Note:** The actual clearing is handled by the frontend when it receives the `clear` message type.

---

### `/logout`
Disconnects the user and returns them to the login screen.

**Usage:** `/logout`

**Response Type:** Handled by frontend (not a CommandHandler command)

**Note:** This command is handled client-side in `frontend/js/main.js` and triggers:
1. WebSocket disconnection
2. JWT token removal from localStorage
3. Page reload to show login screen

---

## Error Handling

The CommandHandler provides consistent error handling:

1. **Invalid Command:** Returns error response with available commands suggestion
2. **Missing Arguments:** Returns error response with usage instructions
3. **Execution Errors:** Catches exceptions and returns error response

**Error Response Format:**
```python
{
    "type": "error",
    "content": "Error message describing what went wrong"
}
```

---

## Testing

The CommandHandler is tested in `backend/tests/test_command_handler.py`:

```python
import pytest
from backend.commands.handler import CommandHandler
from backend.rooms.service import RoomService
from backend.websocket.manager import WebSocketManager
from backend.database import User

def test_help_command():
    room_service = RoomService()
    websocket_manager = WebSocketManager()
    handler = CommandHandler(room_service, websocket_manager)
    
    user = User(id=1, username="testuser")
    response = handler.help_command(user)
    
    assert response["type"] == "system"
    assert "/help" in response["content"]
    assert "/logout" in response["content"]

def test_join_command_success():
    room_service = RoomService()
    room_service.create_default_rooms()
    websocket_manager = WebSocketManager()
    handler = CommandHandler(room_service, websocket_manager)
    
    user = User(id=1, username="testuser")
    response = handler.join_command(user, "Techline")
    
    assert response["type"] == "join_room"
    assert response["room"] == "Techline"
```

Run tests with:
```bash
pytest backend/tests/test_command_handler.py -v
```

---

## Integration with Frontend

The frontend handles commands in `frontend/js/main.js`:

```javascript
function handleCommandSubmit(command, args, fullInput) {
    switch (command) {
        case 'clear':
            // Client-side clear
            chatDisplay.clear();
            break;
            
        case 'logout':
            // Client-side logout
            logout();
            break;
            
        default:
            // Send to server
            wsClient.send({
                type: 'command',
                command: command,
                args: args
            });
            break;
    }
}
```

---

## Requirements Mapping

The CommandHandler implements the following requirements:

- **7.1**: Help command listing available commands
- **7.2**: Rooms command showing room list with user counts
- **7.3**: Users command showing active users
- **7.4**: Clear command for clearing terminal display
- **7.5**: Error handling for invalid commands

---

## Future Enhancements

Potential improvements to the CommandHandler:

1. **Command Aliases:** Support shortcuts (e.g., `/j` for `/join`)
2. **Command History:** Track and suggest recently used commands
3. **Tab Completion:** Auto-complete room names and commands
4. **Admin Commands:** Add moderation commands for administrators
5. **Custom Commands:** Allow plugins to register custom commands
6. **Command Permissions:** Role-based command access control

---

## Dependencies

The CommandHandler depends on:

- `backend.database.User`: User model for authentication
- `backend.rooms.service.RoomService`: Room management operations
- `backend.websocket.manager.WebSocketManager`: User connection queries

---

## See Also

- [Room Service Documentation](../rooms/README.md)
- [WebSocket Manager Documentation](../websocket/README.md)
- [Main Application Documentation](../../README.md)
- [Command Handler Tests](../tests/test_command_handler.py)
