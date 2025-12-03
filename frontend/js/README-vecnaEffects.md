# VecnaEffects Component

## Overview

The `VecnaEffects` class manages visual effects during Vecna activation in the GATEKEEPER BBS terminal interface. It provides methods for applying text corruption effects and Psychic Grip visual effects including screen flicker, inverted colors, scanline ripples, and ASCII static storms.

## Requirements

This component implements the following requirements:
- **5.1**: Text corruption effects for emotional triggers
- **5.2**: Screen flicker effects during Psychic Grip
- **5.3**: Inverted color effects during Psychic Grip
- **5.4**: Scanline ripple effects during Psychic Grip
- **5.5**: ASCII static storm overlay effects
- **5.6**: Cleanup and restoration of normal visual rendering

## Usage

### Initialization

```javascript
import { VecnaEffects } from './vecnaEffects.js';

const chatDisplay = document.getElementById('chatDisplay');
const vecnaEffects = new VecnaEffects(chatDisplay);
```

### Apply Text Corruption

Display a corrupted message with glitch effects:

```javascript
const corruptedMessage = vecnaEffects.applyTextCorruption('wHy c@n\'t u fig. tH1s out, humaN?');
chatDisplay.appendChild(corruptedMessage);
```

### Start Psychic Grip Effects

Activate visual effects for a specified duration:

```javascript
// All effects (default)
vecnaEffects.startPsychicGrip(7, ['flicker', 'inverted', 'scanlines', 'static']);

// Specific effects only
vecnaEffects.startPsychicGrip(5, ['flicker', 'scanlines']);
```

### End Psychic Grip Effects

Manually end all visual effects:

```javascript
vecnaEffects.endPsychicGrip();
```

Note: Effects automatically end after the specified duration.

## API Reference

### Constructor

**`new VecnaEffects(chatDisplay)`**

Creates a new VecnaEffects instance.

- **Parameters:**
  - `chatDisplay` (HTMLElement): The chat display container element

### Methods

#### `applyTextCorruption(message)`

Applies text corruption styling to a message.

- **Parameters:**
  - `message` (string): The corrupted message text
- **Returns:** HTMLElement with corruption styling
- **Requirement:** 5.1

#### `startPsychicGrip(duration, effects)`

Starts Psychic Grip visual effects.

- **Parameters:**
  - `duration` (number): Duration in seconds
  - `effects` (Array<string>): Array of effect names (default: `['flicker', 'inverted', 'scanlines', 'static']`)
- **Requirements:** 5.2, 5.3, 5.4, 5.5

#### `endPsychicGrip()`

Ends all Psychic Grip effects and restores normal display.

- **Requirement:** 5.6

#### `isEffectsActive()`

Checks if Vecna effects are currently active.

- **Returns:** boolean

### Individual Effect Methods

These methods are called internally by `startPsychicGrip()`:

- `applyScreenFlicker()` - Screen flicker animation (Requirement 5.2)
- `applyInvertedColors()` - Color inversion effect (Requirement 5.3)
- `applyScanlineRipple()` - Scanline ripple animation (Requirement 5.4)
- `showStaticStorm()` - ASCII static overlay (Requirement 5.5)

And their corresponding removal methods:
- `removeScreenFlicker()`
- `removeInvertedColors()`
- `removeScanlineRipple()`
- `hideStaticStorm()`

## CSS Classes

The component uses the following CSS classes defined in `terminal.css`:

- `.vecna-corrupted` - Corrupted text styling with glitch animation
- `.vecna-psychic-grip` - Screen flicker effect
- `.vecna-inverted` - Color inversion effect
- `.vecna-scanlines` - Scanline ripple overlay
- `.vecna-static` - ASCII static storm overlay
- `.vecna-effects-container` - Container for overlay effects

## Visual Effects

### Text Corruption (Requirement 5.1)
- Red glow with enhanced intensity
- Glitch animation with position shifts
- Bold text with increased letter spacing

### Screen Flicker (Requirement 5.2)
- Rapid opacity changes
- Random brightness variations
- 100ms update interval

### Inverted Colors (Requirement 5.3)
- Full color inversion with hue rotation
- Smooth transition effect

### Scanline Ripple (Requirement 5.4)
- Animated horizontal scanlines
- Red-tinted overlay
- Continuous vertical movement

### ASCII Static Storm (Requirement 5.5)
- Random ASCII characters (█▓▒░▄▀■□▪▫)
- 50ms update interval for animation
- Semi-transparent red overlay

## Testing

A test page is available at `frontend/js/test-vecnaEffects.html` to verify all effects work correctly.

Open the test page in a browser and use the control buttons to test:
- Text corruption display
- Full Psychic Grip with all effects
- Individual effects (flicker, inverted, scanlines, static)
- Manual effect termination

## Accessibility

The component respects the `prefers-reduced-motion` media query:
- All animations are disabled when reduced motion is preferred
- Effects still apply but without animation
- Ensures accessibility for users with motion sensitivity

## Integration

This component is designed to be used with:
- `VecnaHandler` - Handles Vecna message types and coordinates effects
- `ChatDisplay` - Displays messages with corruption effects
- `CommandBar` - Can be disabled during Psychic Grip

See task 14 for VecnaHandler implementation.
