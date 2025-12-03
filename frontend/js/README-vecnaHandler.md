# VecnaHandler Component

## Overview

The VecnaHandler component manages Vecna-specific message types and state during adversarial AI interactions. It coordinates between the chat display, command bar, and visual effects to create immersive Vecna experiences.

## Requirements

- **3.3**: Display corrupted hostile responses during emotional triggers
- **4.2**: Disable input during Psychic Grip
- **4.5**: Handle Psychic Grip release and cleanup
- **9.1**: Prefix all Vecna messages with [VECNA] tag
- **9.3**: Apply distinct CSS styling to Vecna messages
- **9.4**: Render Psychic Grip messages with character-by-character animation

## Dependencies

- `ChatDisplay`: For displaying messages
- `CommandLineBar`: For disabling/enabling input
- `VecnaEffects`: For applying visual effects

## Usage

```javascript
import { ChatDisplay } from './chatDisplay.js';
import { CommandLineBar } from './commandBar.js';
import { VecnaEffects } from './vecnaEffects.js';
import { VecnaHandler } from './vecnaHandler.js';

// Initialize dependencies
const chatDisplay = new ChatDisplay('chatDisplay');
const commandBar = new CommandLineBar(onSubmit, onCommand);
const vecnaEffects = new VecnaEffects(document.getElementById('chatDisplay'));

// Create VecnaHandler
const vecnaHandler = new VecnaHandler(chatDisplay, commandBar, vecnaEffects);

// Handle Vecna messages from WebSocket
function handleWebSocketMessage(message) {
    switch (message.type) {
        case 'vecna_emotional':
            vecnaHandler.handleEmotionalTrigger(message);
            break;
            
        case 'vecna_psychic_grip':
            vecnaHandler.handlePsychicGrip(message);
            break;
            
        case 'vecna_release':
            vecnaHandler.handleGripRelease();
            break;
    }
}
```

## API Reference

### Constructor

```javascript
new VecnaHandler(chatDisplay, commandBar, vecnaEffects)
```

Creates a new VecnaHandler instance.

**Parameters:**
- `chatDisplay` (ChatDisplay): Chat display instance
- `commandBar` (CommandLineBar): Command bar instance
- `vecnaEffects` (VecnaEffects): Vecna effects instance

### Methods

#### handleEmotionalTrigger(message)

Handles Vecna emotional trigger messages by displaying corrupted text with special styling.

**Parameters:**
- `message` (Object): Vecna emotional trigger message
  - `content` (string): Corrupted message content
  - `corruption_level` (number, optional): Corruption level applied

**Example:**
```javascript
vecnaHandler.handleEmotionalTrigger({
    content: 'wHy c@n\'t u f1gur3 tH1s out, hum@N?',
    corruption_level: 0.3
});
```

#### handlePsychicGrip(message)

Handles Psychic Grip activation by freezing input, starting visual effects, and displaying narrative with animation.

**Parameters:**
- `message` (Object): Psychic Grip message
  - `content` (string): Narrative content
  - `duration` (number): Freeze duration in seconds (default: 7)
  - `effects` (Array<string>, optional): Visual effects to apply

**Example:**
```javascript
vecnaHandler.handlePsychicGrip({
    content: 'I see you return to the Archives... again and again...',
    duration: 7,
    effects: ['flicker', 'inverted', 'scanlines', 'static']
});
```

#### handleGripRelease()

Handles Psychic Grip release by ending visual effects, re-enabling input, and showing system message.

**Example:**
```javascript
vecnaHandler.handleGripRelease();
```

#### displayVecnaMessage(content, isGrip)

Displays a Vecna message with special styling and optional character-by-character animation.

**Parameters:**
- `content` (string): Message content
- `isGrip` (boolean): Whether this is a Psychic Grip message (enables animation)

**Example:**
```javascript
vecnaHandler.displayVecnaMessage('[VECNA] Your patterns are predictable...', true);
```

#### isGripCurrentlyActive()

Checks if Psychic Grip is currently active.

**Returns:** `boolean`

**Example:**
```javascript
if (vecnaHandler.isGripCurrentlyActive()) {
    console.log('Psychic Grip is active');
}
```

#### forceRelease()

Forces Psychic Grip release (for emergency cleanup).

**Example:**
```javascript
vecnaHandler.forceRelease();
```

## Message Format

### Emotional Trigger Message

```javascript
{
    type: 'vecna_emotional',
    content: 'wHy c@n\'t u fig. tH1s out, humaN?',
    corruption_level: 0.3,
    timestamp: '2025-12-01T12:00:00Z'
}
```

### Psychic Grip Message

```javascript
{
    type: 'vecna_psychic_grip',
    content: 'I see you return to the Archives... again and again...',
    duration: 7,
    effects: ['flicker', 'inverted', 'scanlines', 'static'],
    timestamp: '2025-12-01T12:00:00Z'
}
```

### Grip Release Message

```javascript
{
    type: 'vecna_release',
    content: '[SYSTEM] Control returned to SysOp. Continue your session.',
    timestamp: '2025-12-01T12:00:07Z'
}
```

## State Management

The VecnaHandler maintains the following internal state:

- `isGripActive` (boolean): Whether Psychic Grip is currently active
- `gripReleaseTimer` (number): Timer ID for scheduled grip release

## Visual Effects

The VecnaHandler coordinates with VecnaEffects to apply:

- **Text Corruption**: Red glow with glitch animation
- **Screen Flicker**: Rapid opacity changes
- **Inverted Colors**: Color inversion filter
- **Scanline Ripple**: Animated scanline overlay
- **ASCII Static Storm**: Random ASCII character overlay

## CSS Classes

The following CSS classes are applied by VecnaHandler:

- `.vecna-message`: Base styling for Vecna messages
- `.vecna-text`: Styling for Vecna text content
- `.vecna-corrupted`: Applied by VecnaEffects for corrupted text

## Testing

A test page is available at `frontend/js/test-vecnaHandler.html` for manual testing of all VecnaHandler functionality.

## Integration Notes

- VecnaHandler should be initialized after ChatDisplay, CommandLineBar, and VecnaEffects
- WebSocket message routing should call appropriate VecnaHandler methods based on message type
- Input is automatically disabled during Psychic Grip and re-enabled on release
- Visual effects are automatically cleaned up after Psychic Grip duration expires
- All Vecna messages are automatically prefixed with [VECNA] if not already present

## Error Handling

- If Psychic Grip is already active, subsequent calls to `handlePsychicGrip()` are ignored
- If grip release is called when no grip is active, the call is safely ignored
- Timers are properly cleaned up to prevent memory leaks
- Force release can be used for emergency cleanup if needed
