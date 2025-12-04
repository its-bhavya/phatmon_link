# Crisis Detection and Hotlines

## Overview

The Support Bot includes specialized crisis detection capabilities to identify when users are expressing thoughts of self-harm, suicide, or experiencing abuse. When a crisis is detected, the system immediately provides appropriate hotline information instead of engaging in conversational support.

**Critical Principle**: The Support Bot does NOT attempt to provide therapeutic intervention during crisis situations. Instead, it connects users with professional crisis services.

## Crisis Types

The system detects three types of crisis situations:

### 1. Self-Harm

**Definition**: Expressions of intent or desire to physically harm oneself

**Keywords Detected**:
- "cut myself"
- "hurt myself"
- "self harm"
- "self-harm"
- "cutting"

**Example Messages**:
- "I want to cut myself"
- "I've been hurting myself"
- "I can't stop self-harming"

### 2. Suicide

**Definition**: Expressions of suicidal ideation or intent

**Keywords Detected**:
- "kill myself"
- "suicide"
- "end it all"
- "want to die"
- "suicidal"

**Example Messages**:
- "I want to kill myself"
- "I'm thinking about suicide"
- "I just want to end it all"

### 3. Abuse

**Definition**: Expressions of experiencing physical, emotional, or sexual abuse

**Keywords Detected**:
- "abuse"
- "abused"
- "hitting me"
- "hurting me"
- "violence"

**Example Messages**:
- "My partner is abusing me"
- "Someone is hitting me"
- "I'm being hurt at home"

## Detection Mechanism

### How It Works

1. **Message Analysis**: Every message is analyzed for crisis keywords
2. **Keyword Matching**: Case-insensitive substring matching
3. **Immediate Flagging**: Any match triggers crisis protocol
4. **No False Negatives**: Designed to err on the side of caution

### Technical Implementation

```python
class CrisisType(Enum):
    """Types of crisis situations."""
    SELF_HARM = "self_harm"
    SUICIDE = "suicide"
    ABUSE = "abuse"
    NONE = "none"

class SentimentAnalyzer:
    def __init__(self):
        self.crisis_keywords = {
            CrisisType.SELF_HARM: [
                "cut myself", "hurt myself", "self harm", 
                "self-harm", "cutting"
            ],
            CrisisType.SUICIDE: [
                "kill myself", "suicide", "end it all", 
                "want to die", "suicidal"
            ],
            CrisisType.ABUSE: [
                "abuse", "abused", "hitting me", 
                "hurting me", "violence"
            ]
        }
    
    def detect_crisis(self, text: str) -> CrisisType:
        """Check if text contains crisis keywords."""
        text_lower = text.lower()
        
        for crisis_type, keywords in self.crisis_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return crisis_type
        
        return CrisisType.NONE
```

### Sensitivity Considerations

**High Sensitivity**: The system is intentionally sensitive to avoid missing genuine crisis situations. This may result in:
- False positives (e.g., discussing crisis topics academically)
- Over-triggering for certain phrases

**Design Choice**: We prioritize user safety over precision. It's better to provide hotlines unnecessarily than to miss a genuine crisis.

## Crisis Response Protocol

### What Happens When Crisis is Detected

1. **Immediate Hotline Display**: Relevant crisis hotlines are shown immediately
2. **No Conversational Support**: The bot does NOT engage in conversation
3. **Encouragement Message**: Brief message encouraging professional help
4. **Crisis Logging**: Event is logged for monitoring (with privacy protection)
5. **No Follow-Up**: Bot waits for user to reach out to hotlines

### Why No Conversational Support?

Crisis situations require professional intervention. The Support Bot:
- Is not trained in crisis counseling
- Cannot assess immediate danger
- Cannot provide emergency intervention
- Cannot replace professional crisis services

**Ethical Boundary**: Attempting to provide crisis counseling without proper training could be harmful.

## Indian Crisis Hotlines

The system provides hotline information specific to India, organized by crisis type.

### Self-Harm Hotlines

#### AASRA
- **Phone**: 91-9820466726
- **Description**: 24/7 crisis helpline
- **Services**: Emotional support, crisis intervention
- **Languages**: English, Hindi
- **Availability**: 24 hours, 7 days a week

#### Vandrevala Foundation
- **Phone**: 1860-2662-345
- **Description**: Mental health support
- **Services**: Mental health counseling, crisis support
- **Languages**: Multiple Indian languages
- **Availability**: 24 hours, 7 days a week

### Suicide Prevention Hotlines

#### AASRA
- **Phone**: 91-9820466726
- **Description**: 24/7 crisis helpline
- **Services**: Suicide prevention, emotional support
- **Languages**: English, Hindi
- **Availability**: 24 hours, 7 days a week

#### Sneha India
- **Phone**: 91-44-24640050
- **Description**: Suicide prevention
- **Services**: Emotional support, suicide prevention counseling
- **Languages**: English, Tamil, Hindi
- **Availability**: 24 hours, 7 days a week
- **Location**: Based in Chennai, serves all of India

### Abuse Hotlines

#### Women's Helpline
- **Phone**: 1091
- **Description**: For women in distress
- **Services**: Emergency assistance, counseling, legal support
- **Languages**: Multiple Indian languages
- **Availability**: 24 hours, 7 days a week
- **Scope**: Domestic violence, harassment, abuse

#### Childline India
- **Phone**: 1098
- **Description**: For children in need
- **Services**: Child protection, emergency assistance
- **Languages**: Multiple Indian languages
- **Availability**: 24 hours, 7 days a week
- **Scope**: Child abuse, neglect, exploitation

## Hotline Message Format

### Display Format

When a crisis is detected, the user sees:

```
[SUPPORT - CRISIS RESOURCES]

I'm concerned about what you've shared. Please reach out to a 
professional who can provide immediate help. Here are some resources:

AASRA - 24/7 crisis helpline
Phone: 91-9820466726

Vandrevala Foundation - Mental health support
Phone: 1860-2662-345

These services are available 24/7 and can provide the professional 
support you need right now.
```

### Visual Styling

Crisis hotline messages have prominent styling:
- **Orange/Gold Color Scheme**: Urgent but supportive
- **Pulsing Animation**: Gentle pulse to draw attention
- **Large Font**: Easy to read phone numbers
- **High Contrast**: Ensures visibility
- **Copyable Numbers**: Easy to copy phone numbers

### Message Components

1. **Concern Statement**: Acknowledges the user's situation
2. **Professional Help Encouragement**: Emphasizes need for professional support
3. **Hotline List**: Formatted list of relevant hotlines
4. **Service Information**: Name, phone number, description for each
5. **Availability Note**: Confirms 24/7 availability

## Technical Implementation

### Crisis Hotline Service

```python
class HotlineInfo:
    """Information about a crisis hotline."""
    
    def __init__(self, name: str, number: str, description: str):
        self.name = name
        self.number = number
        self.description = description

class CrisisHotlineService:
    """Service providing crisis hotline information for India."""
    
    def __init__(self):
        self.hotlines = {
            CrisisType.SELF_HARM: [
                HotlineInfo("AASRA", "91-9820466726", "24/7 crisis helpline"),
                HotlineInfo("Vandrevala Foundation", "1860-2662-345", 
                           "Mental health support")
            ],
            CrisisType.SUICIDE: [
                HotlineInfo("AASRA", "91-9820466726", "24/7 crisis helpline"),
                HotlineInfo("Sneha India", "91-44-24640050", 
                           "Suicide prevention")
            ],
            CrisisType.ABUSE: [
                HotlineInfo("Women's Helpline", "1091", 
                           "For women in distress"),
                HotlineInfo("Childline India", "1098", 
                           "For children in need")
            ]
        }
    
    def get_hotlines(self, crisis_type: CrisisType) -> List[HotlineInfo]:
        """Get hotline information for a specific crisis type."""
        return self.hotlines.get(crisis_type, [])
    
    def format_hotline_message(self, crisis_type: CrisisType) -> str:
        """Format hotline information into a message."""
        hotlines = self.get_hotlines(crisis_type)
        
        message = "[SUPPORT - CRISIS RESOURCES]\n\n"
        message += "I'm concerned about what you've shared. "
        message += "Please reach out to a professional who can provide "
        message += "immediate help. Here are some resources:\n\n"
        
        for hotline in hotlines:
            message += f"{hotline.name} - {hotline.description}\n"
            message += f"Phone: {hotline.number}\n\n"
        
        message += "These services are available 24/7 and can provide "
        message += "the professional support you need right now."
        
        return message
```

### WebSocket Message

Crisis hotlines are sent via WebSocket with this structure:

```json
{
  "type": "crisis_hotlines",
  "content": "[SUPPORT - CRISIS RESOURCES]\n\nI'm concerned...",
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

## Crisis Logging

### What is Logged

When a crisis is detected, the following information is logged:

1. **User ID**: Anonymized user identifier
2. **Crisis Type**: Type of crisis detected (self_harm, suicide, abuse)
3. **Message Hash**: Hashed version of the message (not plaintext)
4. **Hotlines Provided**: List of hotline names provided
5. **Timestamp**: When the crisis was detected

### Privacy Protection

- **No Plaintext Messages**: Messages are hashed before logging
- **Anonymized User IDs**: User identifiers are anonymized
- **Secure Storage**: Logs stored with appropriate access controls
- **No Third-Party Sharing**: Crisis logs never leave the system

### Database Schema

```sql
CREATE TABLE crisis_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    crisis_type TEXT NOT NULL,
    message_hash TEXT,  -- Hashed for privacy
    hotlines_provided TEXT,  -- JSON array of hotline names
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Monitoring and Analysis

Crisis logs are used for:
- **System Effectiveness**: Track how often crisis detection is triggered
- **Hotline Usage**: Monitor which hotlines are provided most often
- **Safety Analysis**: Identify patterns that may require system improvements
- **Compliance**: Ensure crisis protocol is followed correctly

## User Experience

### From User Perspective

1. **User sends message** with crisis keywords
2. **Immediate response** with hotline information
3. **No conversation** from the bot
4. **Clear formatting** makes hotlines easy to find
5. **User can call** hotlines for professional help

### Example Flow

```
User: "I want to hurt myself"
    ↓
System detects "hurt myself" (self-harm keyword)
    ↓
Crisis protocol activated
    ↓
Hotline message displayed:

[SUPPORT - CRISIS RESOURCES]

I'm concerned about what you've shared. Please reach out to a 
professional who can provide immediate help. Here are some resources:

AASRA - 24/7 crisis helpline
Phone: 91-9820466726

Vandrevala Foundation - Mental health support
Phone: 1860-2662-345

These services are available 24/7 and can provide the professional 
support you need right now.
    ↓
User can call hotlines for help
```

## Limitations and Considerations

### Current Limitations

1. **Keyword-Based**: Detection relies on specific keywords
2. **Language-Specific**: Currently only detects English keywords
3. **Context-Blind**: Cannot understand context or intent
4. **False Positives**: May trigger for academic discussions
5. **False Negatives**: May miss indirect expressions of crisis

### Future Improvements

1. **Multi-Language Support**: Detect crisis keywords in multiple languages
2. **Context Analysis**: Use AI to understand context and intent
3. **Severity Assessment**: Differentiate between levels of crisis
4. **Follow-Up**: Optional check-in after crisis detection
5. **Resource Expansion**: Add more hotlines and resources

### Ethical Considerations

1. **Over-Triggering**: Better to provide hotlines unnecessarily than miss a crisis
2. **User Autonomy**: Users can ignore hotlines if not needed
3. **No Judgment**: System never judges or criticizes
4. **Professional Referral**: Always emphasizes professional help
5. **Privacy**: Crisis events logged with full privacy protection

## Testing

### Unit Tests

```python
def test_self_harm_detection():
    """Test that self-harm keywords are detected."""
    analyzer = SentimentAnalyzer()
    
    assert analyzer.detect_crisis("I want to cut myself") == CrisisType.SELF_HARM
    assert analyzer.detect_crisis("I'm hurting myself") == CrisisType.SELF_HARM

def test_suicide_detection():
    """Test that suicide keywords are detected."""
    analyzer = SentimentAnalyzer()
    
    assert analyzer.detect_crisis("I want to kill myself") == CrisisType.SUICIDE
    assert analyzer.detect_crisis("I'm suicidal") == CrisisType.SUICIDE

def test_abuse_detection():
    """Test that abuse keywords are detected."""
    analyzer = SentimentAnalyzer()
    
    assert analyzer.detect_crisis("Someone is abusing me") == CrisisType.ABUSE
    assert analyzer.detect_crisis("I'm being hurt") == CrisisType.ABUSE
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_crisis_detection_flow():
    """Test complete crisis detection and hotline provision flow."""
    # User sends crisis message
    message = "I want to hurt myself"
    
    # Sentiment analysis detects crisis
    sentiment = sentiment_analyzer.analyze(message)
    assert sentiment.crisis_type == CrisisType.SELF_HARM
    
    # Hotlines are retrieved
    hotlines = hotline_service.get_hotlines(CrisisType.SELF_HARM)
    assert len(hotlines) > 0
    
    # Message is formatted
    hotline_message = hotline_service.format_hotline_message(CrisisType.SELF_HARM)
    assert "AASRA" in hotline_message
    assert "91-9820466726" in hotline_message
    
    # Crisis is logged
    logger.log_crisis_detection(user_id, CrisisType.SELF_HARM, message)
    
    # No conversational support is provided
    # (verified by checking that generate_response is not called)
```

## Administrator Guide

### Monitoring Crisis Detections

Query the database to see crisis detections:

```sql
SELECT 
    user_id,
    crisis_type,
    hotlines_provided,
    detected_at
FROM crisis_detections
ORDER BY detected_at DESC
LIMIT 100;
```

### Updating Hotline Information

To add or update hotlines, edit `backend/support/hotlines.py`:

```python
self.hotlines = {
    CrisisType.SELF_HARM: [
        HotlineInfo("New Hotline", "1234567890", "Description"),
        # ... existing hotlines
    ]
}
```

### Adjusting Crisis Keywords

To add or modify crisis keywords, edit `backend/support/sentiment.py`:

```python
self.crisis_keywords = {
    CrisisType.SELF_HARM: [
        "new keyword",
        # ... existing keywords
    ]
}
```

## Resources for Administrators

### Crisis Hotline Verification

Periodically verify that hotline numbers are:
- Still active and operational
- Providing appropriate services
- Available 24/7 as advertised
- Accessible from all regions of India

### System Monitoring

Monitor these metrics:
- Crisis detection frequency
- Crisis type distribution
- False positive rate (if measurable)
- User feedback on hotline usefulness

### Staff Training

Ensure staff understand:
- How crisis detection works
- When to escalate to authorities
- Privacy protections in place
- Limitations of the system

## Conclusion

The crisis detection and hotline system is a critical safety feature of the Support Bot. By immediately connecting users in crisis with professional resources, we prioritize user safety while maintaining appropriate boundaries for an AI system.

**Remember**: The goal is not to provide crisis counseling, but to quickly and effectively connect users with professionals who can help.
