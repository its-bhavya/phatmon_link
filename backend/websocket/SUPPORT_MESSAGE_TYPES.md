# Support Bot WebSocket Message Types

## Overview

This document defines the WebSocket message types used for the Empathetic Support Bot feature. These message types enable communication between the backend support system and the frontend UI to provide emotional support to users experiencing distress.

## Message Types

### 1. support_activation

**Purpose:** Sent when a user is flagged for support and a support room is created. This message includes the initial greeting from the Support Bot.

**Direction:** Backend → Frontend

**Requirements:** 2.1, 2.3, 2.4, 12.1, 12.3

**Structure:**
```json
{
  "type": "support_activation",
  "content": "string",
  "room_name": "string",
  "sentiment": {
    "emotion": "string",
    "intensity": "float"
  },
  "timestamp": "ISO 8601 string"
}
```

**Fields:**
- `type` (string, required): Always "support_activation"
- `content` (string, required): The greeting message from the Support Bot
- `room_name` (string, required): Name of the support room created for the user
- `sentiment` (object, required): Sentiment analysis results that triggered support
  - `emotion` (string): Type of emotion detected (sadness, anger, frustration, anxiety)
  - `intensity` (float): Intensity score from 0.0 to 1.0
- `timestamp` (string, required): ISO 8601 formatted timestamp

**Example:**
```json
{
  "type": "support_activation",
  "content": "[SUPPORT] Hi there. I noticed you might be going through a tough time. I'm here to listen without judgment. What's on your mind right now?",
  "room_name": "support_alice_1733356800",
  "sentiment": {
    "emotion": "sadness",
    "intensity": 0.75
  },
  "timestamp": "2024-12-04T18:30:00.000Z"
}
```

**Frontend Handling:**
1. Display the greeting message with [SUPPORT] prefix styling
2. Update UI to indicate user is in a support room
3. Apply support-specific visual styling (warm colors, empathetic tone)
4. Store room name for context

**Visual Requirements:**
- Message should be displayed with distinct support bot styling
- [SUPPORT] prefix should be highlighted in a warm color (e.g., amber/orange)
- Message content should use empathetic, readable formatting
- Clear visual distinction from regular chat messages

---

### 2. support_response

**Purpose:** Sent when the Support Bot generates a response to a user's message in a support room. Contains empathetic, context-aware guidance.

**Direction:** Backend → Frontend

**Requirements:** 4.1, 4.2, 4.3, 4.4, 12.1, 12.2

**Structure:**
```json
{
  "type": "support_response",
  "content": "string",
  "timestamp": "ISO 8601 string"
}
```

**Fields:**
- `type` (string, required): Always "support_response"
- `content` (string, required): The empathetic response from the Support Bot
- `timestamp` (string, required): ISO 8601 formatted timestamp

**Example:**
```json
{
  "type": "support_response",
  "content": "[SUPPORT] That sounds really difficult. It's completely understandable to feel overwhelmed when dealing with so much at once. Can you tell me more about what's been weighing on you the most?",
  "timestamp": "2024-12-04T18:31:15.000Z"
}
```

**Frontend Handling:**
1. Display the response with [SUPPORT] prefix styling
2. Apply empathetic visual styling
3. Maintain support room context
4. Ensure message is clearly from the Support Bot

**Content Characteristics:**
- Always includes [SUPPORT] prefix
- Demonstrates curiosity and empathy
- Uses warm, non-judgmental language
- Contains open-ended questions to encourage sharing
- Validates user's feelings
- Provides practical advice within appropriate boundaries
- Never includes mental health diagnoses

**Visual Requirements:**
- Consistent with support_activation styling
- Clear visual distinction from user messages
- Readable, accessible formatting
- Warm color scheme

---

### 3. crisis_hotlines

**Purpose:** Sent when a crisis situation is detected (self-harm, suicide, abuse). Provides appropriate Indian hotline numbers without conversational support.

**Direction:** Backend → Frontend

**Requirements:** 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 12.1, 12.2, 12.4

**Structure:**
```json
{
  "type": "crisis_hotlines",
  "content": "string",
  "crisis_type": "string",
  "hotlines": [
    {
      "name": "string",
      "number": "string",
      "description": "string"
    }
  ],
  "timestamp": "ISO 8601 string"
}
```

**Fields:**
- `type` (string, required): Always "crisis_hotlines"
- `content` (string, required): Encouragement message to reach out to professionals
- `crisis_type` (string, required): Type of crisis detected (self_harm, suicide, abuse)
- `hotlines` (array, required): List of relevant hotline information
  - `name` (string): Name of the hotline service
  - `number` (string): Phone number to call
  - `description` (string): Brief description of the service
- `timestamp` (string, required): ISO 8601 formatted timestamp

**Example:**
```json
{
  "type": "crisis_hotlines",
  "content": "[SUPPORT] I'm concerned about what you've shared. Please reach out to a professional who can provide immediate help. Here are some resources:",
  "crisis_type": "self_harm",
  "hotlines": [
    {
      "name": "AASRA",
      "number": "91-9820466726",
      "description": "24/7 crisis helpline"
    },
    {
      "name": "Vandrevala Foundation",
      "number": "1860-2662-345",
      "description": "Mental health support"
    }
  ],
  "timestamp": "2024-12-04T18:32:00.000Z"
}
```

**Frontend Handling:**
1. Display message with high visual prominence
2. Format hotline information clearly and accessibly
3. Use urgent but supportive styling
4. Make phone numbers easily readable and copyable
5. Emphasize the importance of professional help

**Visual Requirements:**
- Prominent display with high contrast
- Clear formatting of hotline information
- Service name, number, and description clearly separated
- Phone numbers in large, readable font
- Urgent but supportive color scheme (not alarming)
- Easy to copy phone numbers
- Clear visual hierarchy

**Content Characteristics:**
- Always includes [SUPPORT] prefix
- Brief encouragement to seek professional help
- No conversational support or advice
- Only hotline information and encouragement
- Appropriate hotlines for the specific crisis type

---

## Integration Guidelines

### Backend Implementation

The backend sends these message types through the WebSocket manager:

```python
# Support activation
await websocket_manager.send_to_user(websocket, {
    "type": "support_activation",
    "content": greeting_message,
    "room_name": support_room_name,
    "sentiment": {
        "emotion": sentiment_result.emotion.value,
        "intensity": sentiment_result.intensity
    },
    "timestamp": datetime.utcnow().isoformat()
})

# Support response
await websocket_manager.send_to_user(websocket, {
    "type": "support_response",
    "content": bot_response,
    "timestamp": datetime.utcnow().isoformat()
})

# Crisis hotlines
await websocket_manager.send_to_user(websocket, {
    "type": "crisis_hotlines",
    "content": encouragement_message,
    "crisis_type": crisis_type.value,
    "hotlines": [
        {
            "name": hotline.name,
            "number": hotline.number,
            "description": hotline.description
        }
        for hotline in hotlines
    ],
    "timestamp": datetime.utcnow().isoformat()
})
```

### Frontend Implementation

The frontend routes these messages through the main WebSocket handler:

```javascript
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

The SupportHandler class provides specialized handling:

```javascript
class SupportHandler {
    handleSupportActivation(message) {
        // Display greeting with support styling
        // Mark as in support room
        // Apply visual effects
    }
    
    handleSupportResponse(message) {
        // Display bot response with support styling
        // Maintain support context
    }
    
    handleCrisisHotlines(message) {
        // Display hotlines prominently
        // Format for easy reading
        // Emphasize urgency
    }
}
```

## Message Flow

### Support Activation Flow

```
User sends negative message
         ↓
Backend detects high-intensity negative sentiment
         ↓
Backend creates support room
         ↓
Backend sends support_activation message
         ↓
Frontend displays greeting and updates UI
         ↓
User is now in support room
```

### Support Conversation Flow

```
User sends message in support room
         ↓
Backend generates empathetic response with context
         ↓
Backend sends support_response message
         ↓
Frontend displays response with support styling
         ↓
Conversation continues
```

### Crisis Detection Flow

```
User sends message with crisis keywords
         ↓
Backend detects crisis situation
         ↓
Backend retrieves appropriate hotlines
         ↓
Backend sends crisis_hotlines message
         ↓
Frontend displays hotlines prominently
         ↓
No further conversational support provided
```

## Testing

### Backend Tests

Test that messages are correctly formatted:

```python
def test_support_activation_message_format():
    """Test support_activation message has required fields."""
    message = {
        "type": "support_activation",
        "content": "[SUPPORT] Greeting message",
        "room_name": "support_user_123",
        "sentiment": {
            "emotion": "sadness",
            "intensity": 0.75
        },
        "timestamp": "2024-12-04T18:30:00.000Z"
    }
    
    assert message["type"] == "support_activation"
    assert "[SUPPORT]" in message["content"]
    assert "room_name" in message
    assert "sentiment" in message
    assert "emotion" in message["sentiment"]
    assert "intensity" in message["sentiment"]

def test_support_response_message_format():
    """Test support_response message has required fields."""
    message = {
        "type": "support_response",
        "content": "[SUPPORT] Response message",
        "timestamp": "2024-12-04T18:31:00.000Z"
    }
    
    assert message["type"] == "support_response"
    assert "[SUPPORT]" in message["content"]
    assert "timestamp" in message

def test_crisis_hotlines_message_format():
    """Test crisis_hotlines message has required fields."""
    message = {
        "type": "crisis_hotlines",
        "content": "[SUPPORT] Please reach out",
        "crisis_type": "self_harm",
        "hotlines": [
            {
                "name": "AASRA",
                "number": "91-9820466726",
                "description": "24/7 crisis helpline"
            }
        ],
        "timestamp": "2024-12-04T18:32:00.000Z"
    }
    
    assert message["type"] == "crisis_hotlines"
    assert "[SUPPORT]" in message["content"]
    assert "crisis_type" in message
    assert "hotlines" in message
    assert len(message["hotlines"]) > 0
    assert "name" in message["hotlines"][0]
    assert "number" in message["hotlines"][0]
```

### Frontend Tests

Test that messages are correctly handled:

```javascript
// Test support activation handling
test('handleSupportActivation displays greeting', () => {
    const message = {
        type: 'support_activation',
        content: '[SUPPORT] Greeting',
        room_name: 'support_user_123',
        sentiment: { emotion: 'sadness', intensity: 0.75 }
    };
    
    supportHandler.handleSupportActivation(message);
    
    // Verify message is displayed
    // Verify support styling is applied
    // Verify room context is updated
});

// Test support response handling
test('handleSupportResponse displays response', () => {
    const message = {
        type: 'support_response',
        content: '[SUPPORT] Response'
    };
    
    supportHandler.handleSupportResponse(message);
    
    // Verify message is displayed
    // Verify support styling is applied
});

// Test crisis hotlines handling
test('handleCrisisHotlines displays hotlines', () => {
    const message = {
        type: 'crisis_hotlines',
        content: '[SUPPORT] Please reach out',
        crisis_type: 'self_harm',
        hotlines: [
            { name: 'AASRA', number: '91-9820466726', description: '24/7 crisis helpline' }
        ]
    };
    
    supportHandler.handleCrisisHotlines(message);
    
    // Verify hotlines are displayed prominently
    // Verify formatting is correct
});
```

## Compatibility

### Backward Compatibility

These message types are additive and do not break existing functionality:
- Existing message types continue to work unchanged
- Clients that don't handle support types will ignore them gracefully
- No changes required to existing message handlers

### Forward Compatibility

The message structure is designed to be extensible:
- Additional fields can be added without breaking existing clients
- Optional fields can be introduced for enhanced functionality
- Message versioning can be added if needed in the future

## Security Considerations

### Privacy Protection

- User messages are not included in logs in plaintext
- Sensitive content is anonymized before logging
- Support interactions are logged with hashed content
- Crisis detection logs use message hashes, not full content

### Data Handling

- All messages are transmitted over secure WebSocket connections
- Support room names include user identifiers but are private
- Hotline information is static and safe to transmit
- No personal health information is included in messages

## Requirements Mapping

### support_activation
- **2.1**: Creates dedicated support room
- **2.3**: Automatically joins user to support room
- **2.4**: Sends initial greeting message
- **12.1**: Messages prefixed with [SUPPORT]
- **12.3**: Welcome message explains Support Bot's purpose

### support_response
- **4.1**: Demonstrates curiosity about user's situation
- **4.2**: Expresses empathy for emotional state
- **4.3**: Uses warm, non-judgmental language
- **4.4**: Asks open-ended questions
- **12.1**: Messages prefixed with [SUPPORT]
- **12.2**: Uses distinct visual style

### crisis_hotlines
- **6.4**: No conversational support during crisis
- **6.5**: Provides relevant hotline numbers immediately
- **7.1**: Provides appropriate hotline for crisis type
- **7.2**: Provides appropriate hotline for crisis type
- **7.3**: Includes encouragement to reach out
- **7.4**: Formats hotline information clearly
- **12.1**: Messages prefixed with [SUPPORT]
- **12.2**: Uses distinct visual style
- **12.4**: Clarifies bot is not replacement for professional help

## Changelog

### Version 1.0 (2024-12-04)
- Initial definition of support message types
- Added support_activation, support_response, crisis_hotlines
- Defined message structures and requirements
- Added integration guidelines and testing instructions
