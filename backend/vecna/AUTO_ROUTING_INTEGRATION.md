# Auto-Routing Integration

## Overview

The auto-routing functionality has been integrated into the main message handling flow in `backend/main.py`. This feature automatically analyzes user messages and routes them to the most appropriate room using Gemini AI.

## How It Works

### 1. Initialization (Startup)

When the application starts, the Gemini service is initialized in the `lifespan` function:

```python
# Initialize Gemini service for auto-routing (if enabled)
if config.VECNA_ENABLED and config.GEMINI_API_KEY:
    try:
        app.state.gemini_service = GeminiService(
            api_key=config.GEMINI_API_KEY,
            model=config.GEMINI_MODEL,
            temperature=config.GEMINI_TEMPERATURE,
            max_tokens=config.GEMINI_MAX_TOKENS
        )
        print("Gemini service initialized for auto-routing")
    except GeminiServiceError as e:
        print(f"Warning: Gemini service initialization failed: {e}")
        app.state.gemini_service = None
else:
    app.state.gemini_service = None
```

### 2. Message Processing Flow

When a user sends a chat message, the following happens:

1. **Rate Limiting Check**: Message is checked against rate limits
2. **Auto-Routing Analysis**: If Gemini service is available, the message is analyzed:
   - Checks if message fits current room
   - If not, suggests a better room
   - Moves user if confidence threshold is met (default: 0.7)
3. **Notification**: User receives a system message explaining the move
4. **Room Updates**: All clients receive updated room lists
5. **Message Broadcast**: Original message is sent to the (potentially new) room

### 3. Auto-Routing Logic

The auto-routing uses the `on_message_hook` function from `backend/vecna/auto_router.py`:

```python
notification = await on_message_hook(
    user=user,
    message=content,
    current_room=current_room,
    room_service=app.state.room_service,
    gemini_service=app.state.gemini_service
)
```

This function:
- Analyzes message relevance to current room
- Suggests alternative rooms if needed
- Moves user automatically if confidence is high enough
- Returns a notification message for the user

### 4. Room Transition Handling

If the user is moved to a new room:

1. User receives notification about the move
2. WebSocket manager updates user's room
3. Room service moves user from old room to new room
4. User receives room entry message with description
5. Other users in new room are notified of entry
6. All clients receive updated room list with counts

## Configuration

### Environment Variables

```bash
# Enable/disable auto-routing
VECNA_ENABLED=true

# Gemini API configuration
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.5
GEMINI_MAX_TOKENS=500
```

### Confidence Threshold

The default confidence threshold for auto-routing is **0.7** (70%). This means:
- Messages with 70%+ confidence of being off-topic will trigger a room move
- Lower threshold = more aggressive routing (more moves)
- Higher threshold = more conservative routing (fewer moves)

To adjust the threshold, modify the `confidence_threshold` parameter in `auto_router.py`:

```python
result = await auto_route_user(
    user, message, current_room,
    room_service, gemini_service,
    confidence_threshold=0.75  # More conservative
)
```

## Example Scenarios

### Scenario 1: Technical Question in Lobby

**User in Lobby**: "How do I fix this Python import error?"

**Auto-Router Analysis**:
- Message doesn't fit Lobby (general chat)
- Best room: Techline (tech discussions)
- Confidence: 0.92

**Action**:
- User automatically moved to Techline
- Notification: "[SYSOP] Your message seems to be about technical programming question. Moving you to Techline."

### Scenario 2: General Chat in Techline

**User in Techline**: "What's everyone doing this weekend?"

**Auto-Router Analysis**:
- Message doesn't fit Techline (tech discussions)
- Best room: Lobby (general chat)
- Confidence: 0.85

**Action**:
- User automatically moved to Lobby
- Notification: "[SYSOP] Your message seems to be about general conversation. Moving you to Lobby."

### Scenario 3: Message Fits Current Room

**User in Techline**: "What's your favorite programming language?"

**Auto-Router Analysis**:
- Message fits Techline (tech discussions)
- Confidence: 0.95

**Action**:
- No routing needed
- User stays in Techline
- Message sent normally

## Error Handling

The integration includes robust error handling:

1. **Gemini Service Unavailable**: If the service fails to initialize, auto-routing is disabled but the app continues to work normally
2. **API Errors**: If the Gemini API fails during routing, the error is logged and the message is sent to the current room without routing
3. **Fallback Behavior**: All routing errors fall back to normal message flow

## Testing

To test the auto-routing integration:

1. **Start the server** with a valid Gemini API key:
   ```bash
   python start_server.py
   ```

2. **Connect as a user** and send messages in different rooms

3. **Try off-topic messages**:
   - In Lobby: "How do I debug this code?"
   - In Techline: "Anyone want to play games?"
   - In Arcade Hall: "I need help with Python"

4. **Observe auto-routing** behavior and notifications

## Monitoring

Auto-routing activity is logged to the console:

```
Auto-routing error: <error message>  # If routing fails
```

To enable more detailed logging, set the log level in your application:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('backend.vecna')
```

## Disabling Auto-Routing

To disable auto-routing without removing the code:

1. Set `VECNA_ENABLED=false` in `.env`
2. Or remove/comment out `GEMINI_API_KEY` in `.env`

The application will continue to work normally without auto-routing.

## Future Enhancements

Potential improvements to the auto-routing system:

1. **User Preferences**: Allow users to opt-out of auto-routing
2. **Room Creation**: Automatically create new rooms for emerging topics
3. **Learning**: Track routing accuracy and adjust thresholds
4. **Batch Analysis**: Analyze multiple messages to detect conversation topics
5. **Custom Rules**: Allow admins to define routing rules per room
