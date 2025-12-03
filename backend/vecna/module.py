"""
Vecna Module - Adversarial AI component for conditional hostile interactions.

This module implements the text corruption algorithm and core Vecna functionality
for creating adversarial experiences in the BBS system.
"""

import random
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from backend.vecna.sentiment import SentimentAnalyzer
from backend.vecna.gemini_service import GeminiService
from backend.vecna.user_profile import UserProfile
from backend.vecna.rate_limiter import VecnaRateLimiter, VecnaRateLimitResult
from backend.vecna.monitoring import VecnaMonitor

logger = logging.getLogger(__name__)


def corrupt_text(text: str, corruption_level: float = 0.3) -> str:
    """
    Apply text corruption while maintaining partial readability.
    
    This function corrupts text by applying character substitutions, random deletions,
    and case randomization while ensuring at least 50% of characters remain readable.
    
    Algorithm:
    1. Identify corruption candidates (skip spaces, punctuation)
    2. Apply substitution map to random subset
    3. Randomly delete characters
    4. Randomize case
    5. Ensure readability threshold (50% minimum)
    
    Args:
        text: Original text to corrupt
        corruption_level: Percentage of characters to corrupt (0.0-1.0)
                         Clamped to maximum 0.5 to ensure 50% readability
    
    Returns:
        Corrupted text string with partial readability preserved
        
    Requirements:
        - 3.2: Apply text corruption including character substitution and garbling
        - 3.5: Maintain partial readability while creating visual distortion
    
    Examples:
        >>> corrupt_text("Hello World", 0.3)
        'H3ll0 W0rld'  # Example output (actual output is random)
        
        >>> corrupt_text("", 0.5)
        ''  # Empty string returns empty string
    """
    # Handle edge case: empty string
    if not text:
        return text
    
    # Clamp corruption level to maximum 0.5 to ensure 50% readability
    corruption_level = min(corruption_level, 0.5)
    
    # Character substitution map for creating corrupted text
    substitution_map = {
        'a': '@', 'A': '@',
        'e': '3', 'E': '3',
        'i': '1', 'I': '1',
        'o': '0', 'O': '0',
        's': '$', 'S': '$',
        't': '7', 'T': '7',
        'l': '1', 'L': '1',
    }
    
    # Convert text to list for easier manipulation
    chars = list(text)
    corrupted_chars = []
    
    # Track how many characters we've corrupted
    total_corruptible = 0
    corrupted_count = 0
    
    # First pass: identify corruptible characters (letters only)
    for char in chars:
        if char.isalpha():
            total_corruptible += 1
    
    # Calculate target corruption count
    target_corruptions = int(total_corruptible * corruption_level)
    
    # Second pass: apply corruption
    for i, char in enumerate(chars):
        # Preserve spaces and punctuation
        if not char.isalpha():
            corrupted_chars.append(char)
            continue
        
        # Decide whether to corrupt this character
        should_corrupt = False
        if corrupted_count < target_corruptions:
            # Randomly decide to corrupt, weighted by remaining budget
            remaining_chars = total_corruptible - i
            remaining_budget = target_corruptions - corrupted_count
            if remaining_chars > 0:
                probability = remaining_budget / remaining_chars
                should_corrupt = random.random() < probability
        
        if should_corrupt:
            # Apply substitution if available
            if char in substitution_map:
                corrupted_chars.append(substitution_map[char])
                corrupted_count += 1
            # Otherwise, randomly change case
            elif random.random() < 0.5:
                corrupted_chars.append(char.swapcase())
                corrupted_count += 1
            else:
                corrupted_chars.append(char)
        else:
            corrupted_chars.append(char)
    
    return ''.join(corrupted_chars)



class TriggerType(Enum):
    """Enumeration of Vecna trigger types."""
    EMOTIONAL = "emotional"
    SYSTEM = "system"
    NONE = "none"


@dataclass
class VecnaTrigger:
    """
    Represents a Vecna trigger event.
    
    Attributes:
        trigger_type: Type of trigger (emotional or system)
        reason: Description of why Vecna was triggered
        intensity: Intensity score of the trigger (0.0-1.0)
        user_id: User database ID
        timestamp: When the trigger occurred
    """
    trigger_type: TriggerType
    reason: str
    intensity: float
    user_id: int
    timestamp: datetime


@dataclass
class VecnaResponse:
    """
    Response from Vecna activation.
    
    Attributes:
        trigger_type: Type of trigger that caused this response
        content: Main response content
        corrupted_text: Corrupted version of text (for emotional triggers)
        freeze_duration: Duration in seconds for Psychic Grip (for system triggers)
        visual_effects: List of visual effects to apply
        timestamp: When the response was generated
    """
    trigger_type: TriggerType
    content: str
    corrupted_text: Optional[str] = None
    freeze_duration: Optional[int] = None
    visual_effects: list = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.visual_effects is None:
            self.visual_effects = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class VecnaModule:
    """
    Adversarial AI module for conditional hostile interactions.
    
    This class implements the core Vecna functionality including:
    - Trigger evaluation (emotional triggers only)
    - Psychic Grip execution (freeze + cryptic narrative generation)
    - Integration with SentimentAnalyzer and GeminiService
    
    Requirements: 2.1, 2.2, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.3, 4.4
    """
    
    def __init__(
        self,
        gemini_service: GeminiService,
        sentiment_analyzer: SentimentAnalyzer,
        rate_limiter: Optional[VecnaRateLimiter] = None,
        monitor: Optional[VecnaMonitor] = None,
        psychic_grip_duration_range: tuple = (5, 8)
    ):
        """
        Initialize the Vecna module.
        
        Args:
            gemini_service: Service for AI content generation
            sentiment_analyzer: Service for sentiment analysis
            rate_limiter: Optional rate limiter for abuse prevention
            monitor: Optional monitoring service for logging and metrics
            psychic_grip_duration_range: Tuple of (min, max) seconds for Psychic Grip
        """
        self.gemini = gemini_service
        self.sentiment = sentiment_analyzer
        self.rate_limiter = rate_limiter
        self.monitor = monitor
        self.psychic_grip_duration = psychic_grip_duration_range
        
        logger.info("VecnaModule initialized")
    
    async def evaluate_triggers(
        self,
        user_id: int,
        message: str,
        user_profile: UserProfile
    ) -> Optional[VecnaTrigger]:
        """
        Evaluate if Vecna should activate based on emotional triggers only.
        
        This method checks for high-negative sentiment in user messages.
        It also checks rate limits to prevent abuse.
        
        Args:
            user_id: User database ID
            message: User's message text
            user_profile: UserProfile object with behavioral data
        
        Returns:
            VecnaTrigger object if triggered, None otherwise
        
        Requirements: 2.1, 2.2
        """
        try:
            # Check rate limits first (if rate limiter is configured)
            if self.rate_limiter:
                rate_limit_result = self.rate_limiter.check_rate_limit(user_id)
                
                if not rate_limit_result.allowed:
                    logger.info(
                        f"Vecna activation blocked for user {user_id}: {rate_limit_result.reason}"
                    )
                    return None
            
            # Check emotional trigger (high-negative sentiment)
            sentiment_result = self.sentiment.analyze(message)
            
            if sentiment_result.is_trigger:
                logger.info(f"Vecna emotional trigger for user {user_id}: {sentiment_result.intensity}")
                return VecnaTrigger(
                    trigger_type=TriggerType.EMOTIONAL,
                    reason=f"High-negative sentiment detected: {', '.join(sentiment_result.keywords)}",
                    intensity=sentiment_result.intensity,
                    user_id=user_id,
                    timestamp=datetime.utcnow()
                )
            
            # No triggers detected
            return None
        
        except Exception as e:
            logger.error(f"Error evaluating Vecna triggers: {e}")
            return None
    
    async def execute_emotional_trigger(
        self,
        user_id: int,
        username: str,
        message: str,
        user_profile: UserProfile
    ) -> VecnaResponse:
        """
        Execute emotional trigger: Psychic Grip (freeze + cryptic narrative generation).
        
        This method:
        1. Determines a random freeze duration (5-8 seconds)
        2. Analyzes the user profile (interests, recent rooms, behavioral patterns)
        3. Generates a cryptic narrative using Gemini AI that references emotional state
        4. Returns a VecnaResponse with freeze duration and narrative content
        
        Args:
            user_id: User database ID
            username: Username for logging
            message: User's original message (for emotional context)
            user_profile: UserProfile object for personalization
        
        Returns:
            VecnaResponse with Psychic Grip freeze duration and cryptic narrative
        
        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.3, 4.4
        """
        start_time = datetime.utcnow()
        
        try:
            # Determine random freeze duration (5-8 seconds)
            freeze_duration = random.randint(
                self.psychic_grip_duration[0],
                self.psychic_grip_duration[1]
            )
            
            # Convert UserProfile to dict for Gemini service
            profile_dict = {
                'interests': user_profile.interests,
                'frequent_rooms': user_profile.frequent_rooms,
                'recent_rooms': user_profile.recent_rooms,
                'unfinished_boards': user_profile.unfinished_boards,
                'command_history': user_profile.command_history,
                'behavioral_patterns': user_profile.behavioral_patterns
            }
            
            # Generate Psychic Grip narrative using Gemini
            # This should reference the user's emotional state and profile data
            # Note: The emotional context is implicit from the trigger
            narrative = await self.gemini.generate_psychic_grip_narrative(
                user_profile=profile_dict,
                user_id=user_id
            )
            
            # Prefix with [VECNA] tag
            vecna_content = f"[VECNA] {narrative}"
            
            # Define visual effects for Psychic Grip
            visual_effects = ['flicker', 'inverted', 'scanlines', 'static']
            
            # Calculate duration
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(f"Vecna emotional trigger (Psychic Grip) executed for user {user_id}, duration: {freeze_duration}s")
            
            # Log activation to database (if rate limiter is configured)
            if self.rate_limiter:
                self.rate_limiter.record_activation(
                    user_id=user_id,
                    trigger_type="emotional",
                    reason=f"High-negative sentiment in message",
                    intensity=0.8,  # Default intensity for emotional triggers
                    response_content=vecna_content
                )
            
            # Log activation to monitoring (if monitor is configured)
            if self.monitor:
                self.monitor.log_activation(
                    user_id=user_id,
                    username=username,
                    trigger_type="emotional",
                    reason="High-negative sentiment in message",
                    intensity=0.8,
                    response_content=vecna_content,
                    duration_ms=duration_ms
                )
            
            return VecnaResponse(
                trigger_type=TriggerType.EMOTIONAL,
                content=vecna_content,
                freeze_duration=freeze_duration,
                visual_effects=visual_effects,
                timestamp=datetime.utcnow()
            )
        
        except Exception as e:
            logger.error(f"Error executing emotional trigger: {e}")
            
            # Calculate duration even for errors
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Log error to monitoring
            if self.monitor:
                self.monitor.log_activation(
                    user_id=user_id,
                    username=username,
                    trigger_type="emotional",
                    reason=f"Error: {str(e)}",
                    intensity=0.8,
                    response_content="[VECNA] ...c0nn3ct10n l0st... r3l3as1ng gr1p...",
                    duration_ms=duration_ms
                )
            
            # Fallback response with Psychic Grip
            freeze_duration = random.randint(5, 8)
            return VecnaResponse(
                trigger_type=TriggerType.EMOTIONAL,
                content="[VECNA] ...c0nn3ct10n l0st... r3l3as1ng gr1p...",
                freeze_duration=freeze_duration,
                visual_effects=['flicker', 'inverted', 'scanlines', 'static'],
                timestamp=datetime.utcnow()
            )
    
    async def execute_psychic_grip(
        self,
        user_id: int,
        username: str,
        user_profile: UserProfile
    ) -> VecnaResponse:
        """
        Execute Psychic Grip: freeze thread and generate cryptic narrative.
        
        This method:
        1. Determines a random freeze duration (5-8 seconds)
        2. Generates a cryptic narrative using Gemini AI
        3. Returns a VecnaResponse with freeze duration and effects
        
        Args:
            user_id: User database ID
            username: Username for logging
            user_profile: UserProfile object with behavioral history
        
        Returns:
            VecnaResponse with freeze duration and narrative content
        
        Requirements: 4.1, 4.3, 4.4
        """
        start_time = datetime.utcnow()
        
        try:
            # Determine random freeze duration
            freeze_duration = random.randint(
                self.psychic_grip_duration[0],
                self.psychic_grip_duration[1]
            )
            
            # Convert UserProfile to dict for Gemini service
            profile_dict = {
                'interests': user_profile.interests,
                'frequent_rooms': user_profile.frequent_rooms,
                'recent_rooms': user_profile.recent_rooms,
                'unfinished_boards': user_profile.unfinished_boards,
                'command_history': user_profile.command_history,
                'behavioral_patterns': user_profile.behavioral_patterns
            }
            
            # Generate Psychic Grip narrative using Gemini
            narrative = await self.gemini.generate_psychic_grip_narrative(
                user_profile=profile_dict,
                user_id=user_id
            )
            
            # Prefix with [VECNA] tag
            vecna_content = f"[VECNA] {narrative}"
            
            # Define visual effects for Psychic Grip
            visual_effects = ['flicker', 'inverted', 'scanlines', 'static']
            
            # Calculate duration
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            logger.info(f"Vecna Psychic Grip executed for user {user_id}, duration: {freeze_duration}s")
            
            # Log activation to database (if rate limiter is configured)
            if self.rate_limiter:
                self.rate_limiter.record_activation(
                    user_id=user_id,
                    trigger_type="system",
                    reason=f"System trigger (spam/repetition/anomaly)",
                    intensity=0.75,  # Default intensity for system triggers
                    response_content=vecna_content
                )
            
            # Log activation to monitoring (if monitor is configured)
            if self.monitor:
                self.monitor.log_activation(
                    user_id=user_id,
                    username=username,
                    trigger_type="system",
                    reason="System trigger (spam/repetition/anomaly)",
                    intensity=0.75,
                    response_content=vecna_content,
                    duration_ms=duration_ms
                )
            
            return VecnaResponse(
                trigger_type=TriggerType.SYSTEM,
                content=vecna_content,
                freeze_duration=freeze_duration,
                visual_effects=visual_effects,
                timestamp=datetime.utcnow()
            )
        
        except Exception as e:
            logger.error(f"Error executing Psychic Grip: {e}")
            
            # Calculate duration even for errors
            duration_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Log error to monitoring
            if self.monitor:
                self.monitor.log_activation(
                    user_id=user_id,
                    username=username,
                    trigger_type="system",
                    reason=f"Error: {str(e)}",
                    intensity=0.75,
                    response_content="[VECNA] ...1 s33 y0u w@nd3r...",
                    duration_ms=duration_ms
                )
            
            # Fallback response
            freeze_duration = random.randint(5, 8)
            return VecnaResponse(
                trigger_type=TriggerType.SYSTEM,
                content="[VECNA] ...1 s33 y0u w@nd3r... @1ml3ssly... l0st 1n th3 v01d...",
                freeze_duration=freeze_duration,
                visual_effects=['flicker', 'inverted', 'scanlines', 'static'],
                timestamp=datetime.utcnow()
            )
