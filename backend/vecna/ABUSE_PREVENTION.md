# Vecna Abuse Prevention

This document describes the abuse prevention mechanisms implemented for the Vecna adversarial AI system.

## Overview

The Vecna system includes comprehensive abuse prevention to ensure that the adversarial AI features cannot be exploited or cause negative user experiences. The system implements multiple layers of protection:

1. **Rate Limiting** - Limits the number of Vecna activations per user per hour
2. **Cooldown Periods** - Enforces minimum time between activations
3. **Activation Logging** - Records all activations for monitoring and analysis
4. **Admin Controls** - Allows administrators to disable Vecna globally

## Rate Limiting

### Per-User Hourly Limit

Each user is limited to a maximum number of Vecna activations per hour (default: 5). This prevents:
- Spam triggering of Vecna through repeated negative messages
- System abuse through intentional trigger manipulation
- Degraded user experience from excessive adversarial interactions

Configuration:
```bash
VECNA_MAX_ACTIVATIONS_PER_HOUR=5
```

When the limit is reached, users receive a message:
```
Vecna activation limit reached (5 per hour). Please try again later.
```

### Cooldown Period

A cooldown period (default: 60 seconds) is enforced between consecutive Vecna activations for each user. This prevents:
- Rapid-fire triggering of Vecna
- Overwhelming users with back-to-back adversarial interactions
- System resource exhaustion from frequent AI API calls

Configuration:
```bash
VECNA_COOLDOWN_SECONDS=60
```

When in cooldown, users receive a message:
```
Vecna cooldown active. Please wait X seconds.
```

## Activation Logging

All Vecna activations are logged to the `vecna_activations` database table with the following information:

- **user_id**: User who triggered Vecna
- **trigger_type**: Type of trigger (emotional or system)
- **reason**: Description of why Vecna was triggered
- **intensity**: Intensity score of the trigger (0.0-1.0)
- **response_content**: Content of Vecna's response
- **activated_at**: Timestamp of activation

This logging enables:
- Monitoring of Vecna activation patterns
- Detection of abuse attempts
- Analysis of trigger effectiveness
- Debugging and troubleshooting

### Database Schema

```sql
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

CREATE INDEX idx_vecna_activations_user ON vecna_activations(user_id);
```

## Admin Controls

### Global Enable/Disable

Administrators can enable or disable Vecna globally through the API:

**Get Status:**
```bash
GET /api/admin/vecna/status
```

Response:
```json
{
  "enabled": true,
  "max_activations_per_hour": 5,
  "cooldown_seconds": 60,
  "emotional_threshold": 0.7
}
```

**Control Vecna:**
```bash
POST /api/admin/vecna/control
Content-Type: application/json

{
  "enabled": false
}
```

Response:
```json
{
  "success": true,
  "enabled": false,
  "message": "Vecna has been disabled globally"
}
```

When Vecna is disabled globally, all activation attempts are blocked with the message:
```
Vecna is currently disabled by administrators
```

### Configuration

Global enable/disable can also be controlled via environment variable:
```bash
VECNA_ENABLED=false
```

## User Statistics

The system provides detailed statistics for each user's Vecna activations:

```python
stats = rate_limiter.get_user_activation_stats(user_id)
```

Returns:
```python
{
    "total_activations": 15,           # All-time activations
    "activations_last_hour": 3,        # Activations in last hour
    "activations_remaining": 2,        # Remaining this hour
    "last_activation": "2025-12-03T...", # Last activation timestamp
    "cooldown_remaining": 45.2         # Seconds remaining in cooldown
}
```

## Maintenance

### Cleanup Old Activations

To prevent database bloat, old activation records should be cleaned up periodically:

```python
# Delete activations older than 30 days
deleted_count = rate_limiter.cleanup_old_activations(days=30)
```

This can be run as a scheduled task (e.g., daily cron job).

Configuration:
```bash
PROFILE_RETENTION_DAYS=30
```

### Reset User Cooldown

Administrators can manually reset a user's cooldown if needed:

```python
rate_limiter.reset_user_cooldown(user_id)
```

This is useful for:
- Testing and debugging
- Resolving user support issues
- Handling false positives

## Implementation Details

### VecnaRateLimiter Class

The `VecnaRateLimiter` class (`backend/vecna/rate_limiter.py`) implements all abuse prevention logic:

```python
from backend.vecna.rate_limiter import VecnaRateLimiter

# Initialize with database session
rate_limiter = VecnaRateLimiter(
    db=db_session,
    max_activations_per_hour=5,
    cooldown_seconds=60,
    enabled=True
)

# Check if activation is allowed
result = rate_limiter.check_rate_limit(user_id)
if result.allowed:
    # Proceed with Vecna activation
    pass
else:
    # Block activation, show reason to user
    print(result.reason)

# Record activation
rate_limiter.record_activation(
    user_id=user_id,
    trigger_type="emotional",
    reason="High-negative sentiment",
    intensity=0.8,
    response_content="[VECNA] ..."
)
```

### Integration with VecnaModule

The rate limiter is integrated into the `VecnaModule` class:

```python
# Attach rate limiter to Vecna module
vecna_module.rate_limiter = rate_limiter

# Evaluate triggers (rate limits checked automatically)
trigger = await vecna_module.evaluate_triggers(
    user_id=user_id,
    message=message,
    user_profile=user_profile
)

# If trigger is None, rate limit was exceeded
```

### WebSocket Integration

In the WebSocket endpoint (`backend/main.py`), the rate limiter is created per-connection:

```python
# Initialize rate limiter for this connection
vecna_rate_limiter = VecnaRateLimiter(
    db=db,
    **app.state.vecna_rate_limiter_config
)

# Attach to vecna module before evaluation
vecna_module.rate_limiter = vecna_rate_limiter
```

## Monitoring and Alerts

### Recommended Monitoring

1. **Activation Rate**: Monitor activations per hour across all users
2. **Rate Limit Hits**: Track how often users hit rate limits
3. **Cooldown Violations**: Monitor cooldown violation attempts
4. **API Errors**: Track Gemini API errors during activations
5. **Unusual Patterns**: Detect coordinated abuse attempts

### Example Queries

**Activations in last hour:**
```sql
SELECT COUNT(*) 
FROM vecna_activations 
WHERE activated_at >= datetime('now', '-1 hour');
```

**Top users by activations:**
```sql
SELECT user_id, COUNT(*) as activation_count
FROM vecna_activations
WHERE activated_at >= datetime('now', '-24 hours')
GROUP BY user_id
ORDER BY activation_count DESC
LIMIT 10;
```

**Trigger type distribution:**
```sql
SELECT trigger_type, COUNT(*) as count
FROM vecna_activations
WHERE activated_at >= datetime('now', '-7 days')
GROUP BY trigger_type;
```

## Security Considerations

### API Key Protection

- Gemini API key is stored in environment variables
- Never logged or exposed in responses
- Separate keys for development/production recommended

### Database Security

- Activation logs contain user IDs (not usernames) for privacy
- Response content is stored for debugging but should be sanitized
- Consider encryption for sensitive activation data

### Rate Limit Bypass Prevention

- Rate limits are enforced server-side (cannot be bypassed by client)
- Cooldown tracking uses server timestamps (not client-provided)
- Database queries use indexed columns for performance

## Testing

Comprehensive tests are provided in `backend/tests/test_vecna_rate_limiter.py`:

```bash
# Run rate limiter tests
python -m pytest backend/tests/test_vecna_rate_limiter.py -v
```

Tests cover:
- Rate limit enforcement
- Cooldown period enforcement
- Hourly limit enforcement
- Global enable/disable
- Activation logging
- Multi-user tracking
- Statistics calculation
- Cleanup operations

## Future Enhancements

Potential improvements to abuse prevention:

1. **Dynamic Rate Limits**: Adjust limits based on user behavior patterns
2. **IP-Based Limiting**: Additional rate limiting by IP address
3. **Reputation System**: Track user behavior and adjust limits accordingly
4. **Automated Bans**: Automatically ban users who repeatedly abuse the system
5. **Alert System**: Real-time alerts for suspicious activation patterns
6. **Dashboard**: Admin dashboard for monitoring and control
7. **A/B Testing**: Test different rate limit configurations
8. **Machine Learning**: Detect abuse patterns using ML models
