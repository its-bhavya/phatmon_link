# CommandLineBar Component

## Overview
The CommandLineBar component handles user input for the Phantom Link BBS terminal interface. It provides command history navigation, distinguishes between commands and messages, and manages input submission.

## Usage

```javascript
import { CommandLineBar } from './commandBar.js';

// Initialize with callbacks
const commandBar = new CommandLineBar(
    // Callback for regular messages
    (message) => {
        console.log('Message:', message);
        // Send message to server
    },
    // Callback for commands (starting with /)
    (command, args, fullInput) => {
        console.log('Command:', command);
        console.log('Arguments:', args);
        console.log('Full input:', fullInput);
        // Handle command
    }
);
```

## Features

### Input Handling
- Automatically focuses the input field on initialization
- Maintains focus to ensure seamless typing experience
- Clears input after submission (Requirement 5.4)

### Command vs Message Detection
- Messages: Any input that doesn't start with `/`
- Commands: Input starting with `/` (e.g., `/help`, `/rooms`, `/users`)
- Commands are parsed into command name and arguments

### Command History
- Press **Up Arrow** to navigate to previous commands/messages
- Press **Down Arrow** to navigate to next commands/messages
- History is preserved across the session
- Duplicate consecutive entries are not added

### Keyboard Shortcuts
- **Enter**: Submit current input
- **Up Arrow**: Previous history item
- **Down Arrow**: Next history item

## API

### Constructor
```javascript
new CommandLineBar(onSubmit, onCommand)
```
- `onSubmit(message)`: Called when a regular message is submitted
- `onCommand(command, args, fullInput)`: Called when a command is submitted

### Methods

#### `clearInput()`
Clears the input field and resets history navigation.

#### `addToHistory(text)`
Adds text to the command history.

#### `getHistory()`
Returns an array of all history items.

#### `focus()`
Focuses the input element.

#### `setValue(value)`
Sets the input value programmatically.

#### `getValue()`
Gets the current input value.

#### `disable()`
Disables the input field.

#### `enable()`
Enables the input field and focuses it.

## Requirements Satisfied

- **3.3**: Display command line bar for user input
- **3.4**: Echo characters with terminal styling
- **5.4**: Clear command line bar after submission
- **7.1-7.5**: Handle commands for navigation and control

## HTML Requirements

The component expects an input element with id `commandInput`:

```html
<input 
    type="text" 
    class="command-input" 
    id="commandInput" 
    placeholder="Type a message or /help for commands"
    autocomplete="off"
    spellcheck="false"
/>
```

## Testing

A test file is available at `frontend/js/test-commandBar.html` for manual testing of the component functionality.
