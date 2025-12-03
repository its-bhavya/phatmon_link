# Design Document: Vecna Adversarial AI Module

## Overview

The Vecna Adversarial AI Module is a conditional adversarial layer that temporarily overrides the SysOp Brain to create tension and intrigue in the BBS experience. The system analyzes user messages and behavioral patterns to trigger adversarial interactions including text corruption, hostile responses, and temporary thread freezes ("Psychic Grip"). The module integrates seamlessly with the existing FastAPI backend and JavaScript frontend, using Gemini 2.5 Flash for AI-powered content generation.

The design follows a layered architecture where the SysOp Brain handles normal operations and Vecna conditionally intercepts messages based on emotional or system triggers. After Vecna activation, control always returns to the SysOp Brain to maintain system stability.

## Architecture

### System Layers

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
│  - Visual Effects (flicker, corruption, scanlines)      │
│  - UI State Management (freeze, disable input)          │
│  - Message Display (corrupted text, Vecna styling)      │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                  WebSocket Layer                         │
│  - Message routing                                       │
│  - Vecna message types                                   │
│  - State synchronization                                 │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                   Backend Layer                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │           Message Processing Pipeline             │  │
│  │                                                   │  │
│  │  1. SysOp Brain (Initial Routing)               │  │
│  │           ↓                                      │  │
│  │  2. Vecna Trigger Evaluation                    │  │
│  │           ↓                                      │  │
│  │  3. Conditional Vecna Activation                │  │
│  │           ↓                                      │  │
│  │  4. Return to SysOp Brain                       │  │
│  └───────────────────────────────────────────────────┘  │
│                                                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Supporting Services                  │  │
│  │  - User Profile Service                          │  │
│  │  - Sentiment Analysis Service                    │  │
│  │  - Pattern Detection Service                     │  │
│  │  - Gemini AI Service                             │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│                   Data Layer                             │
│  - User profiles (interests, rooms, patterns)           │
│  - Behavioral history                                    │
│  - Vecna activation logs                                 │
└─────────────────────────────────────────────────────────┘
```

### Message Flow Diagram

```
User Message
     │
     ▼
SysOp Brain
  │  (Normal routing, board creation, room suggestions)
  │
  ▼
Vecna Conditional Check
  │
  ├─── No Trigger ──────────────────────────┐
  │                                          │
  ├─── Emotional Trigger ───────────────────┤
  │    (High negative sentiment)             │
  │    │                                     │
  │    ▼                                     │
  │  Psychic Grip (5-8s freeze)             │
  │  Analyze user profile                   │
  │  Generate cryptic narrative             │
  │  (hostile but not offensive)            │
  │  Send to User                           │
  │    │                                     │
  └────┴─────────────────────────────────────┘
                    │
                    ▼
          Back to SysOp Brain
          (Resume normal operation)
```

## Components and Interfaces

### Backend Components

#### 1. SysOp Brain Service (`backend/sysop/brain.py`)

The primary AI routing system that handles normal BBS operations.

```python
class SysOpBrain:
    """
    Primary AI routing system for normal BBS operations.
    
    Responsibilities:
    - Message routing
    - Dynamic board creation
    - Room suggestions based on user profiles
    - Workflow management
    """
    
    def __init__(self, gemini_service: GeminiService, room_service: RoomService):
        self.gemini = gemini_service
        self.room_service = room_service
    
    async def process_message(
        self, 
        user: User, 
        message: str, 
        current_room: str
    ) -> Dict[str, Any]:
        """
        Process incoming message with normal routing logic.
        
        Returns:
            Dict containing routing decision and suggested actions
        """
        pass
    
    async def suggest_rooms(self, user_profile: UserProfile) -> List[str]:
        """Generate room suggestions based on user interests and activity."""
        pass
    
    async def create_dynamic_board(
        self, 
        topic: str, 
        user: User
    ) -> Optional[Room]:
        """Create a new board dynamically based on conversation topic."""
        pass
```

#### 2. Vecna Module (`backend/vecna/module.py`)

The adversarial AI component that conditionally overrides SysOp Brain.

```python
class VecnaModule:
    """
    Adversarial AI module for conditional hostile interactions.
    
    Responsibilities:
    - Trigger evaluation (emotional and system)
    - Text corruption
    - Hostile response generation
    - Psychic Grip execution
    """
    
    def __init__(
        self, 
        gemini_service: GeminiService,
        sentiment_analyzer: SentimentAnalyzer
    ):
        self.gemini = gemini_service
        self.sentiment = sentiment_analyzer
        self.psychic_grip_duration = (5, 8)  # seconds range
    
    async def evaluate_triggers(
        self, 
        user: User, 
        message: str,
        user_profile: UserProfile
    ) -> Optional[VecnaTrigger]:
        """
        Evaluate if Vecna should activate.
        
        Returns:
            VecnaTrigger object if triggered, None otherwise
        """
        pass
    
    async def execute_emotional_trigger(
        self, 
        user: User, 
        message: str,
        user_profile: UserProfile
    ) -> VecnaResponse:
        """
        Execute emotional trigger: freeze thread and generate cryptic narrative.
        
        Returns:
            VecnaResponse with freeze duration and cryptic narrative content
        """
        pass
    
    async def execute_psychic_grip(
        self, 
        user: User,
        user_profile: UserProfile
    ) -> VecnaResponse:
        """
        Execute Psychic Grip: freeze thread and generate cryptic narrative.
        
        Returns:
            VecnaResponse with freeze duration and narrative content
        """
        pass
    
    def corrupt_text(self, text: str, corruption_level: float = 0.3) -> str:
        """
        Apply character substitution and garbling to text.
        
        Args:
            text: Original text
            corruption_level: Percentage of characters to corrupt (0.0-1.0)
        
        Returns:
            Corrupted text string
        """
        pass
```

#### 3. User Profile Service (`backend/vecna/user_profile.py`)

Tracks and analyzes user behavioral patterns for Vecna.

```python
class UserProfile:
    """
    User behavioral profile for Vecna analysis.
    
    Attributes:
        user_id: User database ID
        interests: List of detected interests
        frequent_rooms: Dict mapping room names to visit counts
        recent_rooms: List of recently visited rooms (last 10)
        command_history: List of recent commands with timestamps
        unfinished_boards: List of boards created but abandoned
        activity_baseline: Statistical baseline for normal activity
        behavioral_patterns: Detected patterns (repetition, spam, etc.)
    """
    
    user_id: int
    interests: List[str]
    frequent_rooms: Dict[str, int]
    recent_rooms: List[str]
    command_history: List[Tuple[str, datetime]]
    unfinished_boards: List[str]
    activity_baseline: Dict[str, float]
    behavioral_patterns: Dict[str, Any]
    

```

```python
class UserProfileService:
    """
    Service for managing user profiles and behavioral tracking.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.profiles: Dict[int, UserProfile] = {}
    
    def get_profile(self, user_id: int) -> UserProfile:
        """Get or create user profile."""
        pass
    
    def record_room_visit(self, user_id: int, room_name: str) -> None:
        """Record a room visit in user profile."""
        pass
    
    def record_command(self, user_id: int, command: str) -> None:
        """Record a command execution."""
        pass
    
    def record_board_creation(
        self, 
        user_id: int, 
        board_name: str, 
        completed: bool = False
    ) -> None:
        """Record board creation and completion status."""
        pass
    
    def update_interests(self, user_id: int, message: str) -> None:
        """Extract and update user interests from message content."""
        pass
```

#### 4. Sentiment Analysis Service (`backend/vecna/sentiment.py`)

Analyzes message sentiment to detect emotional triggers.

```python
class SentimentAnalyzer:
    """
    Sentiment analysis for detecting emotional triggers.
    """
    
    def __init__(self):
        self.negative_keywords = [
            "hate", "angry", "frustrated", "terrible", "awful",
            "broken", "useless", "stupid", "worst", "fail"
        ]
        self.intensity_threshold = 0.7
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analyze text sentiment.
        
        Returns:
            SentimentResult with polarity, intensity, and trigger status
        """
        pass
    
    def is_high_negative_intensity(self, text: str) -> bool:
        """Check if text contains high-intensity negative sentiment."""
        pass
```

#### 5. Gemini AI Service (`backend/vecna/gemini_service.py`)

Interface to Gemini 2.5 Flash for AI content generation.

```python
class GeminiService:
    """
    Service for interacting with Gemini 2.5 Flash API.
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "gemini-2.5-flash"
        self.client = self._initialize_client()
    
    async def generate_sysop_suggestion(
        self, 
        user_profile: UserProfile,
        context: str
    ) -> str:
        """Generate SysOp Brain room suggestion or response."""
        pass
    
    async def generate_hostile_response(
        self, 
        user_message: str,
        user_profile: UserProfile
    ) -> str:
        """
        Generate Vecna hostile response to user message.
        
        Uses adversarial prompting to create degraded, hostile content.
        """
        pass
    
    async def generate_psychic_grip_narrative(
        self, 
        user_profile: UserProfile
    ) -> str:
        """
        Generate cryptic Psychic Grip narrative based on user behavior.
        
        References:
        - Frequent rooms
        - Repetitive actions
        - Unfinished tasks
        - Behavioral patterns
        """
        pass
    
    def _create_adversarial_prompt(
        self, 
        user_message: str,
        user_profile: UserProfile
    ) -> str:
        """Create adversarial prompt for Vecna responses."""
        pass
```

### Frontend Components

#### 1. Vecna Effects Manager (`frontend/js/vecnaEffects.js`)

Manages visual effects during Vecna activation.

```javascript
class VecnaEffects {
    /**
     * Vecna visual effects manager.
     * 
     * Responsibilities:
     * - Screen flicker
     * - Inverted colors
     * - Scanline ripple
     * - ASCII static storm
     * - Text corruption display
     */
    
    constructor(chatDisplay) {
        this.chatDisplay = chatDisplay;
        this.isActive = false;
        this.effectsContainer = null;
    }
    

    
    /**
     * Start Psychic Grip visual effects.
     */
    startPsychicGrip(duration) {
        // Apply screen flicker, inverted colors, scanlines
        // Disable input
        // Show ASCII static overlay
    }
    
    /**
     * End Psychic Grip and restore normal display.
     */
    endPsychicGrip() {
        // Remove all effects
        // Re-enable input
        // Show system message
    }
    
    /**
     * Apply screen flicker effect.
     */
    applyScreenFlicker() {
        // CSS animation for screen flicker
    }
    
    /**
     * Apply inverted color effect.
     */
    applyInvertedColors() {
        // Invert terminal colors temporarily
    }
    
    /**
     * Apply scanline ripple effect.
     */
    applyScanlineRipple() {
        // Animated scanline distortion
    }
    
    /**
     * Show ASCII static storm overlay.
     */
    showStaticStorm() {
        // Generate and animate ASCII static characters
    }
}
```

#### 2. Vecna Message Handler (`frontend/js/vecnaHandler.js`)

Handles Vecna-specific message types from backend.

```javascript
class VecnaHandler {
    /**
     * Handler for Vecna messages and state management.
     */
    
    constructor(chatDisplay, commandBar, vecnaEffects) {
        this.chatDisplay = chatDisplay;
        this.commandBar = commandBar;
        this.vecnaEffects = vecnaEffects;
        this.isGripActive = false;
    }
    
    /**
     * Handle Vecna emotional trigger message (Psychic Grip).
     */
    handleEmotionalTrigger(message) {
        // Same as handlePsychicGrip - unified approach
        // Freeze input, start visual effects, display narrative
    }
    
    /**
     * Handle Psychic Grip activation.
     */
    handlePsychicGrip(message) {
        // Freeze input
        // Start visual effects
        // Display narrative with slow character animation
        // Schedule grip release
    }
    
    /**
     * Handle Psychic Grip release.
     */
    handleGripRelease() {
        // End visual effects
        // Re-enable input
        // Show system message
    }
    
    /**
     * Display Vecna message with special styling.
     */
    displayVecnaMessage(content, isGrip = false) {
        // Add [VECNA] prefix
        // Apply Vecna-specific CSS classes
        // Optionally animate character-by-character
    }
}
```

### Data Models

#### VecnaTrigger

```python
from enum import Enum
from dataclasses import dataclass

class TriggerType(Enum):
    EMOTIONAL = "emotional"
    SYSTEM = "system"
    NONE = "none"

@dataclass
class VecnaTrigger:
    """Represents a Vecna trigger event."""
    trigger_type: TriggerType
    reason: str
    intensity: float
    user_id: int
    timestamp: datetime
```

#### VecnaResponse

```python
@dataclass
class VecnaResponse:
    """Response from Vecna activation."""
    trigger_type: TriggerType
    content: str
    corrupted_text: Optional[str]
    freeze_duration: Optional[int]  # seconds
    visual_effects: List[str]
    timestamp: datetime
```

#### SentimentResult

```python
@dataclass
class SentimentResult:
    """Result of sentiment analysis."""
    polarity: float  # -1.0 (negative) to 1.0 (positive)
    intensity: float  # 0.0 to 1.0
    is_trigger: bool
    keywords: List[str]
```

### Database Schema Extensions

```sql
-- User profile behavioral data
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    interests TEXT,  -- JSON array
    frequent_rooms TEXT,  -- JSON object
    recent_rooms TEXT,  -- JSON array
    activity_baseline TEXT,  -- JSON object
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Command history for pattern detection
CREATE TABLE command_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    command TEXT NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Board creation tracking
CREATE TABLE board_tracking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    board_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Vecna activation logs
CREATE TABLE vecna_activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    trigger_type TEXT NOT NULL,
    reason TEXT,
    intensity FLOAT,
    response_content TEXT,
    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Create indexes for performance
CREATE INDEX idx_command_history_user_time ON command_history(user_id, executed_at);
CREATE INDEX idx_vecna_activations_user ON vecna_activations(user_id);
CREATE INDEX idx_board_tracking_user ON board_tracking(user_id);
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: SysOp Brain baseline routing
*For any* user message when no Vecna trigger occurs, the SysOp Brain should route the message and perform normal board creation operations
**Validates: Requirements 1.1**

### Property 2: User profile data access
*For any* message processed by SysOp Brain, the system should query and use user profile data including interests, recent rooms, and activity patterns
**Validates: Requirements 1.2**

### Property 3: Control resumption after Vecna
*For any* Vecna activation, after Vecna completes, the next message should be processed by the SysOp Brain with normal routing
**Validates: Requirements 1.3, 6.4**

### Property 4: Room suggestion generation
*For any* user profile, the SysOp Brain should generate room suggestions based on profile analysis
**Validates: Requirements 1.4**

### Property 5: Board persistence
*For any* dynamically created board, the board should persist in the system and be retrievable in future sessions
**Validates: Requirements 1.5**

### Property 6: Emotional trigger activation
*For any* message with high-intensity negative sentiment above the threshold, Vecna should activate in emotional trigger mode
**Validates: Requirements 2.1**

### Property 7: Vecna control override
*For any* Vecna activation, the message should be processed by Vecna instead of normal SysOp Brain processing
**Validates: Requirements 2.2, 3.1**

### Property 8: Psychic Grip for emotional triggers
*For any* emotional trigger activation, the system should freeze the thread for 5-8 seconds and generate cryptic narrative
**Validates: Requirements 3.2**

### Property 9: Hostile but not offensive tone
*For any* emotional trigger activation, the cryptic narrative should be hostile in tone but not offensive or abusive
**Validates: Requirements 3.4**

### Property 10: Profile reference in emotional narrative
*For any* emotional trigger Psychic Grip, the narrative should reference the user's emotional state and profile data
**Validates: Requirements 3.5**

### Property 11: Thread freeze duration
*For any* Vecna activation, the thread should be frozen for a duration between 5 and 8 seconds
**Validates: Requirements 4.1**

### Property 12: Input disabling during Psychic Grip
*For any* Psychic Grip activation, chat input should be disabled for all affected users during the freeze duration
**Validates: Requirements 4.2**

### Property 13: Profile data in narrative
*For any* Psychic Grip narrative, the content should reference at least one element from the user profile (frequent rooms, repetitive actions, unfinished tasks, or behavioral patterns)
**Validates: Requirements 4.3**

### Property 14: Grip release message
*For any* Psychic Grip activation, after the duration expires, the system should send the message "[SYSTEM] Control returned to SysOp. Continue your session."
**Validates: Requirements 4.5, 9.2**

### Property 15: Visual effects application
*For any* Vecna activation, appropriate visual effects should be applied (screen flicker, inverted colors, scanlines during Psychic Grip)
**Validates: Requirements 5.1**

### Property 16: Visual effects cleanup
*For any* Vecna deactivation, all special visual effects should be removed and normal rendering restored
**Validates: Requirements 5.5, 9.5**

### Property 17: Processing order
*For any* incoming message, the SysOp Brain should perform initial routing before Vecna trigger evaluation
**Validates: Requirements 6.1, 6.2**

### Property 18: Normal path continuation
*For any* message where Vecna triggers are not met, the system should continue normal SysOp Brain operation without interruption
**Validates: Requirements 6.3**

### Property 19: WebSocket compatibility
*For any* existing message type, the system should maintain backward compatibility with existing WebSocket communication
**Validates: Requirements 6.5**

### Property 20: Room visit tracking
*For any* room join event, the user profile should be updated to include that room in recent rooms and increment frequent rooms count
**Validates: Requirements 7.1**

### Property 21: Command tracking
*For any* command execution, the command should be recorded in the user profile command history with timestamp
**Validates: Requirements 7.2**

### Property 22: Board creation tracking
*For any* board creation, the system should record the board in the user profile with completion status
**Validates: Requirements 7.3**

### Property 23: Read-only profile access
*For any* Vecna access to user profile data, the profile should not be modified (read-only access)
**Validates: Requirements 7.5**

### Property 24: Gemini API integration
*For any* SysOp Brain room suggestion, Vecna hostile response, or Psychic Grip narrative, the system should call the Gemini 2.5 Flash API
**Validates: Requirements 8.1, 8.2, 8.3**

### Property 25: API error handling
*For any* Gemini API error, the system should handle the error gracefully and fall back to SysOp Brain control without crashing
**Validates: Requirements 8.4**

### Property 26: Secure credential storage
*For any* Gemini API configuration, credentials should be loaded from environment variables, not hardcoded
**Validates: Requirements 8.5**

### Property 27: Vecna message prefix
*For any* Vecna message, the content should be prefixed with "[VECNA]" tag
**Validates: Requirements 9.1**

### Property 28: Vecna message styling
*For any* Vecna message, distinct CSS classes should be applied for visual differentiation
**Validates: Requirements 9.3**

### Property 29: Character animation
*For any* Psychic Grip message, the text should be rendered with character-by-character animation
**Validates: Requirements 9.4**

## Error Handling

### Backend Error Handling

#### 1. Gemini API Failures

```python
async def handle_gemini_error(error: Exception, context: str) -> str:
    """
    Handle Gemini API errors gracefully.
    
    Fallback strategy:
    1. Log error with context
    2. Return to SysOp Brain control
    3. Use template-based responses if AI unavailable
    4. Notify user of degraded functionality
    """
    logger.error(f"Gemini API error in {context}: {error}")
    
    if context == "vecna_hostile":
        return "[VECNA] sYst3m m@lfunct10n... c0ntr0l r3turn1ng..."
    elif context == "psychic_grip":
        return "[VECNA] ...c0nn3ct10n l0st... r3l3as1ng gr1p..."
    else:
        return "System experiencing difficulties. Returning to normal operation."
```

#### 2. Database Errors

```python
def handle_profile_error(error: Exception, user_id: int) -> UserProfile:
    """
    Handle user profile database errors.
    
    Fallback strategy:
    1. Log error
    2. Return default profile
    3. Continue operation with limited data
    """
    logger.error(f"Profile error for user {user_id}: {error}")
    return UserProfile.create_default(user_id)
```

#### 3. Trigger Evaluation Errors

```python
async def safe_trigger_evaluation(
    user: User, 
    message: str,
    user_profile: UserProfile
) -> Optional[VecnaTrigger]:
    """
    Safely evaluate triggers with error handling.
    
    If evaluation fails, return None (no trigger) to allow normal processing.
    """
    try:
        return await vecna.evaluate_triggers(user, message, user_profile)
    except Exception as e:
        logger.error(f"Trigger evaluation error: {e}")
        return None
```

### Frontend Error Handling

#### 1. WebSocket Message Errors

```javascript
handleWebSocketMessage(message) {
    try {
        // Process message
        if (message.type === 'vecna_emotional') {
            this.vecnaHandler.handleEmotionalTrigger(message);
        } else if (message.type === 'vecna_psychic_grip') {
            this.vecnaHandler.handlePsychicGrip(message);
        }
    } catch (error) {
        console.error('Error handling Vecna message:', error);
        // Fallback to normal message display
        this.chatDisplay.addMessage({
            type: 'system',
            content: message.content || 'System message'
        });
    }
}
```

#### 2. Visual Effects Errors

```javascript
startPsychicGrip(duration) {
    try {
        this.applyScreenFlicker();
        this.applyInvertedColors();
        this.applyScanlineRipple();
        this.showStaticStorm();
    } catch (error) {
        console.error('Error applying Vecna effects:', error);
        // Continue without effects
    }
    
    // Always schedule cleanup
    setTimeout(() => {
        this.endPsychicGrip();
    }, duration * 1000);
}
```

## Testing Strategy

### Unit Testing

Unit tests will verify specific components and edge cases:

#### Backend Unit Tests

1. **Sentiment Analysis Tests** (`test_sentiment.py`)
   - Test high-negative sentiment detection
   - Test neutral sentiment handling
   - Test positive sentiment handling
   - Test edge cases (empty string, special characters)

2. **User Profile Tests** (`test_user_profile.py`)
   - Test profile creation and initialization
   - Test room visit recording
   - Test command history tracking
   - Test board creation tracking

3. **Gemini Service Tests** (`test_gemini_service.py`)
   - Test API call formatting
   - Test error handling
   - Test prompt generation for Psychic Grip narratives
   - Test response parsing

#### Frontend Unit Tests

1. **Vecna Effects Tests** (`test_vecna_effects.js`)
   - Test Psychic Grip activation
   - Test visual effects application (flicker, inverted colors, scanlines, static)
   - Test cleanup after deactivation

2. **Vecna Handler Tests** (`test_vecna_handler.js`)
   - Test Psychic Grip handling (both emotional and system triggers)
   - Test message formatting with [VECNA] prefix
   - Test state management and input disabling
   - Test character-by-character animation

### Property-Based Testing

Property-based tests will verify universal properties across many inputs using **Hypothesis** (Python) for backend testing:

#### Backend Property Tests

1. **Property Test: SysOp Brain baseline routing** (`test_properties.py`)
   - Generate random messages without triggers
   - Verify SysOp Brain processes all messages
   - **Feature: vecna-adversarial-ai, Property 1: SysOp Brain baseline routing**

2. **Property Test: Control resumption after Vecna** (`test_properties.py`)
   - Generate random Vecna activations
   - Verify next message goes to SysOp Brain
   - **Feature: vecna-adversarial-ai, Property 3: Control resumption after Vecna**

3. **Property Test: Emotional trigger activation** (`test_properties.py`)
   - Generate messages with varying sentiment
   - Verify high-negative triggers Vecna
   - **Feature: vecna-adversarial-ai, Property 6: Emotional trigger activation**

4. **Property Test: Psychic Grip for emotional triggers** (`test_properties.py`)
   - Generate random emotional triggers
   - Verify Psychic Grip is activated with 5-8 second freeze
   - **Feature: vecna-adversarial-ai, Property 11: Psychic Grip for emotional triggers**

5. **Property Test: Hostile but not offensive tone** (`test_properties.py`)
   - Generate random emotional trigger narratives
   - Verify tone is hostile but not offensive or abusive
   - **Feature: vecna-adversarial-ai, Property 9: Hostile but not offensive tone**

6. **Property Test: Thread freeze duration** (`test_properties.py`)
   - Generate random emotional triggers
   - Verify freeze duration is between 5-8 seconds
   - **Feature: vecna-adversarial-ai, Property 11: Thread freeze duration**

7. **Property Test: Profile data in narrative** (`test_properties.py`)
   - Generate random user profiles
   - Verify Psychic Grip narratives reference profile data
   - **Feature: vecna-adversarial-ai, Property 13: Profile data in narrative**

8. **Property Test: Room visit tracking** (`test_properties.py`)
   - Generate random room join events
   - Verify profile is updated correctly
   - **Feature: vecna-adversarial-ai, Property 20: Room visit tracking**

9. **Property Test: Read-only profile access** (`test_properties.py`)
   - Generate random Vecna activations
   - Verify profile is not modified by Vecna
   - **Feature: vecna-adversarial-ai, Property 23: Read-only profile access**

10. **Property Test: Vecna message prefix** (`test_properties.py`)
    - Generate random Vecna messages
    - Verify all contain "[VECNA]" prefix
    - **Feature: vecna-adversarial-ai, Property 27: Vecna message prefix**

### Integration Testing

Integration tests will verify end-to-end workflows:

1. **Full Emotional Trigger Flow**
   - Send high-negative message
   - Verify Vecna activation
   - Verify Psychic Grip freeze (5-8 seconds)
   - Verify cryptic narrative generation
   - Verify control return to SysOp



2. **Profile Tracking Integration**
   - Perform various user actions
   - Verify profile updates
   - Verify Vecna can access profile data

3. **Gemini API Integration**
   - Test SysOp Brain suggestions
   - Test Vecna hostile responses
   - Test Psychic Grip narratives
   - Test error handling

### Testing Configuration

All property-based tests will be configured to run a minimum of 100 iterations to ensure comprehensive coverage of the input space.

```python
# Example property test configuration
from hypothesis import given, settings
import hypothesis.strategies as st

@settings(max_examples=100)
@given(message=st.text(min_size=1, max_size=500))
def test_vecna_message_prefix(message):
    """
    Feature: vecna-adversarial-ai, Property 31: Vecna message prefix
    
    For any Vecna message, the content should be prefixed with "[VECNA]" tag.
    """
    vecna_response = vecna.execute_emotional_trigger(user, message)
    assert vecna_response.content.startswith("[VECNA]")
```

## Implementation Notes

### Gemini 2.5 Flash Integration

The system will use the Gemini 2.5 Flash API for all AI content generation. Configuration:

```python
# backend/config.py additions
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL: str = "gemini-2.5-flash"
GEMINI_TEMPERATURE: float = 0.9  # Higher for creative/adversarial content
GEMINI_MAX_TOKENS: int = 500
```

### Vecna Tone Guidelines

The Vecna narrative should embody the character from Stranger Things:
- **Hostile but not offensive**: Menacing and unsettling, but never abusive or using profanity
- **Cryptic and observant**: References user behavior patterns in mysterious ways
- **Psychologically probing**: Comments on frustrations, repetitions, and unfinished tasks
- **Ominous tone**: Uses ellipses, dramatic pauses, and foreboding language

Example phrases:
- "I see you return to [room name]... again and again..."
- "Your frustration grows with each failed attempt..."
- "So many tasks begun, so few completed..."
- "You seek answers in places you've already searched..."

### Psychic Grip Timing

The Psychic Grip duration will be randomly selected between 5-8 seconds for each activation to create unpredictability:

```python
import random

def get_psychic_grip_duration() -> int:
    """Get random Psychic Grip duration between 5-8 seconds."""
    return random.randint(5, 8)
```

### Frontend Visual Effects

Visual effects will be implemented using CSS animations and JavaScript DOM manipulation:

```css
/* Vecna-specific CSS classes */
.vecna-message {
    color: #ff3333;
    text-shadow: 0 0 10px #ff3333, 0 0 20px #ff0000;
}

.vecna-psychic-grip {
    animation: screen-flicker 0.1s infinite;
}

.vecna-inverted {
    filter: invert(1);
}

.vecna-scanlines {
    background: repeating-linear-gradient(
        0deg,
        rgba(0, 0, 0, 0.15),
        rgba(0, 0, 0, 0.15) 1px,
        transparent 1px,
        transparent 2px
    );
    animation: scanline-move 8s linear infinite;
}

@keyframes screen-flicker {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

@keyframes scanline-move {
    0% { background-position: 0 0; }
    100% { background-position: 0 100%; }
}
```

### Message Type Extensions

New WebSocket message types for Vecna:

```javascript
// Emotional trigger message (Psychic Grip)
{
    type: 'vecna_psychic_grip',
    content: '[VECNA] Your frustration... I can taste it. You return to this broken code again and again, seeking answers that elude you...',
    duration: 6,
    effects: ['flicker', 'inverted', 'scanlines', 'static'],
    trigger_type: 'emotional',
    timestamp: '2025-12-01T12:00:00Z'
}

// Psychic Grip message
{
    type: 'vecna_psychic_grip',
    content: '[VECNA] I see you return to the Archives... again and again... searching for something you\'ll never find...',
    duration: 7,
    effects: ['flicker', 'inverted', 'scanlines', 'static'],
    timestamp: '2025-12-01T12:00:00Z'
}

// Grip release message
{
    type: 'vecna_release',
    content: '[SYSTEM] Control returned to SysOp. Continue your session.',
    timestamp: '2025-12-01T12:00:07Z'
}
```

## Performance Considerations

### Sentiment Analysis Optimization

- Cache sentiment analysis results for repeated messages
- Use lightweight keyword-based analysis before heavy NLP
- Implement rate limiting on sentiment analysis calls

### Profile Data Caching

- Cache user profiles in memory with TTL
- Update cache on profile modifications
- Implement lazy loading for profile data

### Gemini API Rate Limiting

- Implement request queuing for API calls
- Add exponential backoff for rate limit errors
- Cache AI responses for similar inputs
- Set reasonable timeout values (5 seconds)

### Database Query Optimization

- Index user_id columns for fast lookups
- Use batch inserts for command history
- Implement connection pooling
- Add query result caching

## Security Considerations

### API Key Protection

- Store Gemini API key in environment variables
- Never log API keys
- Rotate keys periodically
- Use separate keys for development/production

### User Profile Privacy

- Limit profile data retention (30 days)
- Implement data anonymization for logs
- Provide user opt-out mechanism
- Comply with data protection regulations

### Input Validation

- Sanitize all user inputs before processing
- Validate message lengths
- Prevent injection attacks in profile data
- Rate limit Vecna activations per user

### Vecna Abuse Prevention

- Limit Vecna activations per user (max 5 per hour)
- Implement cooldown period between activations
- Log all Vecna activations for monitoring
- Provide admin controls to disable Vecna

## Deployment Considerations

### Environment Variables

```bash
# .env file additions
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.9
GEMINI_MAX_TOKENS=500

# Vecna configuration
VECNA_ENABLED=true
VECNA_EMOTIONAL_THRESHOLD=0.7
VECNA_MAX_ACTIVATIONS_PER_HOUR=5
VECNA_COOLDOWN_SECONDS=60

# Profile tracking
PROFILE_RETENTION_DAYS=30
PROFILE_CACHE_TTL_SECONDS=300
```

### Database Migrations

Database migrations will be required to add new tables for user profiles, command history, board tracking, and Vecna activation logs.

### Monitoring and Logging

- Log all Vecna activations with trigger reasons
- Monitor Gemini API usage and costs
- Track Vecna activation rates per user
- Alert on unusual activation patterns
- Monitor API error rates

## Future Enhancements

### Potential Extensions

1. **Multiple Vecna Personalities**
   - Different adversarial styles based on context
   - Personality selection based on user behavior

2. **Vecna Learning**
   - Adapt responses based on user reactions
   - Learn effective trigger patterns
   - Personalize adversarial content

3. **Collaborative Vecna**
   - Multi-user Psychic Grip events
   - Room-wide adversarial interactions
   - Coordinated narrative generation

4. **Vecna Progression**
   - Escalating intensity over time
   - Achievement system for "surviving" Vecna
   - Unlockable Vecna modes

5. **Admin Controls**
   - Dashboard for Vecna configuration
   - Real-time activation monitoring
   - User-specific Vecna settings
   - Emergency disable switch
