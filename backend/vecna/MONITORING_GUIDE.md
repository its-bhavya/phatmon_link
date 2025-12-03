# Vecna Monitoring and Logging Guide

This guide explains how to use the Vecna monitoring and logging system to track activations, API calls, and detect unusual patterns.

## Overview

The Vecna monitoring system provides:

1. **Structured Logging** - All Vecna activations and Gemini API calls are logged with detailed context
2. **Metrics Collection** - Aggregated statistics on activation rates, trigger types, and user behavior
3. **Alert System** - Automatic detection of unusual patterns like high activation rates or user spam
4. **API Tracking** - Monitoring of Gemini API calls including success rates and performance

## Setup

### 1. Initialize the Monitor

```python
from sqlalchemy.orm import Session
from backend.vecna.monitoring import VecnaMonitor

# Create monitor instance with database session
monitor = VecnaMonitor(db=session)
```

### 2. Integrate with Vecna Module

```python
from backend.vecna.module import VecnaModule
from backend.vecna.gemini_service import GeminiService
from backend.vecna.sentiment import SentimentAnalyzer
from backend.vecna.pattern_detector import PatternDetector
from backend.vecna.rate_limiter import VecnaRateLimiter
from backend.vecna.monitoring import VecnaMonitor

# Initialize services
gemini_service = GeminiService(api_key="your_key", monitor=monitor)
sentiment_analyzer = SentimentAnalyzer()
pattern_detector = PatternDetector()
rate_limiter = VecnaRateLimiter(db=session)

# Initialize Vecna with monitoring
vecna = VecnaModule(
    gemini_service=gemini_service,
    sentiment_analyzer=sentiment_analyzer,
    pattern_detector=pattern_detector,
    rate_limiter=rate_limiter,
    monitor=monitor
)
```

## Features

### Structured Logging

All Vecna activations are logged with structured data:

```python
# Logs are automatically created when Vecna activates
# Example log output:
{
  "timestamp": "2025-12-03T10:30:45.123456",
  "user_id": 42,
  "username": "alice",
  "trigger_type": "emotional",
  "reason": "High-negative sentiment in message",
  "intensity": 0.85,
  "response_preview": "[VECNA] wHy c@n't y0u f1gur3 th1s 0ut?...",
  "duration_ms": 234.5
}
```

### Gemini API Call Tracking

All API calls to Gemini are tracked:

```python
# Successful API call log:
{
  "timestamp": "2025-12-03T10:30:45.123456",
  "operation": "hostile_response",
  "user_id": 42,
  "success": true,
  "duration_ms": 234.5,
  "token_count": 45
}

# Failed API call log:
{
  "timestamp": "2025-12-03T10:30:45.123456",
  "operation": "psychic_grip",
  "user_id": 42,
  "success": false,
  "duration_ms": 5000.0,
  "error_message": "API timeout"
}
```

### Metrics Collection

Get aggregated metrics for any time window:

```python
# Get metrics for last 24 hours
metrics = monitor.get_metrics(time_window_hours=24)

print(f"Total activations: {metrics.total_activations}")
print(f"Emotional triggers: {metrics.emotional_triggers}")
print(f"System triggers: {metrics.system_triggers}")
print(f"Unique users: {metrics.unique_users}")
print(f"Average intensity: {metrics.average_intensity:.2f}")
print(f"Activations per hour: {metrics.activations_per_hour:.2f}")

# Top users
for user_id, username, count in metrics.top_users:
    print(f"  {username}: {count} activations")
```

### API Metrics

Track Gemini API performance:

```python
api_metrics = monitor.get_api_metrics()

print(f"Total API calls: {api_metrics['total_calls']}")
print(f"Failed calls: {api_metrics['failed_calls']}")
print(f"Error rate: {api_metrics['error_rate']:.1%}")
print(f"Average duration: {api_metrics['average_duration_ms']:.1f}ms")
```

### Alert System

Automatically detect unusual patterns:

```python
# Check for unusual patterns in last 5 minutes
alerts = monitor.check_unusual_patterns(time_window_minutes=5)

for alert in alerts:
    print(f"[{alert.severity.upper()}] {alert.alert_type}")
    print(f"  {alert.message}")
    print(f"  Details: {alert.details}")
```

**Alert Types:**

1. **high_activation_rate** - More than 10 activations per minute
2. **user_spam** - Single user triggering 5+ times in 5 minutes
3. **unusual_trigger_distribution** - All emotional or all system triggers
4. **high_intensity_trigger** - Individual trigger with intensity > 0.9
5. **high_api_error_rate** - API error rate exceeds 30%

### User Activation History

Get detailed history for a specific user:

```python
history = monitor.get_user_activation_history(user_id=42, limit=50)

for record in history:
    print(f"{record['activated_at']}: {record['trigger_type']}")
    print(f"  Reason: {record['reason']}")
    print(f"  Intensity: {record['intensity']}")
    print(f"  Response: {record['response_preview']}")
```

## Configuration

### Alert Thresholds

Customize alert thresholds when initializing the monitor:

```python
monitor = VecnaMonitor(db=session)

# Modify thresholds
monitor.alert_thresholds = {
    'high_activation_rate': 15,      # activations per minute
    'user_spam_threshold': 8,         # activations per user per 5 minutes
    'api_error_rate': 0.4,            # 40% error rate
    'high_intensity_threshold': 0.95  # intensity above 0.95
}
```

## Log Formats

### Activation Logs

Activation logs are written to the standard Python logger with the prefix `VECNA_ACTIVATION:`:

```
INFO:backend.vecna.monitoring:VECNA_ACTIVATION: {
  "timestamp": "2025-12-03T10:30:45.123456",
  "user_id": 42,
  "username": "alice",
  "trigger_type": "emotional",
  "reason": "High-negative sentiment in message",
  "intensity": 0.85,
  "response_preview": "[VECNA] wHy c@n't y0u f1gur3 th1s 0ut?...",
  "duration_ms": 234.5
}
```

### API Call Logs

API call logs use the prefix `GEMINI_API_CALL:` for success and `GEMINI_API_ERROR:` for failures:

```
INFO:backend.vecna.monitoring:GEMINI_API_CALL: {
  "timestamp": "2025-12-03T10:30:45.123456",
  "operation": "hostile_response",
  "user_id": 42,
  "success": true,
  "duration_ms": 234.5,
  "token_count": 45
}
```

### Alert Logs

Alerts are logged with severity-appropriate levels (INFO, WARNING, CRITICAL):

```
WARNING:backend.vecna.monitoring:VECNA_ALERT: {
  "timestamp": "2025-12-03T10:30:45.123456",
  "severity": "warning",
  "alert_type": "high_activation_rate",
  "message": "High Vecna activation rate detected: 12.5 per minute",
  "details": {
    "activation_count": 62,
    "time_window_minutes": 5,
    "rate_per_minute": 12.4
  }
}
```

## Best Practices

### 1. Regular Metrics Review

Set up periodic metrics collection to track trends:

```python
import schedule
import time

def collect_metrics():
    metrics = monitor.get_metrics(time_window_hours=1)
    # Store or log metrics
    print(f"Hourly metrics: {metrics.to_dict()}")

# Run every hour
schedule.every().hour.do(collect_metrics)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### 2. Alert Monitoring

Check for unusual patterns regularly:

```python
def check_alerts():
    alerts = monitor.check_unusual_patterns(time_window_minutes=5)
    
    for alert in alerts:
        if alert.severity == 'critical':
            # Send notification to admins
            send_admin_notification(alert)
        
        # Log all alerts
        print(f"Alert: {alert.message}")

# Run every 5 minutes
schedule.every(5).minutes.do(check_alerts)
```

### 3. API Performance Monitoring

Track API performance to detect issues:

```python
def monitor_api_performance():
    metrics = monitor.get_api_metrics()
    
    if metrics['error_rate'] > 0.2:
        print(f"WARNING: High API error rate: {metrics['error_rate']:.1%}")
    
    if metrics['average_duration_ms'] > 1000:
        print(f"WARNING: Slow API responses: {metrics['average_duration_ms']:.0f}ms")

# Run every 10 minutes
schedule.every(10).minutes.do(monitor_api_performance)
```

### 4. Database Cleanup

Periodically clean up old activation records:

```python
from backend.vecna.rate_limiter import VecnaRateLimiter

rate_limiter = VecnaRateLimiter(db=session)

# Clean up records older than 30 days
deleted_count = rate_limiter.cleanup_old_activations(days=30)
print(f"Cleaned up {deleted_count} old activation records")
```

## Integration with Logging Systems

### File Logging

Configure Python logging to write to files:

```python
import logging

# Configure file handler
file_handler = logging.FileHandler('vecna_monitoring.log')
file_handler.setLevel(logging.INFO)

# Add formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
file_handler.setFormatter(formatter)

# Add handler to logger
logger = logging.getLogger('backend.vecna.monitoring')
logger.addHandler(file_handler)
```

### Structured Logging with JSON

Use a JSON formatter for structured logs:

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage()
        }
        return json.dumps(log_data)

json_handler = logging.FileHandler('vecna_monitoring.json')
json_handler.setFormatter(JSONFormatter())

logger = logging.getLogger('backend.vecna.monitoring')
logger.addHandler(json_handler)
```

### Integration with External Services

Send alerts to external monitoring services:

```python
import requests

def send_to_monitoring_service(alert):
    """Send alert to external monitoring service."""
    payload = {
        'service': 'vecna',
        'severity': alert.severity,
        'alert_type': alert.alert_type,
        'message': alert.message,
        'details': alert.details,
        'timestamp': alert.timestamp
    }
    
    try:
        response = requests.post(
            'https://monitoring-service.example.com/alerts',
            json=payload,
            timeout=5
        )
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to send alert to monitoring service: {e}")

# Use in alert checking
alerts = monitor.check_unusual_patterns(time_window_minutes=5)
for alert in alerts:
    if alert.severity in ['warning', 'critical']:
        send_to_monitoring_service(alert)
```

## Troubleshooting

### High Memory Usage

If monitoring uses too much memory, reset API metrics periodically:

```python
# Reset API metrics every hour
schedule.every().hour.do(monitor.reset_api_metrics)
```

### Missing Logs

Ensure the monitor is properly initialized and passed to services:

```python
# Verify monitor is set
assert vecna.monitor is not None
assert gemini_service.monitor is not None
```

### Database Performance

Add indexes to improve query performance (already included in schema):

```sql
CREATE INDEX idx_vecna_activations_user ON vecna_activations(user_id);
CREATE INDEX idx_vecna_activations_time ON vecna_activations(activated_at);
```

## Example: Complete Monitoring Setup

```python
from sqlalchemy.orm import Session
from backend.vecna.monitoring import VecnaMonitor
from backend.vecna.module import VecnaModule
from backend.vecna.gemini_service import GeminiService
from backend.vecna.sentiment import SentimentAnalyzer
from backend.vecna.pattern_detector import PatternDetector
from backend.vecna.rate_limiter import VecnaRateLimiter
from backend.config import get_config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vecna.log'),
        logging.StreamHandler()
    ]
)

# Initialize services
config = get_config()
db_session = Session()

monitor = VecnaMonitor(db=db_session)
gemini_service = GeminiService(
    api_key=config.GEMINI_API_KEY,
    model=config.GEMINI_MODEL,
    temperature=config.GEMINI_TEMPERATURE,
    max_tokens=config.GEMINI_MAX_TOKENS,
    monitor=monitor
)
sentiment_analyzer = SentimentAnalyzer()
pattern_detector = PatternDetector()
rate_limiter = VecnaRateLimiter(db=db_session)

vecna = VecnaModule(
    gemini_service=gemini_service,
    sentiment_analyzer=sentiment_analyzer,
    pattern_detector=pattern_detector,
    rate_limiter=rate_limiter,
    monitor=monitor
)

# Set up periodic monitoring
import schedule

def hourly_metrics():
    metrics = monitor.get_metrics(time_window_hours=1)
    print(f"Hourly Vecna Metrics:")
    print(f"  Total activations: {metrics.total_activations}")
    print(f"  Emotional: {metrics.emotional_triggers}, System: {metrics.system_triggers}")
    print(f"  Unique users: {metrics.unique_users}")
    print(f"  Avg intensity: {metrics.average_intensity:.2f}")

def check_patterns():
    alerts = monitor.check_unusual_patterns(time_window_minutes=5)
    for alert in alerts:
        print(f"[{alert.severity.upper()}] {alert.message}")

schedule.every().hour.do(hourly_metrics)
schedule.every(5).minutes.do(check_patterns)

# Run monitoring loop
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Summary

The Vecna monitoring system provides comprehensive observability into:

- **Activation patterns** - When and why Vecna triggers
- **API performance** - Gemini API success rates and latency
- **User behavior** - Which users trigger Vecna most frequently
- **System health** - Unusual patterns and potential issues

Use this system to ensure Vecna operates correctly and to detect any abuse or performance problems early.
