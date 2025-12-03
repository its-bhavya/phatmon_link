"""
Vecna Monitoring and Logging Module.

This module provides comprehensive monitoring, logging, and alerting for the
Vecna adversarial AI system, including:
- Structured logging for all Vecna activations
- Gemini API call tracking and error logging
- Metrics collection for activation rates per user
- Alert system for unusual activation patterns

Requirements: Deployment considerations (Task 19)
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import VecnaActivation, User

# Configure structured logging
logger = logging.getLogger(__name__)


@dataclass
class VecnaActivationLog:
    """
    Structured log entry for Vecna activation.
    
    Attributes:
        timestamp: When the activation occurred
        user_id: User database ID
        username: Username for readability
        trigger_type: Type of trigger (emotional or system)
        reason: Description of why Vecna was triggered
        intensity: Intensity score of the trigger (0.0-1.0)
        response_preview: First 100 chars of response
        duration_ms: Time taken to generate response (milliseconds)
    """
    timestamp: str
    user_id: int
    username: str
    trigger_type: str
    reason: str
    intensity: float
    response_preview: str
    duration_ms: Optional[float] = None
    
    def to_json(self) -> str:
        """Convert to JSON string for structured logging."""
        return json.dumps(asdict(self), indent=2)


@dataclass
class GeminiAPILog:
    """
    Structured log entry for Gemini API calls.
    
    Attributes:
        timestamp: When the API call was made
        operation: Type of operation (sysop_suggestion, hostile_response, psychic_grip)
        user_id: User database ID (if applicable)
        success: Whether the API call succeeded
        duration_ms: Time taken for API call (milliseconds)
        error_message: Error message if failed
        token_count: Approximate token count (if available)
    """
    timestamp: str
    operation: str
    user_id: Optional[int]
    success: bool
    duration_ms: float
    error_message: Optional[str] = None
    token_count: Optional[int] = None
    
    def to_json(self) -> str:
        """Convert to JSON string for structured logging."""
        return json.dumps(asdict(self), indent=2)


@dataclass
class VecnaMetrics:
    """
    Metrics for Vecna activations.
    
    Attributes:
        total_activations: Total activations in time period
        emotional_triggers: Count of emotional triggers
        system_triggers: Count of system triggers
        unique_users: Number of unique users triggered
        average_intensity: Average trigger intensity
        activations_per_hour: Activation rate per hour
        top_users: List of (user_id, username, count) tuples
    """
    total_activations: int
    emotional_triggers: int
    system_triggers: int
    unique_users: int
    average_intensity: float
    activations_per_hour: float
    top_users: List[tuple]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Alert:
    """
    Alert for unusual Vecna activation patterns.
    
    Attributes:
        timestamp: When the alert was triggered
        severity: Alert severity (info, warning, critical)
        alert_type: Type of alert (high_rate, user_spam, api_errors, etc.)
        message: Human-readable alert message
        details: Additional details as dictionary
    """
    timestamp: str
    severity: str
    alert_type: str
    message: str
    details: Dict[str, Any]
    
    def to_json(self) -> str:
        """Convert to JSON string for structured logging."""
        return json.dumps(asdict(self), indent=2)


class VecnaMonitor:
    """
    Monitoring and logging service for Vecna activations.
    
    This class provides:
    - Structured logging for all Vecna events
    - Metrics collection and aggregation
    - Alert generation for unusual patterns
    - API call tracking
    
    Requirements: Deployment considerations (Task 19)
    """
    
    def __init__(self, db: Session):
        """
        Initialize the Vecna monitor.
        
        Args:
            db: Database session for querying activation data
        """
        self.db = db
        
        # In-memory tracking for real-time metrics
        self._api_call_count = 0
        self._api_error_count = 0
        self._api_total_duration_ms = 0.0
        
        # Alert thresholds
        self.alert_thresholds = {
            'high_activation_rate': 10,  # activations per minute
            'user_spam_threshold': 5,     # activations per user per 5 minutes
            'api_error_rate': 0.3,        # 30% error rate
            'high_intensity_threshold': 0.9  # intensity above 0.9
        }
        
        logger.info("VecnaMonitor initialized")
    
    def log_activation(
        self,
        user_id: int,
        username: str,
        trigger_type: str,
        reason: str,
        intensity: float,
        response_content: str,
        duration_ms: Optional[float] = None
    ) -> None:
        """
        Log a Vecna activation with structured logging.
        
        Args:
            user_id: User database ID
            username: Username for readability
            trigger_type: Type of trigger (emotional or system)
            reason: Description of why Vecna was triggered
            intensity: Intensity score of the trigger (0.0-1.0)
            response_content: Full response content
            duration_ms: Time taken to generate response (milliseconds)
        """
        # Create structured log entry
        log_entry = VecnaActivationLog(
            timestamp=datetime.utcnow().isoformat(),
            user_id=user_id,
            username=username,
            trigger_type=trigger_type,
            reason=reason,
            intensity=intensity,
            response_preview=response_content[:100] + "..." if len(response_content) > 100 else response_content,
            duration_ms=duration_ms
        )
        
        # Log with structured format
        logger.info(
            f"VECNA_ACTIVATION: {log_entry.to_json()}",
            extra={
                'event_type': 'vecna_activation',
                'user_id': user_id,
                'trigger_type': trigger_type,
                'intensity': intensity
            }
        )
        
        # Check for high-intensity triggers (potential alert)
        if intensity >= self.alert_thresholds['high_intensity_threshold']:
            self._generate_alert(
                severity='warning',
                alert_type='high_intensity_trigger',
                message=f"High-intensity Vecna trigger detected for user {username}",
                details={
                    'user_id': user_id,
                    'username': username,
                    'intensity': intensity,
                    'reason': reason
                }
            )
    
    def log_gemini_api_call(
        self,
        operation: str,
        user_id: Optional[int],
        success: bool,
        duration_ms: float,
        error_message: Optional[str] = None,
        token_count: Optional[int] = None
    ) -> None:
        """
        Log a Gemini API call with structured logging.
        
        Args:
            operation: Type of operation (sysop_suggestion, hostile_response, psychic_grip)
            user_id: User database ID (if applicable)
            success: Whether the API call succeeded
            duration_ms: Time taken for API call (milliseconds)
            error_message: Error message if failed
            token_count: Approximate token count (if available)
        """
        # Update in-memory metrics
        self._api_call_count += 1
        self._api_total_duration_ms += duration_ms
        if not success:
            self._api_error_count += 1
        
        # Create structured log entry
        log_entry = GeminiAPILog(
            timestamp=datetime.utcnow().isoformat(),
            operation=operation,
            user_id=user_id,
            success=success,
            duration_ms=duration_ms,
            error_message=error_message,
            token_count=token_count
        )
        
        # Log with appropriate level
        if success:
            logger.info(
                f"GEMINI_API_CALL: {log_entry.to_json()}",
                extra={
                    'event_type': 'gemini_api_call',
                    'operation': operation,
                    'success': True
                }
            )
        else:
            logger.error(
                f"GEMINI_API_ERROR: {log_entry.to_json()}",
                extra={
                    'event_type': 'gemini_api_error',
                    'operation': operation,
                    'error': error_message
                }
            )
        
        # Check API error rate
        if self._api_call_count >= 10:  # Only check after 10 calls
            error_rate = self._api_error_count / self._api_call_count
            if error_rate >= self.alert_thresholds['api_error_rate']:
                self._generate_alert(
                    severity='critical',
                    alert_type='high_api_error_rate',
                    message=f"High Gemini API error rate detected: {error_rate:.1%}",
                    details={
                        'error_rate': error_rate,
                        'total_calls': self._api_call_count,
                        'failed_calls': self._api_error_count
                    }
                )
    
    def get_metrics(
        self,
        time_window_hours: int = 24,
        top_users_limit: int = 10
    ) -> VecnaMetrics:
        """
        Get aggregated metrics for Vecna activations.
        
        Args:
            time_window_hours: Time window for metrics (default 24 hours)
            top_users_limit: Number of top users to include (default 10)
        
        Returns:
            VecnaMetrics object with aggregated statistics
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        
        # Query activations in time window
        activations = self.db.query(VecnaActivation).filter(
            VecnaActivation.activated_at >= cutoff_time
        ).all()
        
        if not activations:
            return VecnaMetrics(
                total_activations=0,
                emotional_triggers=0,
                system_triggers=0,
                unique_users=0,
                average_intensity=0.0,
                activations_per_hour=0.0,
                top_users=[]
            )
        
        # Calculate metrics
        total_activations = len(activations)
        emotional_triggers = sum(1 for a in activations if a.trigger_type == 'emotional')
        system_triggers = sum(1 for a in activations if a.trigger_type == 'system')
        unique_users = len(set(a.user_id for a in activations))
        
        # Calculate average intensity (filter out None values)
        intensities = [a.intensity for a in activations if a.intensity is not None]
        average_intensity = sum(intensities) / len(intensities) if intensities else 0.0
        
        # Calculate activations per hour
        activations_per_hour = total_activations / time_window_hours
        
        # Get top users
        user_counts = defaultdict(int)
        for activation in activations:
            user_counts[activation.user_id] += 1
        
        # Sort by count and get top users with usernames
        top_user_ids = sorted(user_counts.items(), key=lambda x: x[1], reverse=True)[:top_users_limit]
        
        top_users = []
        for user_id, count in top_user_ids:
            user = self.db.query(User).filter(User.id == user_id).first()
            username = user.username if user else f"user_{user_id}"
            top_users.append((user_id, username, count))
        
        metrics = VecnaMetrics(
            total_activations=total_activations,
            emotional_triggers=emotional_triggers,
            system_triggers=system_triggers,
            unique_users=unique_users,
            average_intensity=average_intensity,
            activations_per_hour=activations_per_hour,
            top_users=top_users
        )
        
        # Log metrics
        logger.info(
            f"VECNA_METRICS: {json.dumps(metrics.to_dict(), indent=2)}",
            extra={
                'event_type': 'vecna_metrics',
                'time_window_hours': time_window_hours
            }
        )
        
        return metrics
    
    def check_unusual_patterns(self, time_window_minutes: int = 5) -> List[Alert]:
        """
        Check for unusual activation patterns and generate alerts.
        
        This method checks for:
        - High activation rate (too many activations in short time)
        - User spam (single user triggering too frequently)
        - Unusual trigger distribution
        
        Args:
            time_window_minutes: Time window for pattern detection (default 5 minutes)
        
        Returns:
            List of Alert objects for detected unusual patterns
        """
        alerts = []
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        
        # Query recent activations
        recent_activations = self.db.query(VecnaActivation).filter(
            VecnaActivation.activated_at >= cutoff_time
        ).all()
        
        if not recent_activations:
            return alerts
        
        # Check 1: High activation rate
        activation_rate_per_minute = len(recent_activations) / time_window_minutes
        if activation_rate_per_minute >= self.alert_thresholds['high_activation_rate']:
            alert = Alert(
                timestamp=datetime.utcnow().isoformat(),
                severity='warning',
                alert_type='high_activation_rate',
                message=f"High Vecna activation rate detected: {activation_rate_per_minute:.1f} per minute",
                details={
                    'activation_count': len(recent_activations),
                    'time_window_minutes': time_window_minutes,
                    'rate_per_minute': activation_rate_per_minute
                }
            )
            alerts.append(alert)
            self._log_alert(alert)
        
        # Check 2: User spam (single user triggering too frequently)
        user_counts = defaultdict(int)
        for activation in recent_activations:
            user_counts[activation.user_id] += 1
        
        for user_id, count in user_counts.items():
            if count >= self.alert_thresholds['user_spam_threshold']:
                user = self.db.query(User).filter(User.id == user_id).first()
                username = user.username if user else f"user_{user_id}"
                
                alert = Alert(
                    timestamp=datetime.utcnow().isoformat(),
                    severity='warning',
                    alert_type='user_spam',
                    message=f"User {username} triggered Vecna {count} times in {time_window_minutes} minutes",
                    details={
                        'user_id': user_id,
                        'username': username,
                        'activation_count': count,
                        'time_window_minutes': time_window_minutes
                    }
                )
                alerts.append(alert)
                self._log_alert(alert)
        
        # Check 3: Unusual trigger distribution (all emotional or all system)
        emotional_count = sum(1 for a in recent_activations if a.trigger_type == 'emotional')
        system_count = sum(1 for a in recent_activations if a.trigger_type == 'system')
        
        if len(recent_activations) >= 10:  # Only check if we have enough data
            if emotional_count == 0 or system_count == 0:
                alert = Alert(
                    timestamp=datetime.utcnow().isoformat(),
                    severity='info',
                    alert_type='unusual_trigger_distribution',
                    message=f"Unusual trigger distribution: {emotional_count} emotional, {system_count} system",
                    details={
                        'emotional_triggers': emotional_count,
                        'system_triggers': system_count,
                        'total_activations': len(recent_activations)
                    }
                )
                alerts.append(alert)
                self._log_alert(alert)
        
        return alerts
    
    def get_user_activation_history(
        self,
        user_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get activation history for a specific user.
        
        Args:
            user_id: User database ID
            limit: Maximum number of records to return (default 50)
        
        Returns:
            List of activation records as dictionaries
        """
        activations = self.db.query(VecnaActivation).filter(
            VecnaActivation.user_id == user_id
        ).order_by(
            VecnaActivation.activated_at.desc()
        ).limit(limit).all()
        
        history = []
        for activation in activations:
            history.append({
                'id': activation.id,
                'trigger_type': activation.trigger_type,
                'reason': activation.reason,
                'intensity': activation.intensity,
                'response_preview': activation.response_content[:100] + "..." if activation.response_content and len(activation.response_content) > 100 else activation.response_content,
                'activated_at': activation.activated_at.isoformat()
            })
        
        return history
    
    def get_api_metrics(self) -> Dict[str, Any]:
        """
        Get Gemini API call metrics.
        
        Returns:
            Dictionary with API metrics:
            - total_calls: Total API calls made
            - failed_calls: Number of failed calls
            - error_rate: Percentage of failed calls
            - average_duration_ms: Average API call duration
        """
        error_rate = (self._api_error_count / self._api_call_count) if self._api_call_count > 0 else 0.0
        average_duration = (self._api_total_duration_ms / self._api_call_count) if self._api_call_count > 0 else 0.0
        
        return {
            'total_calls': self._api_call_count,
            'failed_calls': self._api_error_count,
            'error_rate': error_rate,
            'average_duration_ms': average_duration
        }
    
    def reset_api_metrics(self) -> None:
        """Reset in-memory API metrics (useful for testing or periodic resets)."""
        self._api_call_count = 0
        self._api_error_count = 0
        self._api_total_duration_ms = 0.0
        logger.info("API metrics reset")
    
    def _generate_alert(
        self,
        severity: str,
        alert_type: str,
        message: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Generate and log an alert.
        
        Args:
            severity: Alert severity (info, warning, critical)
            alert_type: Type of alert
            message: Human-readable alert message
            details: Additional details as dictionary
        """
        alert = Alert(
            timestamp=datetime.utcnow().isoformat(),
            severity=severity,
            alert_type=alert_type,
            message=message,
            details=details
        )
        self._log_alert(alert)
    
    def _log_alert(self, alert: Alert) -> None:
        """
        Log an alert with appropriate severity level.
        
        Args:
            alert: Alert object to log
        """
        log_message = f"VECNA_ALERT: {alert.to_json()}"
        
        if alert.severity == 'critical':
            logger.critical(
                log_message,
                extra={
                    'event_type': 'vecna_alert',
                    'severity': 'critical',
                    'alert_type': alert.alert_type
                }
            )
        elif alert.severity == 'warning':
            logger.warning(
                log_message,
                extra={
                    'event_type': 'vecna_alert',
                    'severity': 'warning',
                    'alert_type': alert.alert_type
                }
            )
        else:
            logger.info(
                log_message,
                extra={
                    'event_type': 'vecna_alert',
                    'severity': 'info',
                    'alert_type': alert.alert_type
                }
            )
