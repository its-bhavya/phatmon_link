# Automatic Room Routing with Gemini AI

## Overview

The automatic room routing system uses Google's Gemini AI to intelligently route users to appropriate chat rooms based on their message content. This creates a more organized and topic-focused chat experience.

## Features

### 1. Message Relevance Analysis
Analyzes whether a user's message fits the current room's topic.

**Example**: User asks "How do I fix this Python bug?" in the Lobby → System detects this is a technical question that doesn't fit general chat.

### 2. Smart Room Suggestions
Suggests the best room for a message from all available rooms.

**Example**: Technical question → Suggests "Techline" room for tech discussions.

### 3. Automatic User Routing
Automatically moves users to more appropriate rooms when confidence is high.

**Example**: User is moved from Lobby to Techline with notification: "[SYSOP] Your message seems to be about technical programming question. Moving you to Techline."

### 4. Dynamic Room Creation
Detects when multiple users are discussing a topic that needs its own room.

**Example**: 5+ users discussing React in Lobby → System creates "React Development" room and notifies users.

## Quick Start

### 1. Configuration

Add to your `.env` file:

```bash
GEMINI_API_KEY=your_api_key_here
VECNA_ENABLED=true
GEMINI_MODEL=gemini-2.0-flash-exp
GEMINI_TEMPERATURE=0.9
GEMINI_MAX_TOKENS=500
```

### 2. Basic Usage

```python
from backend.vecna.gemini_service import GeminiService
from backend.vecna.auto_router import auto_route_user
from backend.config import get_config

# Initialize
config = get_config()
gemini = GeminiService(api_key=config.GEMINI_API_KEY)

# Auto-route user
result = await auto_route_user(
    user=current_user,
    message="How do I fix this Python bug?",
    current_room="Lobby",
    room_service=room_service,
    gemini_service=gemini
)

# Check if user was moved
if result['moved']:
    print(f"User moved to {result['to_room']}")
    await send_notification(user, result['notification'])
```

### 3. Agent Hook Integration

See `AGENT_HOOKS_GUIDE.md` for detailed integration instructions.

## Files

- `gemini_service.py` - Core Gemini AI service with routing methods
- `auto_router.py` - High-level routing functions for easy integration
- `AGENT_HOOKS_GUIDE.md` - Complete guide for agent hook integration
- `example_usage.py` - Example code demonstrating all features
- `README_AUTO_ROUTING.md` - This file

## Architecture

```
User Message
     │
     ▼
Analyze Relevance
     │
     ├─ Fits Current Room → Stay
     │
     └─ Doesn't Fit
          │
          ▼
     Suggest Best Room
          │
          ├─ Existing Room → Move User
          │
          └─ No Good Match → Flag for Room Creation
                │
                ▼
          Check Message Patterns
                │
                └─ Multiple Users + Same Topic → Create New Room
```

## Configuration Options

### Confidence Thresholds

Control how aggressive the routing is:

- **Conservative** (0.8-0.9): Only moves users when very confident
- **Balanced** (0.7-0.8): Good default for most use cases
- **Aggressive** (0.6-0.7): Moves users more frequently

### Message Thresholds

Control room creation sensitivity:

- **Conservative** (8-10 messages): Requires strong evidence
- **Balanced** (5-7 messages): Good default
- **Aggressive** (3-5 messages): Creates rooms more readily

## API Reference

### GeminiService Methods

#### `analyze_message_relevance(message, current_room, room_description)`
Analyzes if a message fits the current room.

**Returns**: `{"is_relevant": bool, "confidence": float, "reason": str}`

#### `suggest_best_room(message, available_rooms, user_profile)`
Suggests the best room for a message.

**Returns**: `{"suggested_room": str, "confidence": float, "reason": str, "should_create_new": bool, "new_room_topic": str}`

#### `should_create_new_room(recent_messages, available_rooms, threshold)`
Determines if a new room should be created.

**Returns**: `{"should_create": bool, "topic": str, "confidence": float, "reason": str, "affected_users": list}`

### Auto-Router Functions

#### `auto_route_user(user, message, current_room, room_service, gemini_service, confidence_threshold)`
Main routing function that analyzes and moves users.

**Returns**: `{"moved": bool, "from_room": str, "to_room": str, "reason": str, "confidence": float, "notification": str}`

#### `check_and_create_room(recent_messages, room_service, gemini_service, message_threshold, confidence_threshold)`
Checks if new room should be created and creates it.

**Returns**: `{"created": bool, "room_name": str, "description": str, "reason": str, "affected_users": list, "notification": str}`

## Examples

### Example 1: Simple Auto-Routing

```python
result = await auto_route_user(
    user, "How do I fix this bug?", "Lobby",
    room_service, gemini_service
)

if result['moved']:
    await notify_user(result['notification'])
```

### Example 2: Room Creation Check

```python
recent_messages = get_last_20_messages()

result = await check_and_create_room(
    recent_messages, room_service, gemini_service
)

if result['created']:
    await broadcast(result['notification'])
```

### Example 3: Custom Thresholds

```python
# More conservative routing
result = await auto_route_user(
    user, message, room,
    room_service, gemini_service,
    confidence_threshold=0.85  # Higher = more conservative
)
```

## Testing

Run the example script to see the system in action:

```bash
python backend/vecna/example_usage.py
```

This will demonstrate:
- Message relevance analysis
- Room suggestions
- Auto-routing
- Room creation
- Complete workflow

## Best Practices

1. **Start Conservative**: Use high confidence thresholds (0.8+) initially
2. **Monitor Logs**: Track routing decisions to tune thresholds
3. **User Feedback**: Allow users to provide feedback on routing
4. **Rate Limiting**: Don't check for new rooms on every message
5. **Clear Descriptions**: Ensure room descriptions are clear for better AI analysis

## Troubleshooting

### Users moved too often
→ Increase `confidence_threshold` to 0.85+

### Rooms created too frequently
→ Increase `message_threshold` to 8-10 and `confidence_threshold` to 0.85+

### API errors
→ Check logs, system has built-in fallbacks

### Users not notified
→ Ensure notifications are being sent to users

## Performance

- **API Calls**: 1-2 per message (cached when possible)
- **Latency**: ~200-500ms per analysis
- **Cost**: ~$0.0001 per message (Gemini pricing)

## Future Enhancements

- User preference learning
- Room popularity tracking
- Multi-language support
- Custom routing rules
- A/B testing framework

## Support

For issues or questions:
1. Check `AGENT_HOOKS_GUIDE.md` for integration help
2. Run `example_usage.py` to verify setup
3. Check logs for error messages
4. Review Gemini API status

## License

Part of the Phantom Link BBS project.
