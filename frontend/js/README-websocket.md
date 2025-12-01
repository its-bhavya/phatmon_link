# WebSocket Client

## Overview

The `WebSocketClient` class provides a robust WebSocket connection manager for the Phantom Link BBS frontend. It handles connection management, automatic reconnection with exponential backoff, message sending/receiving, and connection status notifications.

## Features

- **Automatic Reconnection**: Automatically attempts to reconnect on connection loss with exponential backoff
- **JWT Authentication**: Retrieves JWT token from localStorage and includes it in connection
- **Retry Logic**: Retries connection up to 3 times on failure
- **Event Callbacks**: Register callbacks for connection, disconnection, and message events
- **Status Notifications**: Dispatches custom events for UI status updates
- **Connection State Management**: Track connection state and check if connected

## Usage

### Basic Setup

```javascript
// Create WebSocket client instance
const wsClient = new WebSocketClient('ws://localhost:8000/ws');

// Register message handler
wsClient.onMessage((message) => {
    console.log('Received:', message);
    // Handle different message types
    switch (message.type) {
        case 'chat_message':
            displayChatMessage(message);
            break;
        case 'system':
            displaySystemMessage(message);
            break;
        case 'user_list':
            updateUserList(message.users);
            break;
        // ... handle other message types
    }
});

// Register connection handler
wsClient.onConnect(() => {
    console.log('Connected to server');
});

// Register disconnection handler
wsClient.onDisconnect((event) => {
    console.log('Disconnected:', event.code, event.reason);
});

// Connect to server
wsClient.connect();
```

### Sending Messages

```javascript
// Send a chat message
wsClient.send({
    type: 'chat_message',
    content: 'Hello, world!',
    room: 'lobby'
});

// Send a command
wsClient.send({
    type: 'command',
    command: 'rooms'
});

// Join a room
wsClient.send({
    type: 'join_room',
    room: 'techline'
});
```

### Connection Management

```javascript
// Check if connected
if (wsClient.isConnected()) {
    console.log('WebSocket is connected');
}

// Get current state
const state = wsClient.getState();
// Returns: 'connecting', 'open', 'closing', 'closed', or 'disconnected'

// Manually disconnect
wsClient.disconnect();

// Manually reconnect
wsClient.reconnect();
```

### Status Notifications

The WebSocket client dispatches custom events that can be listened to for UI updates:

```javascript
window.addEventListener('ws-status', (event) => {
    const { message, type } = event.detail;
    // type is either 'info' or 'error'
    
    if (type === 'error') {
        showErrorNotification(message);
    } else {
        showInfoNotification(message);
    }
});
```

## Message Types

### Client → Server

**Chat Message:**
```javascript
{
    type: "chat_message",
    content: "Hello world",
    room: "lobby"
}
```

**Command:**
```javascript
{
    type: "command",
    command: "rooms"
}
```

**Join Room:**
```javascript
{
    type: "join_room",
    room: "techline"
}
```

### Server → Client

**Chat Message:**
```javascript
{
    type: "chat_message",
    username: "user123",
    content: "Hello world",
    timestamp: "2025-11-30T12:34:56Z",
    room: "lobby"
}
```

**User List:**
```javascript
{
    type: "user_list",
    users: [
        { username: "user123", room: "lobby" },
        { username: "user456", room: "techline" }
    ]
}
```

**Room List:**
```javascript
{
    type: "room_list",
    rooms: [
        { name: "Lobby", count: 5 },
        { name: "Techline", count: 2 }
    ]
}
```

**System Message:**
```javascript
{
    type: "system",
    content: "Welcome to Phantom Link BBS"
}
```

**Error:**
```javascript
{
    type: "error",
    content: "Invalid command"
}
```

## Reconnection Behavior

The WebSocket client implements automatic reconnection with exponential backoff:

1. **Initial Delay**: 1 second
2. **Exponential Backoff**: Delay doubles with each attempt (1s, 2s, 4s)
3. **Max Delay**: 8 seconds
4. **Max Attempts**: 3 attempts
5. **Failure**: After 3 failed attempts, user is notified to refresh the page

The reconnection only occurs on unexpected disconnections. Manual disconnections via `disconnect()` will not trigger automatic reconnection.

## Authentication

The WebSocket client expects a JWT token to be stored in localStorage under the key `jwt_token`. This token is automatically retrieved and included as a query parameter when connecting:

```javascript
// Token should be set after successful login
localStorage.setItem('jwt_token', 'your-jwt-token-here');

// WebSocket client will automatically use it
wsClient.connect();
```

If no token is found, the connection will fail with an error notification.

## API Reference

### Constructor

```javascript
new WebSocketClient(url)
```

- `url` (string): WebSocket server URL (e.g., 'ws://localhost:8000/ws')

### Methods

#### `connect()`
Establishes WebSocket connection using JWT token from localStorage.

#### `disconnect()`
Manually closes the WebSocket connection. Does not trigger automatic reconnection.

#### `send(message)`
Sends a JSON message through the WebSocket.
- `message` (object): Message object to send
- Returns: `true` if sent successfully, `false` otherwise

#### `onMessage(callback)`
Registers a callback for incoming messages.
- `callback` (function): Function called with message object

#### `onConnect(callback)`
Registers a callback for connection established.
- `callback` (function): Function called when connected

#### `onDisconnect(callback)`
Registers a callback for disconnection.
- `callback` (function): Function called with close event

#### `reconnect()`
Manually triggers reconnection (disconnects then reconnects).

#### `isConnected()`
Returns `true` if WebSocket is currently connected, `false` otherwise.

#### `getState()`
Returns current connection state: 'connecting', 'open', 'closing', 'closed', or 'disconnected'.

## Testing

A test page is available at `test-websocket.html` for manual testing of the WebSocket client functionality. Open it in a browser to:

- Test connection/disconnection
- Send test messages and commands
- View connection logs
- Manage JWT tokens
- Test reconnection behavior

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 5.1**: Messages transmitted via WebSocket connection
- **Requirement 5.5**: Automatic reconnection on interruption with status notifications
- **Requirement 8.2**: Connection failure retry up to 3 times with error messages

## Error Handling

The WebSocket client handles various error scenarios:

- **No Token**: Notifies user to login
- **Connection Failure**: Displays error and attempts retry
- **Send Failure**: Logs error and notifies user
- **Parse Error**: Logs error but maintains connection
- **Max Retries Exceeded**: Notifies user to refresh page
