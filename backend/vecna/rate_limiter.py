"""
Vecna Rate Limiter - Abuse prevention for Vecna activations.

This module implements rate limiting and cooldown mechanisms to prevent
abuse of the Vecna adversarial AI system.

Requirements: Security considerations
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.orm import Session

from backend.database import VecnaActivation
from backend.config import get_config

logger = logging.getLogger(__name__)


@dataclass
class VecnaRateLimitResult:
    """
    Result of Vecna rate limit check.
    
    Attributes:
        allowed: Whether Vecna activation is allowed
        reason: Reason for denial if not allowed
        activations_remaining: Number of activations remaining in current hour
        cooldown_remaining: Seconds remaining in cooldown period (if applicable)
    """
    allowed: bool
    reason: Optional[str] = None
    activations_remaining: Optional[int] = None
    cooldown_remaining: Optional[float] = None


class VecnaRateLimiter:
    """
    Rate limiter for Vecna activations to prevent abuse.
    
    This class implements:
    - Per-user activation limits (max N per hour)
    - Cooldown periods between activations (minimum seconds between triggers)
    - Global admin controls to disable Vecna
    - Activation logging to database
    
    Requirements: Security considerations
    """
    
    def __init__(
        self,
        db: Session,
        max_activations_per_hour: Optional[int] = None,
        cooldown_seconds: Optional[int] = None,
        enabled: Optional[bool] = None
    ):
        """
        Initialize the Vecna rate limiter.
        
        Args:
            db: Database session for logging activations
            max_activations_per_hour: Maximum activations per user per hour (default from config)
            cooldown_seconds: Minimum seconds between activations (default from config)
            enabled: Whether Vecna is globally enabled (default from config)
        """
        self.db = db
        
        # Load configuration
        config = get_config()
        self.max_activations_per_hour = max_activations_per_hour or config.VECNA_MAX_ACTIVATIONS_PER_HOUR
        self.cooldown_seconds = cooldown_seconds or config.VECNA_COOLDOWN_SECONDS
        self.enabled = enabled if enabled is not None else config.VECNA_ENABLED
        
        # In-memory tracking for cooldowns (faster than DB queries)
        # Key: user_id, Value: timestamp of last activation
        self._last_activation: Dict[int, datetime] = {}
        
        logger.info(
            f"VecnaRateLimiter initialized: "
            f"max_activations={self.max_activations_per_hour}/hour, "
            f"cooldown={self.cooldown_seconds}s, "
            f"enabled={self.enabled}"
        )
    
    def check_rate_limit(self, user_id: int) -> VecnaRateLimitResult:
        """
        Check if Vecna activation is allowed for a user.
        
        This method checks:
        1. Global Vecna enabled status
        2. Cooldown period since last activation
        3. Hourly activation limit
        
        Args:
            user_id: User database ID
        
        Returns:
            VecnaRateLimitResult with allowed status and details
        """
        # Check 1: Global enabled status
        if not self.enabled:
            return VecnaRateLimitResult(
                allowed=False,
                reason="Vecna is currently disabled by administrators",
                activations_remaining=0,
                cooldown_remaining=0
            )
        
        current_time = datetime.utcnow()
        
        # Check 2: Cooldown period
        if user_id in self._last_activation:
            last_activation = self._last_activation[user_id]
            elapsed = (current_time - last_activation).total_seconds()
            
            if elapsed < self.cooldown_seconds:
                cooldown_remaining = self.cooldown_seconds - elapsed
                return VecnaRateLimitResult(
                    allowed=False,
                    reason=f"Vecna cooldown active. Please wait {int(cooldown_remaining)} seconds.",
                    activations_remaining=None,
                    cooldown_remaining=cooldown_remaining
                )
        
        # Check 3: Hourly activation limit
        one_hour_ago = current_time - timedelta(hours=1)
        
        # Query recent activations from database
        recent_activations = self.db.query(VecnaActivation).filter(
            VecnaActivation.user_id == user_id,
            VecnaActivation.activated_at >= one_hour_ago
        ).count()
        
        if recent_activations >= self.max_activations_per_hour:
            return VecnaRateLimitResult(
                allowed=False,
                reason=f"Vecna activation limit reached ({self.max_activations_per_hour} per hour). Please try again later.",
                activations_remaining=0,
                cooldown_remaining=None
            )
        
        # All checks passed
        activations_remaining = self.max_activations_per_hour - recent_activations
        
        return VecnaRateLimitResult(
            allowed=True,
            reason=None,
            activations_remaining=activations_remaining,
            cooldown_remaining=None
        )
    
    def record_activation(
        self,
        user_id: int,
        trigger_type: str,
        reason: str,
        intensity: float,
        response_content: str
    ) -> None:
        """
        Record a Vecna activation in the database and update cooldown tracking.
        
        This method:
        1. Logs the activation to the vecna_activations table
        2. Updates in-memory cooldown tracking
        3. Commits the transaction
        
        Args:
            user_id: User database ID
            trigger_type: Type of trigger (emotional or system)
            reason: Description of why Vecna was triggered
            intensity: Intensity score of the trigger (0.0-1.0)
            response_content: Content of Vecna's response
        """
        try:
            # Create activation record
            activation = VecnaActivation(
                user_id=user_id,
                trigger_type=trigger_type,
                reason=reason,
                intensity=intensity,
                response_content=response_content,
                activated_at=datetime.utcnow()
            )
            
            # Add to database
            self.db.add(activation)
            self.db.commit()
            
            # Update in-memory cooldown tracking
            self._last_activation[user_id] = datetime.utcnow()
            
            logger.info(
                f"Vecna activation recorded: user_id={user_id}, "
                f"trigger_type={trigger_type}, intensity={intensity}"
            )
        
        except Exception as e:
            logger.error(f"Error recording Vecna activation: {e}")
            self.db.rollback()
    
    def get_user_activation_stats(self, user_id: int) -> Dict[str, any]:
        """
        Get activation statistics for a user.
        
        Args:
            user_id: User database ID
        
        Returns:
            Dictionary with activation statistics:
            - total_activations: Total activations all-time
            - activations_last_hour: Activations in the last hour
            - activations_remaining: Remaining activations this hour
            - last_activation: Timestamp of last activation (or None)
            - cooldown_remaining: Seconds remaining in cooldown (or 0)
        """
        current_time = datetime.utcnow()
        one_hour_ago = current_time - timedelta(hours=1)
        
        # Query total activations
        total_activations = self.db.query(VecnaActivation).filter(
            VecnaActivation.user_id == user_id
        ).count()
        
        # Query activations in last hour
        activations_last_hour = self.db.query(VecnaActivation).filter(
            VecnaActivation.user_id == user_id,
            VecnaActivation.activated_at >= one_hour_ago
        ).count()
        
        # Calculate remaining activations
        activations_remaining = max(0, self.max_activations_per_hour - activations_last_hour)
        
        # Get last activation time
        last_activation = self._last_activation.get(user_id)
        
        # Calculate cooldown remaining
        cooldown_remaining = 0
        if last_activation:
            elapsed = (current_time - last_activation).total_seconds()
            cooldown_remaining = max(0, self.cooldown_seconds - elapsed)
        
        return {
            "total_activations": total_activations,
            "activations_last_hour": activations_last_hour,
            "activations_remaining": activations_remaining,
            "last_activation": last_activation.isoformat() if last_activation else None,
            "cooldown_remaining": cooldown_remaining
        }
    
    def set_enabled(self, enabled: bool) -> None:
        """
        Set global Vecna enabled status (admin control).
        
        Args:
            enabled: Whether Vecna should be enabled
        """
        self.enabled = enabled
        logger.info(f"Vecna globally {'enabled' if enabled else 'disabled'} by admin")
    
    def is_enabled(self) -> bool:
        """
        Check if Vecna is globally enabled.
        
        Returns:
            True if Vecna is enabled, False otherwise
        """
        return self.enabled
    
    def reset_user_cooldown(self, user_id: int) -> None:
        """
        Reset cooldown for a specific user (admin function).
        
        Args:
            user_id: User database ID
        """
        if user_id in self._last_activation:
            del self._last_activation[user_id]
            logger.info(f"Cooldown reset for user_id={user_id}")
    
    def cleanup_old_activations(self, days: int = 30) -> int:
        """
        Clean up old activation records from the database.
        
        This should be called periodically to prevent database bloat.
        
        Args:
            days: Number of days to retain (default 30)
        
        Returns:
            Number of records deleted
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Delete old records
            deleted_count = self.db.query(VecnaActivation).filter(
                VecnaActivation.activated_at < cutoff_date
            ).delete()
            
            self.db.commit()
            
            logger.info(f"Cleaned up {deleted_count} old Vecna activation records")
            return deleted_count
        
        except Exception as e:
            logger.error(f"Error cleaning up old activations: {e}")
            self.db.rollback()
            return 0
