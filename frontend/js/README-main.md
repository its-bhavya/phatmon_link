# Main Application Logic

This module integrates all frontend components and manages the application lifecycle.

## Components Integrated

- **WebSocketClient**: Manages real-time communication with the backend
- **CommandLineBar**: Handles user input and command history
- **ChatDisplay**: Renders messages with timestamps and formatting

## Features

### Message Handling
- Routes incoming WebSocket messages to appropriate handlers
- Displays chat messages with username and timestamp
- Shows system messages and errors with distinct styling
- Updates active user list when users join/leave

### Command Processing
- `/help` - Shows available commands
- `/rooms` - Lists all rooms with user counts
- `/users` - Shows active users and their rooms
- `/clear` - Clears the terminal display
- `/join <room>` - Switches to a different room
- `/disconnect` - Manually disconnects from server
- `/reconnect` - Manually reconnects to server

### Connection Management
- Automatic authentication using JWT token from localStorage
- Redirects to auth page if no token found
- Handles connection/disconnection events
- Displays connection status messages

## Requirements Satisfied

- **5.1**: Real-time message transmission via WebSocket
- **5.2**: Message broadcasting to room members
- **5.3**: Message display with username and timestamp
- **6.3**: Active user list updates
- **6.4**: User list shows username and room
- **7.1**: Help command handling
- **7.2**: Rooms command with user counts
- **7.3**: Users command with active list
- **7.5**: Invalid command error handling
- **9.3**: Message routing and processing

## Usage

The application initializes automatically when the DOM is ready:

```javascript
// Initialization happens automatically
// No manual setup required

// Optional: Access exported functions
import { logout } from './main.js';
logout(); // Disconnect and return to auth page
```

## Message Flow

1. User types in command bar
2. CommandLineBar distinguishes between messages and commands
3. Main.js sends appropriate WebSocket message
4. Backend processes and responds
5. Main.js routes response to appropriate handler
6. ChatDisplay renders the result

## Error Handling

- Connection errors: Displays error message and attempts reconnection
- Invalid commands: Shows error message from server
- Authentication errors: Redirects to login page
- Room not found: Shows error without changing current room
