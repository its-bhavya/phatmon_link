# Design Document: Empathetic Support Bot

## Overview

The Empathetic Support Bot is a compassionate AI system that detects users experiencing negative emotions and connects them with an intelligent, empathetic bot in a dedicated support room. The system analyzes message sentiment to identify users who may benefit from emotional support, then creates a private conversation with context-aware guidance. For crisis situations involving self-harm or abuse, the system provides appropriate Indian hotline numbers without attempting therapeutic intervention.

The design follows a layered architecture where sentiment analysis identifies users in distress, a support room is created for private conversation, and the Support Bot provides empathetic responses using Gemini AI with appropriate safety boundaries. The system integrates seamlessly with the existing BBS infrastructure while replacing the Vecna adversarial AI module.

## Architecture

### System Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│  - Support room UI                                       │
│  - Message display with [SUPPORT] styling               │
│  - Crisis hotline information display                   │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                  WebSocket Layer                         │
│  - Message routing                                       │
│  - Support message types                                 │
│  - Room management                                       │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                   Backend Layer                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Message Processing Pipeline             │  │
│  │                                                   │  │
│  │  1. SysOp Brain (Initial Routing)               │  │
│  │           ↓                                      │  │
│  │  2. Sentiment Analysis                          │  │
│  │           ↓                                      │  │
│  │  3. Crisis Detection                            │  │
│  │           ↓                                      │  │
│  │  4. Support Bot Activation (if needed)          │  │
│  │           ↓                                      │  │
│  │  5. Return to Normal Flow                       │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Supporting Services                  │  │
│  │  - User Profile Service                          │  │
│  │  - Sentiment Analysis Service                    │  │
│  │  - Crisis Detection Service                      │  │
│  │  - Gemini AI Service                             │  │
│  │  - Support Room Service                          │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                   Data Layer                             │
│  - User profiles (interests, rooms, patterns)           │
│  - Support interaction logs                              │
│  - Crisis detection logs                                 │
└─────────────────────────────────────────────────────────┘
```

### Message Flow Diagram

```
User Message
     │
     ▼
SysOp Brain
  │  (Normal routing)
  │
  ▼
Sentiment Analysis
  │
  ├─── Neutral/Positive ────────────────────┐
  │                                          │
  ├─── Negative (Non-Crisis) ───────────────┤
  │    │                                     │
  │    ▼                                     │
  │  Create Support Room                    │
  │  Connect User to Support Bot            │
  │  Generate Empathetic Response           │
  │    │                                     │
  │    ▼                                     │
  │  Continue Support Conversation          │
  │    │                                     │
  ├─── Crisis Detected ──────────────────────┤
  │    │                                     │
  │    ▼                                     │
  │  Provide Hotline Information            │
  │  Log Crisis Event                       │
  │    │                                     │
  └────┴─────────────────────────────────────┘
                    │
                    ▼
          Back to Normal Flow
```

## Components and Interfaces

### Backend Components

#### 1. Sentiment Analysis Service (`backend/support/sentiment.py`)

Analyzes message sentiment to detect negative emotions and crisis situations.

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

class EmotionType(Enum):
    """Types of negative emotions detected."""
    SADNESS = "sadness"
    ANGER = "anger"
    FRUSTRATION = "frustration"
    ANXIETY = "anxiety"
    NEUTRAL = "neutral"
    POSITIVE = "positive"

class CrisisType(Enum):
    """Types of crisis situations."""
    SELF_HARM = "self_harm"
    SUICIDE = "suicide"
    ABUSE = "abuse"
    NONE = "none"

@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    emotion: EmotionType
    intensity: float  # 0.0 to 1.0
    requires_support: bool
    crisis_type: CrisisType
    keywords: List[str]

class SentimentAnalyzer:
    """
    Sentiment analysis for detecting emotional distress and crisis situations.
    """
    
    def __init__(self):
        self.negative_keywords = {
            EmotionType.SADNESS: ["sad", "depressed", "lonely", "hopeless", "empty", "worthless"],
            EmotionType.ANGER: ["angry", "furious", "hate", "rage", "pissed"],
            EmotionType.FRUSTRATION: ["frustrated", "annoyed", "irritated", "fed up", "stuck"],
            EmotionType.ANXIETY: ["anxious", "worried", "scared", "nervous", "panic", "afraid"]
        }
        
        self.crisis_keywords = {
            CrisisType.SELF_HARM: ["cut myself", "hurt myself", "self harm", "self-harm", "cutting"],
            CrisisType.SUICIDE: ["kill myself", "suicide", "end it all", "want to die", "suicidal"],
            CrisisType.ABUSE: ["abuse", "abused", "hitting me", "hurting me", "violence"]
        }
        
        self.intensity_threshold = 0.6
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze text for emotional content and crisis indicators.
        
        Returns:
            SentimentResult with emotion type, intensity, and crisis detection
        """
        pass
    
    def detect_crisis(self, text: str) -> CrisisType:
        """Check if text contains crisis keywords."""
        pass
    
    def calculate_intensity(self, text: str, keywords: List[str]) -> float:
        """Calculate intensity score based on keyword matches."""
        pass
```

#### 2. Support Bot Module (`backend/support/bot.py`)

The empathetic AI bot that provides emotional support.

```python
from typing import Optional
from backend.support.sentiment import SentimentResult, CrisisType
from backend.vecna.gemini_service import GeminiService
from backend.vecna.user_profile import UserProfile

class SupportBot:
    """
    Empathetic AI bot for providing emotional support.
    
    Responsibilities:
    - Generate empathetic responses
    - Provide practical advice within boundaries
    - Handle crisis situations appropriately
    - Maintain conversation context
    """
    
    def __init__(self, gemini_service: GeminiService):
        self.gemini = gemini_service
        self.bot_name = "Support Bot"
    
    async def generate_greeting(
        self, 
        user_profile: UserProfile,
        trigger_message: str,
        sentiment: SentimentResult
    ) -> str:
        """
        Generate initial greeting message for support room.
        
        Returns:
            Greeting message acknowledging user's emotional state
        """
        pass
    
    async def generate_response(
        self, 
        user_message: str,
        user_profile: UserProfile,
        conversation_history: List[dict]
    ) -> str:
        """
        Generate empathetic response to user message.
        
        Returns:
            Supportive response with curiosity and empathy
        """
        pass
    
    def generate_crisis_response(self, crisis_type: CrisisType) -> str:
        """
        Generate crisis response with appropriate hotline information.
        
        Returns:
            Message with hotline numbers and encouragement to seek help
        """
        pass
    
    def _create_empathetic_prompt(
        self,
        user_message: str,
        user_profile: UserProfile,
        conversation_history: List[dict]
    ) -> str:
        """Create prompt for Gemini with empathetic guidelines."""
        pass
```

#### 3. Support Room Service (`backend/support/room_service.py`)

Manages creation and lifecycle of support rooms.

```python
from typing import Optional, Dict
from datetime import datetime
from backend.database import User
from backend.rooms.service import RoomService

class SupportRoomService:
    """
    Service for managing support rooms.
    
    Responsibilities:
    - Create dedicated support rooms
    - Track active support sessions
    - Manage room lifecycle
    """
    
    def __init__(self, room_service: RoomService):
        self.room_service = room_service
        self.active_support_rooms: Dict[int, str] = {}  # user_id -> room_name
    
    def create_support_room(self, user: User) -> str:
        """
        Create a dedicated support room for a user.
        
        Returns:
            Room name for the support room
        """
        pass
    
    def get_support_room(self, user_id: int) -> Optional[str]:
        """Get the support room name for a user if it exists."""
        pass
    
    def is_support_room(self, room_name: str) -> bool:
        """Check if a room is a support room."""
        pass
    
    def close_support_room(self, user_id: int) -> None:
        """Close a support room when user leaves."""
        pass
```

#### 4. Crisis Hotline Service (`backend/support/hotlines.py`)

Provides crisis hotline information for India.

```python
from backend.support.sentiment import CrisisType
from typing import Dict, List

class HotlineInfo:
    """Information about a crisis hotline."""
    
    def __init__(self, name: str, number: str, description: str):
        self.name = name
        self.number = number
        self.description = description

class CrisisHotlineService:
    """
    Service providing crisis hotline information for India.
    """
    
    def __init__(self):
        self.hotlines = {
            CrisisType.SELF_HARM: [
                HotlineInfo(
                    "AASRA",
                    "91-9820466726",
                    "24/7 crisis helpline"
                ),
                HotlineInfo(
                    "Vandrevala Foundation",
                    "1860-2662-345",
                    "Mental health support"
                )
            ],
            CrisisType.SUICIDE: [
                HotlineInfo(
                    "AASRA",
                    "91-9820466726",
                    "24/7 crisis helpline"
                ),
                HotlineInfo(
                    "Sneha India",
                    "91-44-24640050",
                    "Suicide prevention"
                )
            ],
            CrisisType.ABUSE: [
                HotlineInfo(
                    "Women's Helpline",
                    "1091",
                    "For women in distress"
                ),
                HotlineInfo(
                    "Childline India",
                    "1098",
                    "For children in need"
                )
            ]
        }
    
    def get_hotlines(self, crisis_type: CrisisType) -> List[HotlineInfo]:
        """Get hotline information for a specific crisis type."""
        pass
    
    def format_hotline_message(self, crisis_type: CrisisType) -> str:
        """Format hotline information into a message."""
        pass
```

#### 5. Support Interaction Logger (`backend/support/logger.py`)

Logs support interactions for monitoring and improvement.

```python
from datetime import datetime
from sqlalchemy.orm import Session
from backend.support.sentiment import SentimentResult, CrisisType

class SupportInteractionLogger:
    """
    Logger for support bot interactions.
    
    Responsibilities:
    - Log support activations
    - Log crisis detections
    - Anonymize sensitive content
    - Track effectiveness metrics
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_support_activation(
        self,
        user_id: int,
        sentiment: SentimentResult,
        trigger_message: str
    ) -> None:
        """Log when support bot is activated for a user."""
        pass
    
    def log_crisis_detection(
        self,
        user_id: int,
        crisis_type: CrisisType,
        message: str
    ) -> None:
        """Log when a crisis situation is detected."""
        pass
    
    def log_bot_response(
        self,
        user_id: int,
        user_message: str,
        bot_response: str
    ) -> None:
        """Log a support bot interaction."""
        pass
    
    def _anonymize_content(self, content: str) -> str:
        """Anonymize sensitive content for logging."""
        pass
```

### Frontend Components

#### 1. Support Message Handler (`frontend/js/supportHandler.js`)

Handles support-specific message types from backend.

```javascript
class SupportHandler {
    /**
     * Handler for support bot messages and state management.
     */
    
    constructor(chatDisplay, commandBar) {
        this.chatDisplay = chatDisplay;
        this.commandBar = commandBar;
        this.inSupportRoom = false;
    }
    
    /**
     * Handle support room creation and initial greeting.
     */
    handleSupportActivation(message) {
        // Display greeting message
        // Mark as in support room
        // Apply support room styling
    }
    
    /**
     * Handle support bot response.
     */
    handleSupportResponse(message) {
        // Display bot message with [SUPPORT] prefix
        // Apply empathetic styling
    }
    
    /**
     * Handle crisis hotline information.
     */
    handleCrisisHotlines(message) {
        // Display hotline information prominently
        // Format for easy reading
        // Emphasize urgency
    }
    
    /**
     * Display support message with special styling.
     */
    displaySupportMessage(content) {
        // Add [SUPPORT] prefix
        // Apply support-specific CSS classes
    }
}
```

### Data Models

#### SentimentResult

```python
from enum import Enum
from dataclasses import dataclass

@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    emotion: EmotionType
    intensity: float
    requires_support: bool
    crisis_type: CrisisType
    keywords: List[str]
```

#### SupportSession

```python
@dataclass
class SupportSession:
    """Represents an active support session."""
    user_id: int
    room_name: str
    started_at: datetime
    trigger_message: str
    sentiment: SentimentResult
    conversation_history: List[dict]
```

### Database Schema Extensions

```sql
-- Support interaction logs
CREATE TABLE support_activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    emotion_type TEXT NOT NULL,
    intensity FLOAT NOT NULL,
    trigger_message_hash TEXT,  -- Hashed for privacy
    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Crisis detection logs
CREATE TABLE crisis_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    crisis_type TEXT NOT NULL,
    message_hash TEXT,  -- Hashed for privacy
    hotlines_provided TEXT,  -- JSON array of hotline names
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Support bot interactions
CREATE TABLE support_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_message_hash TEXT,  -- Hashed for privacy
    bot_response_hash TEXT,  -- Hashed for privacy
    interaction_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create indexes for performance
CREATE INDEX idx_support_activations_user ON support_activations(user_id);
CREATE INDEX idx_crisis_detections_user ON crisis_detections(user_id);
CREATE INDEX idx_support_interactions_user ON support_interactions(user_id);
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: High-intensity negative sentiment triggers support
*For any* message with high-intensity negative sentiment above the threshold, the system should flag the message for support intervention
**Validates: Requirements 1.1**

### Property 2: Negative emotion detection triggers support
*For any* message containing sadness, anger, frustration, or anxiety indicators, the system should classify the sentiment as requiring support
**Validates: Requirements 1.2, 1.3, 1.4, 1.5**

### Property 3: Support room creation for flagged users
*For any* user flagged for support, the system should create a dedicated support room
**Validates: Requirements 2.1**

### Property 4: Unique support room naming
*For any* set of support rooms created, all room names should be unique to prevent conflicts
**Validates: Requirements 2.2**

### Property 5: Automatic user joining to support room
*For any* support room created, the user should be automatically joined to that room
**Validates: Requirements 2.3**

### Property 6: Initial greeting on room join
*For any* user joining a support room, the system should send an initial greeting message from the Support Bot
**Validates: Requirements 2.4**

### Property 7: Support room privacy marking
*For any* support room created, the room should be marked as private to the user
**Validates: Requirements 2.5**

### Property 8: Bot receives message history context
*For any* Support Bot response generation, the system should provide the bot with the user's recent message history
**Validates: Requirements 3.1**

### Property 9: Bot receives user interests context
*For any* Support Bot response generation, the system should provide the bot with the user's interests from their profile
**Validates: Requirements 3.2**

### Property 10: Bot receives room activity context
*For any* Support Bot response generation, the system should provide the bot with the user's recent room activity
**Validates: Requirements 3.3**

### Property 11: Bot receives trigger message context
*For any* Support Bot response generation, the system should provide the bot with the original message that triggered support
**Validates: Requirements 3.4**

### Property 12: Read-only user data access
*For any* Support Bot access to user context, the user data should remain unchanged (read-only access)
**Validates: Requirements 3.5**

### Property 13: Bot responses include questions
*For any* Support Bot response, the response should contain at least one question to encourage sharing
**Validates: Requirements 4.4**

### Property 14: No mental health diagnoses in responses
*For any* Support Bot response, the response should not contain diagnostic terms for mental health conditions
**Validates: Requirements 5.4**

### Property 15: Self-harm crisis detection
*For any* message containing self-harm keywords, the system should classify the situation as a crisis
**Validates: Requirements 6.1**

### Property 16: Abuse crisis detection
*For any* message containing abuse keywords, the system should classify the situation as a crisis
**Validates: Requirements 6.2**

### Property 17: Suicide crisis detection
*For any* message containing suicide keywords, the system should classify the situation as a crisis
**Validates: Requirements 6.3**

### Property 18: No conversational support during crisis
*For any* crisis detection, the system should not generate a conversational support response
**Validates: Requirements 6.4**

### Property 19: Immediate hotline provision for crisis
*For any* crisis detection, the system should provide relevant Indian hotline numbers immediately
**Validates: Requirements 6.5**

### Property 20: Crisis responses include encouragement
*For any* crisis response sent, the message should include encouragement to reach out to professionals
**Validates: Requirements 7.3**

### Property 21: Hotline information formatting
*For any* crisis response sent, hotline information should be formatted with service name and number
**Validates: Requirements 7.4**

### Property 22: Crisis responses limited to hotlines
*For any* crisis response sent, the response should not include advice beyond hotline information
**Validates: Requirements 7.5**

### Property 23: Support activation logging
*For any* user flagged for support, the system should log the detection event with timestamp and sentiment score
**Validates: Requirements 8.1**

### Property 24: Support room creation logging
*For any* support room created, the system should log the room creation with user ID and trigger message
**Validates: Requirements 8.2**

### Property 25: Crisis detection logging
*For any* crisis detected, the system should log the crisis type and response provided
**Validates: Requirements 8.3**

### Property 26: Bot interaction logging
*For any* Support Bot response generated, the system should log the interaction for monitoring
**Validates: Requirements 8.4**

### Property 27: Privacy protection in logs
*For any* support interaction logged, sensitive content should be anonymized to protect user privacy
**Validates: Requirements 8.5**

### Property 28: Gemini API usage for responses
*For any* Support Bot response generation, the system should use Gemini 2.5 Flash API for content generation
**Validates: Requirements 9.1**

### Property 29: User context in API prompts
*For any* Gemini API call, the system should include user context in the prompt
**Validates: Requirements 9.2**

### Property 30: Empathetic guidelines in API prompts
*For any* Gemini API call, the system should include empathetic conversation guidelines in the prompt
**Validates: Requirements 9.3**

### Property 31: Graceful API error handling
*For any* Gemini API error, the system should handle the error gracefully with fallback responses
**Validates: Requirements 9.4**

### Property 32: Secure credential loading
*For any* Gemini API configuration, credentials should be loaded from environment variables
**Validates: Requirements 9.5**

### Property 33: User can leave support room
*For any* user in a support room, the user should be able to leave using standard commands
**Validates: Requirements 10.1**

### Property 34: Return to previous room on leave
*For any* user leaving a support room, the system should return the user to their previous room
**Validates: Requirements 10.2**

### Property 35: Support room preservation
*For any* user leaving a support room, the support room should be preserved for potential return
**Validates: Requirements 10.3**

### Property 36: Conversation history maintenance
*For any* user returning to a support room, the conversation history should be maintained
**Validates: Requirements 10.4**

### Property 37: SysOp Brain initial routing
*For any* message entering the system, the SysOp Brain should perform initial routing before support evaluation
**Validates: Requirements 11.1**

### Property 38: Support evaluation after routing
*For any* message processed, the system should evaluate whether support intervention is needed after initial routing
**Validates: Requirements 11.2**

### Property 39: Normal flow continuation without support
*For any* message where support is not needed, the system should continue normal SysOp Brain operation without interruption
**Validates: Requirements 11.3**

### Property 40: Control return after support
*For any* support intervention completed, the system should return message flow control to the SysOp Brain
**Validates: Requirements 11.4**

### Property 41: WebSocket compatibility
*For any* existing message type, the system should maintain compatibility with existing WebSocket communication
**Validates: Requirements 11.5**

### Property 42: Support message prefix
*For any* Support Bot message sent, the message should be prefixed with "[SUPPORT]" tag
**Validates: Requirements 12.1**

## Error Handling

### Backend Error Handling

#### 1. Gemini API Failures

```python
async def handle_gemini_error(error: Exception, context: str) -> str:
    """
    Handle Gemini API errors gracefully.
    
    Fallback strategy:
    1. Log error with context
    2. Use template-based empathetic responses
    3. Notify user of limited functionality
    4. Continue support session with fallback
    """
    logger.error(f"Gemini API error in {context}: {error}")
    
    fallback_responses = {
        "greeting": "I'm here to listen and support you. I'm experiencing some technical difficulties, but I'd still like to help. Can you tell me more about what's on your mind?",
        "response": "I hear you, and I want to understand better. Can you tell me more about how you're feeling?",
        "crisis": "I'm concerned about what you've shared. Please reach out to a professional who can provide immediate help."
    }
    
    return fallback_responses.get(context, fallback_responses["response"])
```

#### 2. Database Errors

```python
def handle_logging_error(error: Exception, log_type: str) -> None:
    """
    Handle database logging errors.
    
    Fallback strategy:
    1. Log error to file system
    2. Continue operation without blocking
    3. Alert administrators
    """
    logger.error(f"Database logging error for {log_type}: {error}")
    # Continue operation - logging failures shouldn't block support
```

#### 3. Sentiment Analysis Errors

```python
def safe_sentiment_analysis(message: str) -> SentimentResult:
    """
    Safely analyze sentiment with error handling.
    
    If analysis fails, return neutral sentiment to allow normal processing.
    """
    try:
        return sentiment_analyzer.analyze(message)
    except Exception as e:
        logger.error(f"Sentiment analysis error: {e}")
        return SentimentResult(
            emotion=EmotionType.NEUTRAL,
            intensity=0.0,
            requires_support=False,
            crisis_type=CrisisType.NONE,
            keywords=[]
        )
```

### Frontend Error Handling

#### 1. WebSocket Message Errors

```javascript
handleWebSocketMessage(message) {
    try {
        if (message.type === 'support_activation') {
            this.supportHandler.handleSupportActivation(message);
        } else if (message.type === 'support_response') {
            this.supportHandler.handleSupportResponse(message);
        } else if (message.type === 'crisis_hotlines') {
            this.supportHandler.handleCrisisHotlines(message);
        }
    } catch (error) {
        console.error('Error handling support message:', error);
        // Fallback to normal message display
        this.chatDisplay.addMessage({
            type: 'system',
            content: message.content || 'Support message'
        });
    }
}
```

## Testing Strategy

### Unit Testing

Unit tests will verify specific components and edge cases:

#### Backend Unit Tests

1. **Sentiment Analysis Tests** (`test_sentiment.py`)
   - Test negative emotion detection (sadness, anger, frustration, anxiety)
   - Test neutral and positive sentiment handling
   - Test crisis keyword detection (self-harm, suicide, abuse)
   - Test intensity calculation
   - Test edge cases (empty string, special characters, mixed emotions)

2. **Support Bot Tests** (`test_support_bot.py`)
   - Test greeting message generation
   - Test empathetic response generation
   - Test crisis response generation with hotlines
   - Test context inclusion in prompts
   - Test fallback responses for API errors

3. **Support Room Service Tests** (`test_support_room_service.py`)
   - Test support room creation
   - Test unique room naming
   - Test room lifecycle management
   - Test room privacy settings

4. **Crisis Hotline Service Tests** (`test_crisis_hotlines.py`)
   - Test hotline retrieval for each crisis type
   - Test hotline message formatting
   - Test correct Indian hotline numbers

5. **Support Logger Tests** (`test_support_logger.py`)
   - Test support activation logging
   - Test crisis detection logging
   - Test interaction logging
   - Test content anonymization

#### Frontend Unit Tests

1. **Support Handler Tests** (`test_support_handler.js`)
   - Test support activation handling
   - Test support response display
   - Test crisis hotline display
   - Test message formatting with [SUPPORT] prefix

### Property-Based Testing

Property-based tests will verify universal properties across many inputs using **Hypothesis** (Python) for backend testing:

#### Backend Property Tests

1. **Property Test: High-intensity negative sentiment triggers support** (`test_properties.py`)
   - Generate random messages with varying sentiment
   - Verify high-intensity negative messages trigger support
   - **Feature: empathetic-support-bot, Property 1: High-intensity negative sentiment triggers support**

2. **Property Test: Negative emotion detection triggers support** (`test_properties.py`)
   - Generate messages with various emotion keywords
   - Verify all negative emotions trigger support classification
   - **Feature: empathetic-support-bot, Property 2: Negative emotion detection triggers support**

3. **Property Test: Unique support room naming** (`test_properties.py`)
   - Generate multiple support room creation requests
   - Verify all room names are unique
   - **Feature: empathetic-support-bot, Property 4: Unique support room naming**

4. **Property Test: Crisis detection** (`test_properties.py`)
   - Generate messages with crisis keywords
   - Verify all crisis types are detected correctly
   - **Feature: empathetic-support-bot, Property 15, 16, 17: Crisis detection**

5. **Property Test: No conversational support during crisis** (`test_properties.py`)
   - Generate crisis messages
   - Verify no conversational support response is generated
   - **Feature: empathetic-support-bot, Property 18: No conversational support during crisis**

6. **Property Test: Support message prefix** (`test_properties.py`)
   - Generate random support bot responses
   - Verify all messages have [SUPPORT] prefix
   - **Feature: empathetic-support-bot, Property 42: Support message prefix**

7. **Property Test: Read-only user data access** (`test_properties.py`)
   - Generate random user profiles
   - Access profiles through Support Bot
   - Verify profiles remain unchanged
   - **Feature: empathetic-support-bot, Property 12: Read-only user data access**

8. **Property Test: Privacy protection in logs** (`test_properties.py`)
   - Generate random sensitive messages
   - Log interactions
   - Verify logged content is anonymized
   - **Feature: empathetic-support-bot, Property 27: Privacy protection in logs**

### Integration Testing

Integration tests will verify end-to-end workflows:

1. **Support Activation Flow**
   - User sends negative message
   - System detects sentiment
   - Support room is created
   - User is joined to room
   - Greeting is sent
   - Verify complete flow

2. **Crisis Detection Flow**
   - User sends crisis message
   - System detects crisis
   - Hotlines are provided
   - No conversational support
   - Crisis is logged
   - Verify complete flow

3. **Support Conversation Flow**
   - User in support room
   - User sends message
   - Bot generates response with context
   - Response includes question
   - Interaction is logged
   - Verify complete flow

4. **Room Leave and Return Flow**
   - User leaves support room
   - User returns to previous room
   - Support room is preserved
   - User returns to support room
   - History is maintained
   - Verify complete flow

## Migration from Vecna

### Files to Remove

1. `backend/vecna/module.py` - Vecna adversarial AI module
2. `backend/vecna/monitoring.py` - Vecna monitoring
3. `backend/vecna/rate_limiter.py` - Vecna-specific rate limiting
4. `backend/vecna/auto_router.py` - Vecna auto-routing
5. `test_psychic_grip_messages.py` - Vecna tests
6. `PSYCHIC_GRIP_ENHANCEMENT.md` - Vecna documentation
7. `BROWSER_TESTING_GUIDE.md` - Vecna testing guide
8. `.kiro/specs/vecna-adversarial-ai/` - Vecna spec directory
9. `.kiro/hooks/auto-route-message-send.kiro.hook` - Vecna hook

### Files to Keep and Modify

1. `backend/vecna/sentiment.py` - Rename to `backend/support/sentiment.py` and modify for empathetic support
2. `backend/vecna/gemini_service.py` - Keep for Support Bot AI generation
3. `backend/vecna/user_profile.py` - Keep for user context

### Configuration Changes

Update `.env` and `backend/config.py`:

```python
# Remove Vecna configuration
- VECNA_ENABLED
- VECNA_EMOTIONAL_THRESHOLD
- VECNA_SPAM_THRESHOLD
- VECNA_COMMAND_REPEAT_THRESHOLD
- VECNA_MAX_ACTIVATIONS_PER_HOUR
- VECNA_COOLDOWN_SECONDS

# Add Support Bot configuration
+ SUPPORT_BOT_ENABLED=true
+ SUPPORT_SENTIMENT_THRESHOLD=0.6
+ SUPPORT_CRISIS_DETECTION_ENABLED=true
```

### Database Migration

```sql
-- Drop Vecna tables
DROP TABLE IF EXISTS vecna_activations;
DROP TABLE IF EXISTS vecna_rate_limits;

-- Create Support Bot tables
CREATE TABLE support_activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    emotion_type TEXT NOT NULL,
    intensity FLOAT NOT NULL,
    trigger_message_hash TEXT,
    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE crisis_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    crisis_type TEXT NOT NULL,
    message_hash TEXT,
    hotlines_provided TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE support_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_message_hash TEXT,
    bot_response_hash TEXT,
    interaction_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Frontend Changes

1. Remove Vecna effects (`frontend/js/vecnaEffects.js`)
2. Remove Vecna handler (`frontend/js/vecnaHandler.js`)
3. Remove Vecna CSS styling
4. Add Support Bot handler (`frontend/js/supportHandler.js`)
5. Add Support Bot CSS styling (warm, empathetic colors)

## Security and Privacy Considerations

### Privacy Protection

1. **Content Anonymization**: All logged messages are hashed to protect user privacy
2. **Minimal Data Collection**: Only collect data necessary for support functionality
3. **Secure Storage**: User profiles and logs stored with appropriate access controls
4. **No Third-Party Sharing**: Support interactions never shared with external services

### Safety Boundaries

1. **No Therapeutic Claims**: Bot explicitly states it's not a therapist
2. **Crisis Escalation**: Immediate hotline provision for crisis situations
3. **No Diagnoses**: Bot never diagnoses mental health conditions
4. **Professional Referral**: Encourages seeking professional help when appropriate

### Ethical Guidelines

1. **Non-Judgmental**: Bot maintains warm, accepting tone
2. **Autonomy Respect**: Users can leave support at any time
3. **Transparency**: Clear about AI nature and limitations
4. **Harm Prevention**: Crisis detection prioritizes user safety

## Performance Considerations

### Response Time

- Sentiment analysis: < 100ms
- Support room creation: < 200ms
- Bot response generation: < 2s (Gemini API call)
- Crisis detection: < 50ms (keyword matching)

### Scalability

- Support rooms are lightweight (no special resources)
- Sentiment analysis uses efficient keyword matching
- Logging is asynchronous to avoid blocking
- Gemini API calls are rate-limited per user

### Resource Usage

- Memory: Minimal (user profiles cached, support sessions in-memory)
- Database: Moderate (logging all interactions)
- API: Gemini API calls only for bot responses (not crisis situations)
