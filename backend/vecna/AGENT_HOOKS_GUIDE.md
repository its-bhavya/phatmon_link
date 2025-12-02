# Agent Hooks Guide: Automatic Room Routing

This guide explains how to use the automatic room routing feature with Kiro agent hooks.

## Overview

The automatic room routing system uses Gemini AI to:
1. **Analyze message relevance**: Determine if a message fits the current room
2. **Suggest better rooms**: Find the most appropriate room for off-topic messages
3. **Auto-route users**: Automatically move users to better rooms
4. **Create new rooms**: Detect when a new room is needed based on conversation patterns

## Quick Start

### 1. Setup

First, ensure your `.env` file has the Gemini API key:

```bash
GEMINI_API_KEY=your_api_key_here
VECNA_ENABLED=true
```

### 2. Create Agent Hook for Message Routing

**Hook Name**: Auto-Route on Message Send

**Trigger**: When a message is sent

**Action**: Python script

```python
from backend.vecna.auto_router import on_message_hook
from backend.vecna.gemini_service import GeminiService
from backend.rooms.service import RoomService
from backend.config import get_config

# Initialize services
config = get_config()
gemini_service = GeminiService(
    api_key=config.GEMINI_API_KEY,
    model=config.GEMINI_MODEL,
    temperature=config.GEMINI_TEMPERATURE,
    max_tokens=config.GEMINI_MAX_TOKENS
)

# Get room service (from your app context)
room_service = app.state.room_service

# Run auto-routing
notification = await on_message_hook(
    user=current_user,
    message=message_text,
    current_room=current_room_name,
    room_service=room_service,
    gemini_service=gemini_service
)

# Send notification if user was moved
if notification:
    await websocket.send_json({
        "type": "system",
        "content": notification
    })
```

### 3. Create Agent Hook for Room Creation

**Hook Name**: Check for New Room Creation

**Trigger**: Every 10 messages (or on a timer)

**Action**: Python script

```python
from backend.vecna.auto_router import periodic_room_check_hook
from backend.vecna.gemini_service import GeminiService
from backend.rooms.service import RoomService
from backend.config import get_config

# Initialize services
config = get_config()
gemini_service = GeminiService(api_key=config.GEMINI_API_KEY)
room_service = app.state.room_service

# Get recent messages (last 20)
recent_messages = [
    {
        "user": msg.username,
        "message": msg.content,
        "room": msg.room_name
    }
    for msg in get_recent_messages(limit=20)
]

# Check if new room should be created
notification = await periodic_room_check_hook(
    recent_messages=recent_messages,
    room_service=room_service,
    gemini_service=gemini_service
)

# Broadcast notification if room was created
if notification:
    await broadcast_to_all_users({
        "type": "system",
        "content": notification
    })
```

## Advanced Usage

### Custom Confidence Thresholds

You can adjust how aggressive the auto-routing is:

```python
from backend.vecna.auto_router import auto_route_user

# More aggressive (moves users more often)
result = await auto_route_user(
    user, message, current_room,
    room_service, gemini_service,
    confidence_threshold=0.6  # Lower = more aggressive
)

# More conservative (only moves when very confident)
result = await auto_route_user(
    user, message, current_room,
    room_service, gemini_service,
    confidence_threshold=0.85  # Higher = more conservative
)
```

### Custom Room Creation Threshold

Control how many messages are needed before creating a new room:

```python
from backend.vecna.auto_router import check_and_create_room

# Require more messages (less aggressive)
result = await check_and_create_room(
    recent_messages,
    room_service,
    gemini_service,
    message_threshold=10,  # Need 10 messages about same topic
    confidence_threshold=0.8
)

# Require fewer messages (more aggressive)
result = await check_and_create_room(
    recent_messages,
    room_service,
    gemini_service,
    message_threshold=3,  # Only need 3 messages
    confidence_threshold=0.7
)
```

### Manual Control

If you want more control over the routing decision:

```python
from backend.vecna.auto_router import auto_route_user

result = await auto_route_user(
    user, message, current_room,
    room_service, gemini_service
)

# Check result before taking action
if result['moved']:
    print(f"User moved from {result['from_room']} to {result['to_room']}")
    print(f"Reason: {result['reason']}")
    print(f"Confidence: {result['confidence']:.2f}")
    
    # Send custom notification
    await send_notification(user, result['notification'])
else:
    print(f"User stayed in {result['from_room']}")
    print(f"Reason: {result['reason']}")
```

## Configuration

### Environment Variables

```bash
# Gemini AI Configuration
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_TEMPERATURE=0.9
GEMINI_MAX_TOKENS=500

# Vecna Configuration (must be enabled)
VECNA_ENABLED=true
```

### Recommended Settings

For **production** (conservative):
- `confidence_threshold`: 0.75-0.85
- `message_threshold`: 7-10
- Auto-routing: Enabled with user notification

For **development** (aggressive):
- `confidence_threshold`: 0.6-0.7
- `message_threshold`: 3-5
- Auto-routing: Enabled with verbose logging

## Examples

### Example 1: User Asks Technical Question in Lobby

```
User in Lobby: "How do I fix this Python import error?"

Auto-Router Analysis:
- Message doesn't fit Lobby (general chat)
- Best room: Techline (tech discussions)
- Confidence: 0.92

Action:
- User automatically moved to Techline
- Notification: "[SYSOP] Your message seems to be about technical programming question. Moving you to Techline."
```

### Example 2: Multiple Users Discuss React

```
Recent Messages in Lobby:
- Alice: "Anyone know about React hooks?"
- Bob: "Yeah, useEffect is confusing"
- Charlie: "I'm struggling with useState"
- Dave: "React context is hard to understand"
- Eve: "Need help with React Router"

Auto-Router Analysis:
- 5 users discussing React-specific topics
- No existing "React Development" room
- Confidence: 0.88

Action:
- New room "React Development" created
- Notification: "[SYSOP] New room 'React Development' created based on recent discussions. Type /join React Development to participate!"
```

### Example 3: User Message Fits Current Room

```
User in Techline: "What's your favorite programming language?"

Auto-Router Analysis:
- Message fits Techline (tech discussions)
- Confidence: 0.95

Action:
- No routing needed
- User stays in Techline
```

## Troubleshooting

### Issue: Users being moved too often

**Solution**: Increase `confidence_threshold` to 0.8 or higher

```python
result = await auto_route_user(
    user, message, current_room,
    room_service, gemini_service,
    confidence_threshold=0.85  # More conservative
)
```

### Issue: New rooms created too frequently

**Solution**: Increase `message_threshold` and `confidence_threshold`

```python
result = await check_and_create_room(
    recent_messages,
    room_service,
    gemini_service,
    message_threshold=10,  # Need more messages
    confidence_threshold=0.85  # Higher confidence required
)
```

### Issue: Gemini API errors

**Solution**: The system has built-in fallbacks. Check logs for errors:

```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('backend.vecna')
```

### Issue: Users not being notified

**Solution**: Ensure you're sending the notification:

```python
notification = await on_message_hook(...)
if notification:
    # Make sure this is actually sending to the user
    await send_to_user(notification)
```

## Best Practices

1. **Start Conservative**: Begin with high confidence thresholds (0.8+) and adjust based on user feedback

2. **Monitor Performance**: Log routing decisions to understand patterns:
   ```python
   logger.info(f"Routing decision: {result}")
   ```

3. **User Feedback**: Allow users to opt-out or provide feedback on routing decisions

4. **Rate Limiting**: Don't check for new rooms on every message - use a counter or timer

5. **Room Descriptions**: Ensure room descriptions are clear and descriptive for better AI analysis

6. **Testing**: Test with various message types before deploying to production

## Integration with Existing Code

To integrate with your existing WebSocket message handler:

```python
# In your WebSocket message handler
async def handle_message(websocket, message_data):
    user = get_current_user(websocket)
    current_room = get_user_room(user)
    message_text = message_data['content']
    
    # Auto-route before processing message
    notification = await on_message_hook(
        user, message_text, current_room,
        room_service, gemini_service
    )
    
    if notification:
        await websocket.send_json({
            "type": "system",
            "content": notification
        })
    
    # Continue with normal message processing
    await process_message(user, message_text)
```

## API Reference

See the docstrings in `backend/vecna/auto_router.py` for detailed API documentation.

Key functions:
- `auto_route_user()`: Main routing function
- `check_and_create_room()`: Room creation checker
- `on_message_hook()`: Simple wrapper for message hooks
- `periodic_room_check_hook()`: Simple wrapper for periodic checks
