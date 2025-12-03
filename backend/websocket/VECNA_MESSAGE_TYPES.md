# Vecna WebSocket Message Types

This document defines the WebSocket message types used for Vecna adversarial AI interactions.

## Overview

Vecna adds three new message types to the WebSocket protocol:
1. `vecna_emotional` - Emotional trigger with corrupted text
2. `vecna_psychic_grip` - System trigger with thread freeze
3. `vecna_release` - Psychic Grip release notification

These message types are sent from the backend to the frontend when Vecna activates based on emotional or system triggers.

## Message Type Definitions

### 1. vecna_emotional

Sent when Vecna activates via emotional trigger (high-intensity negative sentiment).

**Requirements:** 3.3, 9.1

**Structure:**
```json
{
  "type": "vecna_emotional",
  "content": "[VECNA] h0st1l3 r3sp0ns3 t3xt...",
  "corrupted_text": "c0rrupt3d v3rs10n 0f us3r m3ss@g3",
  "visual_effects": ["text_corruption"],
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

**Fields:**
- `type` (string): Always "vecna_emotional"
- `content` (string): Hostile response text with [VECNA] prefix
- `corrupted_text` (string): Corrupted version of the original user message
- `visual_effects` (array): List of visual effects to apply (e.g., ["text_corruption"])
- `timestamp` (string): ISO 8601 timestamp of when the message was generated

**Frontend Handling:**
- Display the corrupted text with special styling
- Apply text corruption visual effects
- Show [VECNA] prefix in distinct color/style
- Do NOT freeze input (emotional trigger only corrupts, doesn't freeze)

**Example:**
```javascript
{
  "type": "vecna_emotional",
  "content": "[VECNA] Y0ur fr@str@t10n 1s d3l1c10us...",
  "corrupted_text": "Th1s syst3m 1s t3rr1bl3!",
  "visual_effects": ["text_corruption"],
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

---

### 2. vecna_psychic_grip

Sent when Vecna activates via system trigger (spam, repeated commands, unusual activity).

**Requirements:** 4.1, 4.5, 9.1

**Structure:**
```json
{
  "type": "vecna_psychic_grip",
  "content": "[VECNA] I see you visiting #general... again and again...",
  "freeze_duration": 6,
  "visual_effects": ["screen_flicker", "inverted_colors", "scanlines", "static"],
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

**Fields:**
- `type` (string): Always "vecna_psychic_grip"
- `content` (string): Cryptic narrative text referencing user behavior with [VECNA] prefix
- `freeze_duration` (integer): Duration in seconds to freeze the thread (5-8 seconds)
- `visual_effects` (array): List of visual effects to apply during the grip
- `timestamp` (string): ISO 8601 timestamp of when the grip started

**Frontend Handling:**
- DISABLE chat input for the duration specified
- Apply all specified visual effects (screen flicker, inverted colors, scanlines, static)
- Display the narrative text with character-by-character animation
- Show [VECNA] prefix in distinct color/style
- Wait for `vecna_release` message before re-enabling input

**Visual Effects:**
- `screen_flicker`: Apply screen flicker animation
- `inverted_colors`: Invert terminal colors temporarily
- `scanlines`: Apply slow scanline ripple effect
- `static`: Show ASCII static storm overlay

**Example:**
```javascript
{
  "type": "vecna_psychic_grip",
  "content": "[VECNA] You keep typing /help... /help... /help... Do you really need help, or are you just... testing me?",
  "freeze_duration": 7,
  "visual_effects": ["screen_flicker", "inverted_colors", "scanlines"],
  "timestamp": "2024-01-15T10:30:00.000000"
}
```

---

### 3. vecna_release

Sent when Psychic Grip duration expires and control returns to SysOp Brain.

**Requirements:** 4.5, 9.2

**Structure:**
```json
{
  "type": "vecna_release",
  "content": "[SYSTEM] Control returned to SysOp. Continue your session."
}
```

**Fields:**
- `type` (string): Always "vecna_release"
- `content` (string): System message indicating control has returned

**Frontend Handling:**
- Remove all Vecna visual effects
- RE-ENABLE chat input
- Display the system message
- Restore normal terminal styling

**Example:**
```javascript
{
  "type": "vecna_release",
  "content": "[SYSTEM] Control returned to SysOp. Continue your session."
}
```

---

## Message Flow Examples

### Emotional Trigger Flow

1. User sends message with high-intensity negative sentiment
2. Backend evaluates triggers and detects emotional trigger
3. Backend sends `vecna_emotional` message
4. Frontend displays corrupted text with visual effects
5. Normal operation continues (no freeze)

```
User: "This system is terrible and broken!"
  ↓
Backend: Emotional trigger detected
  ↓
Frontend receives: vecna_emotional
  ↓
Display: "[VECNA] Y0ur @ng3r f33ds m3..."
  ↓
Normal operation resumes
```

### System Trigger Flow (Psychic Grip)

1. User triggers system pattern (spam, repeated commands, anomaly)
2. Backend evaluates triggers and detects system trigger
3. Backend sends `vecna_psychic_grip` message
4. Frontend freezes input and applies visual effects
5. Backend schedules `vecna_release` after freeze_duration
6. Frontend receives `vecna_release` and restores normal operation

```
User: Sends 5 messages in 3 seconds (spam)
  ↓
Backend: System trigger detected
  ↓
Frontend receives: vecna_psychic_grip (freeze_duration: 6)
  ↓
Frontend: Disable input, apply effects, show narrative
  ↓
Wait 6 seconds...
  ↓
Frontend receives: vecna_release
  ↓
Frontend: Remove effects, enable input
  ↓
Normal operation resumes
```

---

## Integration with Existing Message Types

Vecna message types integrate seamlessly with existing WebSocket message types:

**Existing Types:**
- `chat_message` - Regular chat messages
- `system` - System notifications
- `error` - Error messages
- `user_list` - Active user list updates
- `room_list` - Room list updates
- `room_change` - Room change notifications
- `help` - Help command responses

**Vecna Types:**
- `vecna_emotional` - Emotional trigger response
- `vecna_psychic_grip` - System trigger with freeze
- `vecna_release` - Grip release notification

All message types use the same WebSocket connection and JSON message format.

---

## Backend Implementation

The backend sends Vecna messages in `backend/main.py` within the WebSocket message handling loop:

```python
# Emotional trigger
if vecna_trigger.trigger_type == TriggerType.EMOTIONAL:
    vecna_response = await vecna_module.execute_emotional_trigger(...)
    await websocket_manager.send_to_user(websocket, {
        "type": "vecna_emotional",
        "content": vecna_response.content,
        "corrupted_text": vecna_response.corrupted_text,
        "visual_effects": vecna_response.visual_effects,
        "timestamp": vecna_response.timestamp.isoformat()
    })

# System trigger (Psychic Grip)
elif vecna_trigger.trigger_type == TriggerType.SYSTEM:
    vecna_response = await vecna_module.execute_psychic_grip(...)
    await websocket_manager.send_to_user(websocket, {
        "type": "vecna_psychic_grip",
        "content": vecna_response.content,
        "freeze_duration": vecna_response.freeze_duration,
        "visual_effects": vecna_response.visual_effects,
        "timestamp": vecna_response.timestamp.isoformat()
    })
    
    # Schedule release
    async def send_grip_release():
        await asyncio.sleep(vecna_response.freeze_duration)
        await websocket_manager.send_to_user(websocket, {
            "type": "vecna_release",
            "content": "[SYSTEM] Control returned to SysOp. Continue your session."
        })
    asyncio.create_task(send_grip_release())
```

---

## Frontend Implementation

The frontend handles Vecna messages in `frontend/js/main.js`:

```javascript
function handleWebSocketMessage(message) {
    switch (message.type) {
        // ... existing cases ...
        
        case 'vecna_emotional':
            handleVecnaEmotional(message);
            break;
            
        case 'vecna_psychic_grip':
            handleVecnaPsychicGrip(message);
            break;
            
        case 'vecna_release':
            handleVecnaRelease(message);
            break;
            
        // ... other cases ...
    }
}
```

---

## Testing

To test Vecna message types:

1. **Emotional Trigger Test:**
   - Send a message with high-intensity negative sentiment
   - Expected: Receive `vecna_emotional` message with corrupted text
   - Verify: Text corruption effects applied, no input freeze

2. **System Trigger Test (Spam):**
   - Send 3+ messages within 5 seconds
   - Expected: Receive `vecna_psychic_grip` message
   - Verify: Input disabled, visual effects applied, narrative displayed
   - Expected: Receive `vecna_release` after freeze_duration
   - Verify: Input re-enabled, effects removed

3. **System Trigger Test (Command Repetition):**
   - Execute same command 3+ times within 10 seconds
   - Expected: Receive `vecna_psychic_grip` message
   - Verify: Same as spam test

---

## Error Handling

If Vecna message processing fails:

1. **Backend Errors:**
   - Log error and continue normal operation
   - Do not send Vecna message if generation fails
   - Fall back to SysOp Brain control

2. **Frontend Errors:**
   - Log error to console
   - Display message as system message if Vecna handler fails
   - Ensure input is never permanently disabled

---

## Security Considerations

- Vecna messages are only sent to the specific user who triggered them
- Rate limiting prevents Vecna abuse (max 5 activations per hour per user)
- Cooldown period between activations (60 seconds)
- Admin controls can disable Vecna globally
- All Vecna activations are logged for monitoring

---

## Backward Compatibility

Vecna message types are additive and do not break existing functionality:

- Existing message types continue to work unchanged
- Clients that don't handle Vecna types will log unknown message warnings
- Normal chat flow continues if Vecna is disabled or fails
- WebSocket protocol version remains unchanged
