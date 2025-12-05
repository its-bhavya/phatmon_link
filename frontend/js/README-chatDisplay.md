# ChatDisplay Component

## Overview

The `ChatDisplay` component handles displaying chat messages with timestamps, usernames, and proper formatting in the Obsidian BBS terminal interface. It provides auto-scrolling, message formatting, and support for different message types (chat, system, error).

## Requirements Addressed

- **5.3**: Display messages with sender username, timestamp, and message content
- **7.4**: Clear terminal display with /clear command
- **9.2**: Format messages clearly with timestamps and sender information
- **9.4**: Maintain readability and proper formatting
- **9.5**: Reflect updates immediately in the terminal display

## Usage

### Basic Initialization

```javascript
import { ChatDisplay } from './chatDisplay.js';

// Initialize with default container ID 'chatDisplay'
const chatDisplay = new ChatDisplay();

// Or specify a custom container ID
const chatDisplay = new ChatDisplay('myCustomContainer');
```

### Adding Messages

#### Chat Message
```javascript
chatDisplay.addMessage({
    type: 'chat_message',
    username: 'Alice',
    content: 'Hello everyone!',
    timestamp: '2025-12-01T12:34:56Z'  // Optional, uses current time if not provided
});
```

Output: `[12:34:56] <Alice> Hello everyone!`

#### System Message
```javascript
chatDisplay.addMessage({
    type: 'system',
    content: 'Welcome to Obsidian BBS',
    timestamp: '2025-12-01T12:34:56Z'
});
```

Output: `[12:34:56] * SYSTEM: Welcome to Obsidian BBS` (in yellow)

#### Error Message
```javascript
chatDisplay.addMessage({
    type: 'error',
    content: 'Invalid command',
    timestamp: '2025-12-01T12:34:56Z'
});
```

Output: `[12:34:56] * ERROR: Invalid command` (in red)

### Adding Multiple Messages

```javascript
const messages = [
    { type: 'chat_message', username: 'Alice', content: 'Hi!' },
    { type: 'chat_message', username: 'Bob', content: 'Hello!' },
    { type: 'system', content: 'Charlie joined the room' }
];

chatDisplay.addMessages(messages);
```

### Clearing the Display

```javascript
// Clear all messages (for /clear command)
chatDisplay.clear();
```

### Auto-Scroll Control

```javascript
// Check if auto-scroll is enabled
if (chatDisplay.isAutoScrollEnabled()) {
    console.log('Auto-scroll is on');
}

// Disable auto-scroll
chatDisplay.disableAutoScroll();

// Enable auto-scroll
chatDisplay.enableAutoScroll();

// Manually scroll to bottom
chatDisplay.scrollToBottom();
```

### Getting Message Count

```javascript
const count = chatDisplay.getMessageCount();
console.log(`Total messages: ${count}`);
```

## Message Format

### Timestamp Format
All timestamps are formatted as `[HH:MM:SS]` in 24-hour format with zero-padding.

Examples:
- `[09:05:03]` - 9:05:03 AM
- `[14:30:45]` - 2:30:45 PM
- `[00:00:00]` - Midnight

### Chat Message Format
```
[HH:MM:SS] <username> message content
```

### System Message Format
```
[HH:MM:SS] * SYSTEM: message content
```

### Error Message Format
```
[HH:MM:SS] * ERROR: message content
```

## Features

### Auto-Scroll
- Automatically scrolls to the latest message when new messages arrive
- Detects when user manually scrolls up and disables auto-scroll
- Re-enables auto-scroll when user scrolls back to the bottom
- Can be manually controlled via `enableAutoScroll()` and `disableAutoScroll()`

### Security
- All message content is HTML-escaped to prevent XSS attacks
- Usernames are also escaped for security

### Styling
The component uses CSS classes for styling:
- `.message` - Base message class
- `.message.system` - System messages (yellow)
- `.message.error` - Error messages (red)
- `.timestamp` - Timestamp styling (dark green)
- `.username` - Username styling (bright green, bold)

## HTML Structure

The component expects a container element in the HTML:

```html
<div class="chat-display" id="chatDisplay">
    <!-- Messages will be dynamically added here -->
</div>
```

## Testing

A test page is available at `test-chatDisplay.html` that demonstrates all features:
- Adding different message types
- Multiple messages
- Clearing the display
- Auto-scroll toggling
- Message count tracking

To test, open `test-chatDisplay.html` in a browser.

## API Reference

### Constructor

#### `new ChatDisplay(containerId)`
- **Parameters:**
  - `containerId` (string, optional): ID of the container element. Default: `'chatDisplay'`
- **Throws:** Error if container element is not found

### Methods

#### `addMessage(message)`
Add a single message to the display.
- **Parameters:**
  - `message` (Object): Message object
    - `type` (string): Message type ('chat_message', 'system', 'error')
    - `content` (string): Message content
    - `username` (string, optional): Username for chat messages
    - `timestamp` (string, optional): ISO timestamp (uses current time if not provided)

#### `addMessages(messages)`
Add multiple messages at once.
- **Parameters:**
  - `messages` (Array<Object>): Array of message objects

#### `clear()`
Clear all messages from the display.

#### `scrollToBottom()`
Manually scroll to the bottom of the chat display.

#### `enableAutoScroll()`
Enable automatic scrolling to new messages.

#### `disableAutoScroll()`
Disable automatic scrolling.

#### `isAutoScrollEnabled()`
Check if auto-scroll is currently enabled.
- **Returns:** boolean

#### `getMessageCount()`
Get the number of messages currently displayed.
- **Returns:** number

## Integration Example

```javascript
import { ChatDisplay } from './chatDisplay.js';
import { CommandLineBar } from './commandBar.js';

// Initialize components
const chatDisplay = new ChatDisplay();
const commandBar = new CommandLineBar(
    // Handle regular messages
    (message) => {
        chatDisplay.addMessage({
            type: 'chat_message',
            username: 'You',
            content: message
        });
    },
    // Handle commands
    (command, args) => {
        if (command === 'clear') {
            chatDisplay.clear();
        } else {
            chatDisplay.addMessage({
                type: 'system',
                content: `Executing command: /${command}`
            });
        }
    }
);

// Add welcome message
chatDisplay.addMessage({
    type: 'system',
    content: 'Welcome to Obsidian BBS'
});
```

## Browser Compatibility

The component uses modern JavaScript features:
- ES6 modules
- Template literals
- Arrow functions
- Const/let declarations

Supported browsers:
- Chrome/Edge 61+
- Firefox 60+
- Safari 11+
- Opera 48+
