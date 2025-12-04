# Privacy and Security

## Overview

The Support Bot is designed with privacy and security as core principles. This document details the privacy protections, security measures, and data handling practices implemented to protect user information and maintain trust.

## Privacy Principles

### 1. Data Minimization

**Principle**: Collect only the data necessary for support functionality.

**Implementation**:
- We do NOT store full message content in logs
- We do NOT collect personal health information
- We do NOT track user behavior outside support interactions
- We do NOT share data with third parties

**What We Collect**:
- Sentiment analysis results (emotion type, intensity)
- Support activation events (timestamp, trigger)
- Crisis detection events (type, hotlines provided)
- Anonymized interaction logs

**What We DON'T Collect**:
- Full message transcripts
- Personal identifying information
- Medical history or diagnoses
- Location data
- Device information

### 2. Content Anonymization

**Principle**: Protect message content through hashing and anonymization.

**Implementation**:

```python
def _anonymize_content(self, content: str) -> str:
    """
    Anonymize sensitive content for logging.
    
    Uses SHA-256 hashing to create a one-way hash of the content.
    The original content cannot be recovered from the hash.
    """
    import hashlib
    return hashlib.sha256(content.encode()).hexdigest()
```

**How It Works**:
1. User sends message: "I'm feeling really down today"
2. System processes message for support
3. For logging, message is hashed: `a3f5b8c9d2e1...` (64-character hash)
4. Only the hash is stored in the database
5. Original message is never stored

**Benefits**:
- Original content cannot be recovered
- Hashes can still be used for duplicate detection
- Privacy is protected even if database is compromised

### 3. User Autonomy

**Principle**: Users control their support experience.

**Implementation**:
- Users can leave support rooms at any time
- Users can return to support rooms when ready
- Users are never forced to continue conversations
- Users can ignore crisis hotlines if not applicable

**Commands**:
```
/leave          # Leave support room and return to previous room
/join <room>    # Return to support room if desired
```

### 4. Transparency

**Principle**: Users know what data is collected and how it's used.

**Implementation**:
- Clear documentation of data collection practices
- Explicit boundaries stated in support room greeting
- No hidden data collection or tracking
- Open source code for verification

## Security Measures

### 1. Database Security

**Access Controls**:
- Database access restricted to backend services only
- No direct database access from frontend
- User authentication required for all operations
- Role-based access control for administrators

**Encryption**:
- Database connections use secure protocols
- Sensitive fields are hashed before storage
- No plaintext storage of message content

**Schema Design**:
```sql
-- Support activations table
CREATE TABLE support_activations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    emotion_type TEXT NOT NULL,
    intensity FLOAT NOT NULL,
    trigger_message_hash TEXT,  -- Hashed, not plaintext
    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Crisis detections table
CREATE TABLE crisis_detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    crisis_type TEXT NOT NULL,
    message_hash TEXT,  -- Hashed, not plaintext
    hotlines_provided TEXT,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Support interactions table
CREATE TABLE support_interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_message_hash TEXT,  -- Hashed, not plaintext
    bot_response_hash TEXT,  -- Hashed, not plaintext
    interaction_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 2. WebSocket Security

**Authentication**:
- JWT token required for WebSocket connection
- Token validation on every message
- Automatic disconnection on invalid token

**Message Validation**:
- All messages validated before processing
- Input sanitization to prevent injection attacks
- Rate limiting to prevent abuse

**Connection Security**:
- Secure WebSocket (WSS) in production
- TLS/SSL encryption for all data in transit
- Session management with automatic timeout

### 3. API Security

**Gemini API**:
- API keys stored in environment variables (not in code)
- Secure credential loading from `.env` file
- API calls made over HTTPS
- No user data sent to Gemini beyond conversation context

**Rate Limiting**:
- Gemini API calls rate-limited per user
- Prevents abuse and excessive costs
- Graceful fallback when rate limit exceeded

### 4. Input Validation

**Message Validation**:
- Maximum message length enforced
- Special character handling
- SQL injection prevention (parameterized queries)
- XSS prevention (HTML escaping)

**Command Validation**:
- Whitelist of allowed commands
- Parameter validation
- Permission checks

## Data Handling Practices

### 1. Support Activation Logging

**What is Logged**:
```python
{
    "user_id": 123,
    "emotion_type": "sadness",
    "intensity": 0.75,
    "trigger_message_hash": "a3f5b8c9d2e1...",  # Hashed
    "activated_at": "2024-12-04T18:30:00Z"
}
```

**Privacy Protection**:
- User ID is internal (not personally identifying)
- Trigger message is hashed (not plaintext)
- Emotion type and intensity are aggregate data
- Timestamp is necessary for monitoring

**Purpose**:
- Monitor system effectiveness
- Identify patterns in support activation
- Improve sentiment analysis accuracy
- Ensure support is being provided when needed

### 2. Crisis Detection Logging

**What is Logged**:
```python
{
    "user_id": 123,
    "crisis_type": "self_harm",
    "message_hash": "b4e6c7d8f3a2...",  # Hashed
    "hotlines_provided": ["AASRA", "Vandrevala Foundation"],
    "detected_at": "2024-12-04T18:32:00Z"
}
```

**Privacy Protection**:
- Message is hashed (not plaintext)
- Crisis type is categorical (not specific details)
- Hotlines provided are public information
- No personal health information stored

**Purpose**:
- Monitor crisis detection frequency
- Ensure appropriate hotlines are provided
- Identify system improvements needed
- Comply with safety protocols

### 3. Bot Interaction Logging

**What is Logged**:
```python
{
    "user_id": 123,
    "user_message_hash": "c5f7d8e9a4b3...",  # Hashed
    "bot_response_hash": "d6g8e9f0b5c4...",  # Hashed
    "interaction_at": "2024-12-04T18:33:00Z"
}
```

**Privacy Protection**:
- Both user message and bot response are hashed
- No conversation content stored in plaintext
- Only metadata (timestamp, user ID) is readable

**Purpose**:
- Monitor bot response quality
- Identify conversation patterns
- Improve bot responses over time
- Ensure bot is following guidelines

### 4. User Profile Data

**What is Stored**:
```python
{
    "user_id": 123,
    "interests": ["programming", "music", "gaming"],
    "frequent_rooms": {"Tech": 10, "Lobby": 5},
    "recent_rooms": ["Lobby", "Tech", "Support-123"]
}
```

**Privacy Protection**:
- Interests derived from public chat messages
- Room activity is internal system data
- No personal identifying information
- Data used only for personalization

**Purpose**:
- Personalize support bot responses
- Provide relevant context to bot
- Improve user experience
- Enable context-aware support

**Read-Only Access**:
- Support Bot has read-only access to user profiles
- User profiles are never modified by Support Bot
- Ensures data integrity and privacy

## Privacy by Design

### 1. Default Privacy Settings

**All users have**:
- Private support rooms (not visible to others)
- Hashed message logging (not plaintext)
- Anonymized user identifiers
- No third-party data sharing

**No opt-in required**:
- Privacy protections are automatic
- Users don't need to configure anything
- Maximum privacy by default

### 2. Data Retention

**Support Activation Logs**:
- Retained indefinitely for system monitoring
- Contain only hashed content and metadata
- Can be purged on user account deletion

**Crisis Detection Logs**:
- Retained indefinitely for safety analysis
- Contain only hashed content and crisis type
- Critical for system safety improvements

**Support Interaction Logs**:
- Retained indefinitely for quality monitoring
- Contain only hashed content
- Used for bot improvement

**User Profiles**:
- Retained while account is active
- Deleted when account is deleted
- Can be reset on user request

### 3. Data Access

**Who Can Access Data**:
- System administrators (for monitoring and debugging)
- Automated systems (for support functionality)
- No third parties
- No external services (except Gemini API for response generation)

**What Can Be Accessed**:
- Aggregate statistics (emotion types, crisis frequency)
- Hashed message content (not readable)
- Metadata (timestamps, user IDs)
- System logs (for debugging)

**What CANNOT Be Accessed**:
- Original message content (hashed before storage)
- Personal identifying information (not collected)
- Conversation transcripts (not stored)
- User location or device data (not collected)

## Compliance and Best Practices

### 1. Ethical AI Guidelines

**Transparency**:
- Users know they're interacting with an AI
- Bot limitations are clearly stated
- No deception about bot capabilities

**Fairness**:
- All users receive same level of support
- No discrimination based on user characteristics
- Equal access to crisis resources

**Accountability**:
- System behavior is logged and monitored
- Administrators can review system actions
- Clear escalation path for issues

### 2. Mental Health Best Practices

**Appropriate Boundaries**:
- Bot never claims to be a therapist
- No mental health diagnoses provided
- Crisis situations escalated to professionals

**User Safety**:
- Crisis detection prioritizes user safety
- Immediate hotline provision for emergencies
- No harmful advice or suggestions

**Professional Referral**:
- Always encourages professional help when appropriate
- Provides accurate hotline information
- Emphasizes limitations of AI support

### 3. Data Protection

**Encryption**:
- Data in transit: TLS/SSL encryption
- Data at rest: Database encryption (if configured)
- API communications: HTTPS only

**Access Control**:
- Role-based access control
- Principle of least privilege
- Audit logging of administrative access

**Incident Response**:
- Procedures for data breach response
- User notification protocols
- System recovery procedures

## User Rights

### 1. Right to Access

Users can request:
- Information about what data is stored
- Access to their support activation logs
- Explanation of how their data is used

**How to Request**:
- Contact system administrators
- Provide user ID for verification
- Receive anonymized log data

### 2. Right to Deletion

Users can request:
- Deletion of their user account
- Removal of support interaction logs
- Purging of all associated data

**How to Request**:
- Contact system administrators
- Verify account ownership
- Data will be deleted within 30 days

**Note**: Some data may be retained for legal or safety reasons (e.g., crisis detection logs).

### 3. Right to Opt-Out

Users can:
- Leave support rooms at any time
- Ignore crisis hotlines if not applicable
- Choose not to engage with Support Bot

**How to Opt-Out**:
- Use `/leave` command to exit support room
- Return to normal chat rooms
- Support Bot will not re-engage unless new negative sentiment detected

## Security Incident Response

### 1. Data Breach Response

**If a data breach occurs**:
1. Immediate containment of breach
2. Assessment of data exposed
3. Notification to affected users
4. Remediation of vulnerability
5. Post-incident review and improvements

**User Notification**:
- Users notified within 72 hours
- Clear explanation of what data was exposed
- Steps users can take to protect themselves
- Contact information for questions

### 2. System Compromise

**If system is compromised**:
1. Immediate shutdown of affected services
2. Forensic analysis of compromise
3. Restoration from secure backups
4. Security audit before restoration
5. User notification if data was accessed

### 3. Reporting Security Issues

**How to Report**:
- Email: security@phantomlink.example (replace with actual email)
- Include detailed description of issue
- Provide steps to reproduce if applicable
- Responsible disclosure appreciated

**Response Timeline**:
- Acknowledgment within 24 hours
- Initial assessment within 72 hours
- Resolution timeline provided
- Credit given for responsible disclosure

## Testing and Verification

### 1. Privacy Testing

**Tests Performed**:
- Verify message content is hashed before storage
- Confirm no plaintext messages in database
- Validate user profile read-only access
- Check that logs contain only anonymized data

**Test Example**:
```python
def test_message_content_is_hashed():
    """Test that message content is hashed before logging."""
    logger = SupportInteractionLogger(db)
    
    original_message = "I'm feeling really down"
    logger.log_support_activation(user_id=123, sentiment=sentiment, 
                                   trigger_message=original_message)
    
    # Query database
    activation = db.query(SupportActivation).first()
    
    # Verify original message is not in database
    assert original_message not in activation.trigger_message_hash
    # Verify hash is present
    assert len(activation.trigger_message_hash) == 64  # SHA-256 hash length
```

### 2. Security Testing

**Tests Performed**:
- SQL injection prevention
- XSS attack prevention
- Authentication bypass attempts
- Rate limiting effectiveness
- Input validation

### 3. Access Control Testing

**Tests Performed**:
- Verify users can only access their own support rooms
- Confirm administrators have appropriate access
- Test that Support Bot has read-only access to user profiles
- Validate JWT token expiration and refresh

## Monitoring and Auditing

### 1. System Monitoring

**Metrics Tracked**:
- Support activation frequency
- Crisis detection frequency
- Bot response times
- Error rates
- API usage

**Alerts Configured**:
- Unusual spike in crisis detections
- High error rates
- API failures
- Database connection issues

### 2. Audit Logging

**Events Logged**:
- Administrative access to logs
- Configuration changes
- Database queries (for sensitive data)
- System errors and exceptions

**Log Retention**:
- Audit logs retained for 1 year
- Stored securely with access controls
- Reviewed regularly for anomalies

### 3. Privacy Audits

**Regular Reviews**:
- Quarterly review of data collection practices
- Annual privacy impact assessment
- Regular security audits
- Compliance checks

## Conclusion

Privacy and security are fundamental to the Support Bot's design. Through content anonymization, minimal data collection, secure storage, and transparent practices, we protect user privacy while providing effective emotional support.

**Key Takeaways**:
- Message content is hashed, never stored in plaintext
- Minimal data collection (only what's necessary)
- User autonomy is respected (can leave anytime)
- No third-party data sharing
- Transparent about data practices
- Regular security audits and monitoring

**For Users**: Your privacy is protected. Your conversations are hashed, your data is minimized, and your autonomy is respected.

**For Administrators**: Follow best practices, monitor regularly, respond quickly to incidents, and always prioritize user privacy.

**For Developers**: Maintain privacy by design, test thoroughly, document clearly, and never compromise on security.
