# Support Bot Overview

## Purpose

The Empathetic Support Bot is a compassionate AI assistant designed to provide emotional support to users experiencing distress. When the system detects that a user is expressing negative emotions (sadness, anger, frustration, or anxiety), it automatically creates a private support room and connects the user with an empathetic AI bot.

**The Support Bot is NOT:**
- A replacement for professional mental health care
- A licensed therapist or counselor
- A diagnostic tool for mental health conditions
- An emergency crisis intervention service

**The Support Bot IS:**
- A compassionate listener that provides a safe, non-judgmental space
- An AI assistant that demonstrates curiosity and empathy
- A source of practical coping strategies within appropriate boundaries
- A bridge to professional resources when crisis situations are detected

## How It Works

### 1. Automatic Detection

The system continuously analyzes messages for emotional content using sentiment analysis:

- **Negative Emotions Detected**: Sadness, anger, frustration, anxiety
- **Intensity Threshold**: Messages must exceed 0.6 intensity (on a 0.0-1.0 scale)
- **Crisis Keywords**: Self-harm, suicide, and abuse indicators trigger special handling

### 2. Support Room Creation

When negative sentiment is detected:

1. A private support room is created specifically for the user
2. The room is named uniquely (e.g., `support_alice_1733356800`)
3. The user is automatically joined to the support room
4. An initial greeting message is sent from the Support Bot

### 3. Empathetic Conversation

The Support Bot engages in conversation with these characteristics:

- **Curiosity**: Asks open-ended questions to understand the user's situation
- **Empathy**: Validates feelings and expresses understanding
- **Non-Judgmental**: Uses warm, accepting language without criticism
- **Practical Advice**: Offers general coping strategies appropriate for AI guidance
- **Context-Aware**: Uses knowledge of user interests and activity for personalization

### 4. Crisis Handling

If crisis keywords are detected (self-harm, suicide, abuse):

1. **No conversational support** is provided
2. **Immediate hotline information** is displayed with Indian crisis resources
3. **Encouragement to seek professional help** is emphasized
4. The crisis event is logged for monitoring

## Boundaries and Limitations

### What the Support Bot Will Do

✅ Listen without judgment  
✅ Ask questions to understand your situation  
✅ Validate your feelings and experiences  
✅ Suggest general coping strategies (breathing exercises, journaling, etc.)  
✅ Provide crisis hotline information when needed  
✅ Respect your autonomy to leave the conversation at any time  

### What the Support Bot Will NOT Do

❌ Diagnose mental health conditions  
❌ Prescribe medication or treatment plans  
❌ Provide therapy or clinical counseling  
❌ Make decisions for you  
❌ Judge or criticize your feelings or actions  
❌ Share your conversations with others (privacy protected)  
❌ Force you to continue the conversation  

## User Autonomy

### Leaving the Support Room

You can leave the support room at any time using:

```
/leave
```

When you leave:
- You'll return to your previous room
- The support room is preserved (you can return later)
- Your conversation history is maintained
- No one else can access your support room

### Returning to Support

If you want to return to your support room:

```
/join support_<your_username>_<timestamp>
```

Your conversation history will be available, and the Support Bot will continue from where you left off.

## Privacy and Security

### What We Collect

- **Sentiment Analysis Results**: Emotion type and intensity scores
- **Support Activation Events**: When and why support was triggered
- **Crisis Detections**: Type of crisis and hotlines provided
- **Interaction Logs**: Anonymized records of conversations

### What We Protect

- **Message Content**: All logged messages are hashed (not stored in plaintext)
- **User Identity**: Logs use anonymized identifiers
- **Conversation Privacy**: Support rooms are private to you only
- **No Third-Party Sharing**: Your interactions never leave our system

### Data Retention

- Support activation logs: Retained for system monitoring
- Crisis detection logs: Retained for safety analysis
- Conversation content: Hashed and anonymized
- User profiles: Retained while account is active

## Technical Architecture

### Components

1. **Sentiment Analyzer** (`backend/support/sentiment.py`)
   - Detects negative emotions in messages
   - Calculates intensity scores
   - Identifies crisis keywords

2. **Support Bot** (`backend/support/bot.py`)
   - Generates empathetic responses using Gemini AI
   - Maintains conversation context
   - Provides crisis hotline information

3. **Support Room Service** (`backend/support/room_service.py`)
   - Creates and manages private support rooms
   - Tracks active support sessions
   - Handles room lifecycle

4. **Crisis Hotline Service** (`backend/support/hotlines.py`)
   - Maintains database of Indian crisis hotlines
   - Formats hotline information for display
   - Matches crisis types to appropriate resources

5. **Support Logger** (`backend/support/logger.py`)
   - Logs support activations and interactions
   - Anonymizes sensitive content
   - Tracks system effectiveness

### Message Flow

```
User sends message
    ↓
Sentiment Analysis
    ↓
├─ Neutral/Positive → Normal chat continues
├─ Negative (Non-Crisis) → Support room created → Bot conversation
└─ Crisis Detected → Hotline information provided → No conversation
```

## Integration with Existing System

The Support Bot integrates seamlessly with the existing BBS chat system:

- **SysOp Brain**: Continues to handle normal message routing
- **Room System**: Support rooms work like regular rooms
- **WebSocket**: Uses existing WebSocket infrastructure
- **Commands**: Standard commands work in support rooms
- **User Profiles**: Leverages existing user profile data for context

## Requirements Fulfilled

The Support Bot implementation fulfills all 12 requirements from the specification:

1. **Negative Sentiment Detection** (Req 1): Detects sadness, anger, frustration, anxiety
2. **Support Room Creation** (Req 2): Creates private rooms with unique names
3. **User Context Provision** (Req 3): Provides message history, interests, room activity
4. **Empathetic Responses** (Req 4): Demonstrates curiosity and empathy
5. **Appropriate Boundaries** (Req 5): No therapy, no diagnoses, practical advice only
6. **Crisis Detection** (Req 6): Identifies self-harm, suicide, abuse situations
7. **Hotline Information** (Req 7): Provides Indian crisis hotlines
8. **Interaction Logging** (Req 8): Logs all support events with privacy protection
9. **Gemini AI Integration** (Req 9): Uses Gemini 2.5 Flash for response generation
10. **User Autonomy** (Req 10): Users can leave and return freely
11. **Seamless Integration** (Req 11): Works with existing message flow
12. **Distinct Identity** (Req 12): [SUPPORT] prefix and unique styling

## Getting Help

### For Users

If you're experiencing distress and the Support Bot is activated:
- Engage with the bot if you feel comfortable
- Leave the room at any time using `/leave`
- Seek professional help if you're in crisis (hotlines will be provided)

### For Administrators

If you need to monitor or configure the Support Bot:
- Check logs in `backend/support/logger.py`
- Configure thresholds in `.env` (SUPPORT_SENTIMENT_THRESHOLD)
- Review crisis detections in the database
- Update hotline information in `backend/support/hotlines.py`

### For Developers

If you're working on the Support Bot:
- Read the design document: `.kiro/specs/empathetic-support-bot/design.md`
- Review requirements: `.kiro/specs/empathetic-support-bot/requirements.md`
- Run tests: `pytest backend/tests/test_support_*.py`
- Check error handling: `backend/support/ERROR_HANDLING_SUMMARY.md`

## Future Enhancements

Potential improvements for the Support Bot:

1. **Multi-Language Support**: Hotlines and responses in multiple languages
2. **Customizable Thresholds**: Per-user sensitivity settings
3. **Support History**: View past support sessions
4. **Resource Library**: Curated self-help resources
5. **Peer Support**: Optional connection to trained peer supporters
6. **Feedback System**: Rate bot responses for continuous improvement

## Acknowledgments

The Support Bot is designed with input from mental health best practices and ethical AI guidelines. It aims to provide a helpful, safe space while always prioritizing user safety and professional care when needed.

**Remember**: The Support Bot is here to listen and support you, but it's not a replacement for professional help. If you're in crisis, please reach out to the hotlines provided or contact emergency services.
