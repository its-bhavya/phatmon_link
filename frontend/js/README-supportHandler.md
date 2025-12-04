# SupportHandler Component

## Overview

The `SupportHandler` component manages the display of support bot messages and crisis hotline information in the GATEKEEPER BBS terminal interface. It provides empathetic, warm styling for support messages and prominent, urgent styling for crisis resources.

## Requirements

- **12.1**: Support messages are prefixed with `[SUPPORT]` tag
- **12.2**: Support messages use distinct visual styling (warm, empathetic colors)
- **12.3**: Handles support activation messages with greeting
- **12.4**: Displays crisis hotline information prominently

## Features

- **Support Message Display**: Renders support bot messages with `[SUPPORT]` prefix and warm blue styling
- **Crisis Hotline Display**: Renders crisis resources with prominent orange/gold styling and pulsing animation
- **Message Formatting**: Includes timestamps and proper text formatting
- **Integration**: Works seamlessly with existing `ChatDisplay` component

## Usage

### Initialization

```javascript
import { SupportHandler } from './supportHandler.js';
import { ChatDisplay } from './chatDisplay.js';

// Initialize ChatDisplay first
const chatDisplay = new ChatDisplay('chatDisplay');

// Initialize SupportHandler with ChatDisplay instance
const supportHandler = new SupportHandler(chatDisplay);
```

### Handling Support Activation

When a user is connected to the support bot, handle the activation message:

```javascript
supportHandler.handleSupportActivation({
    type: 'support_activation',
    content: 'Hello, I\'m here to listen and support you...',
    room: 'support-user123',
    timestamp: '2024-12-04T10:30:00Z'
});
```

### Handling Support Responses

When the support bot responds to user messages:

```javascript
supportHandler.handleSupportResponse({
    type: 'support_response',
    content: 'I hear you, and your feelings are valid...',
    timestamp: '2024-12-04T10:31:00Z'
});
```

### Handling Crisis Hotlines

When crisis keywords are detected, display hotline information:

```javascript
supportHandler.handleCrisisHotlines({
    type: 'crisis_hotlines',
    content: 'AASRA - 24/7 crisis helpline\nPhone: 91-9820466726\n...',
    timestamp: '2024-12-04T10:32:00Z'
});
```

## Message Types

### Support Activation
- **Type**: `support_activation`
- **Purpose**: Initial greeting when user enters support room
- **Styling**: Warm blue with `[SUPPORT]` prefix
- **Fields**:
  - `content`: Greeting message
  - `room`: Support room name
  - `timestamp`: ISO timestamp (optional)

### Support Response
- **Type**: `support_response`
- **Purpose**: Bot responses during support conversation
- **Styling**: Warm blue with `[SUPPORT]` prefix
- **Fields**:
  - `content`: Bot response message
  - `timestamp`: ISO timestamp (optional)

### Crisis Hotlines
- **Type**: `crisis_hotlines`
- **Purpose**: Display crisis resources and hotline numbers
- **Styling**: Prominent orange/gold with pulsing animation
- **Fields**:
  - `content`: Formatted hotline information
  - `timestamp`: ISO timestamp (optional)

## Styling

### Support Messages
- **Color**: Soft sky blue (`#87ceeb`)
- **Border**: 3px left border in sky blue
- **Background**: Subtle blue tint
- **Prefix**: `[SUPPORT]` with glow effect

### Crisis Messages
- **Color**: Orange (`#ffa500`) and gold (`#ffd700`)
- **Border**: 4px left border in orange
- **Background**: Subtle orange tint
- **Prefix**: `[SUPPORT - CRISIS RESOURCES]` with pulsing glow
- **Animation**: Gentle pulse to draw attention

## API Reference

### Constructor

```javascript
new SupportHandler(chatDisplay, commandBar)
```

**Parameters:**
- `chatDisplay` (ChatDisplay): Required. ChatDisplay instance for rendering messages
- `commandBar` (CommandLineBar): Optional. CommandLineBar instance (reserved for future use)

### Methods

#### `handleSupportActivation(message)`
Handles support room creation and initial greeting.

**Parameters:**
- `message` (Object): Support activation message
  - `content` (string): Greeting message
  - `room` (string): Support room name
  - `timestamp` (string): ISO timestamp (optional)

#### `handleSupportResponse(message)`
Handles support bot responses.

**Parameters:**
- `message` (Object): Support response message
  - `content` (string): Bot response
  - `timestamp` (string): ISO timestamp (optional)

#### `handleCrisisHotlines(message)`
Handles crisis hotline information display.

**Parameters:**
- `message` (Object): Crisis hotlines message
  - `content` (string): Formatted hotline information
  - `timestamp` (string): ISO timestamp (optional)

#### `isInSupportRoom()`
Returns whether user is currently in a support room.

**Returns:** `boolean`

#### `leaveSupportRoom()`
Marks that user has left the support room.

## Testing

A test page is available at `test-supportHandler.html` that demonstrates all message types and styling.

To test:
1. Open `frontend/js/test-supportHandler.html` in a browser
2. Click the test buttons to see different message types
3. Verify styling and formatting

## Integration with Main Application

The SupportHandler is integrated into `main.js`:

```javascript
// Initialize
supportHandler = new SupportHandler(chatDisplay, commandBar);

// Handle WebSocket messages
function handleWebSocketMessage(message) {
    switch (message.type) {
        case 'support_activation':
            handleSupportActivation(message);
            break;
        case 'support_response':
            handleSupportResponse(message);
            break;
        case 'crisis_hotlines':
            handleCrisisHotlines(message);
            break;
        // ... other message types
    }
}
```

## Accessibility

- **Reduced Motion**: Crisis message pulse animation is disabled when user prefers reduced motion
- **Color Contrast**: All text colors meet WCAG AA standards for readability
- **Screen Readers**: Semantic HTML structure with proper text content

## Future Enhancements

- Interactive hotline buttons (click to copy number)
- Support session history
- Customizable styling themes
- Multi-language support for hotline information
