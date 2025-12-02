"""
User Profile Service for Vecna Adversarial AI Module.

This module provides user behavioral tracking and analysis for Vecna triggers.
It tracks room visits, command patterns, board creation, and calculates
behavioral deviations from baseline activity.

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from sqlalchemy.orm import Session
from backend.database import User, UserProfile as UserProfileModel, CommandHistory, BoardTracking


@dataclass
class UserProfile:
    """
    User behavioral profile for Vecna analysis.
    
    This class represents a user's behavioral patterns including interests,
    room visits, command history, and activity baselines. It provides methods
    for pattern detection and deviation calculation.
    
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
    interests: List[str] = field(default_factory=list)
    frequent_rooms: Dict[str, int] = field(default_factory=dict)
    recent_rooms: List[str] = field(default_factory=list)
    command_history: List[Tuple[str, datetime]] = field(default_factory=list)
    unfinished_boards: List[str] = field(default_factory=list)
    activity_baseline: Dict[str, float] = field(default_factory=dict)
    behavioral_patterns: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_deviation(self, current_activity: Dict[str, Any]) -> float:
        """
        Calculate deviation from baseline activity.
        
        This method compares current activity metrics against the user's
        baseline to detect unusual behavior patterns.
        
        Args:
            current_activity: Dict containing current activity metrics
                Expected keys: 'messages_per_minute', 'commands_per_minute',
                'room_switches_per_hour'
        
        Returns:
            Deviation score (0.0 = normal, 1.0+ = significant deviation)
        """
        if not self.activity_baseline:
            # No baseline yet, return 0 (no deviation)
            return 0.0
        
        total_deviation = 0.0
        metric_count = 0
        
        for metric, current_value in current_activity.items():
            if metric in self.activity_baseline:
                baseline_value = self.activity_baseline[metric]
                if baseline_value > 0:
                    # Calculate relative deviation
                    deviation = abs(current_value - baseline_value) / baseline_value
                    total_deviation += deviation
                    metric_count += 1
        
        if metric_count == 0:
            return 0.0
        
        # Return average deviation across all metrics
        return total_deviation / metric_count
    
    def detect_spam_pattern(self, recent_messages: List[str], timestamps: Optional[List[datetime]] = None) -> bool:
        """
        Detect spam patterns in recent messages using multiple heuristics.
        
        Spam is detected when:
        - High message frequency in short time window
        - Multiple messages with high fuzzy similarity
        - Messages with similar length (template spam)
        - Low entropy (few unique normalized forms)
        
        Args:
            recent_messages: List of recent message texts
            timestamps: Optional list of message timestamps for frequency analysis
        
        Returns:
            True if spam pattern detected, False otherwise
        """
        if len(recent_messages) < 3:
            return False
        
        # Normalize messages for comparison
        def normalize(text: str) -> str:
            """Normalize text by lowercasing, removing extra whitespace and punctuation."""
            text = text.lower()
            text = re.sub(r'\s+', ' ', text)  # Collapse whitespace
            text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
            return text.strip()
        
        def similarity(a: str, b: str) -> float:
            """Calculate similarity ratio between two strings."""
            return SequenceMatcher(None, a, b).ratio()
        
        normalized = [normalize(m) for m in recent_messages]
        
        # 1. High-frequency check: 3+ messages in 4 seconds
        if timestamps and len(timestamps) >= 3:
            last_five_times = timestamps[-5:] if len(timestamps) >= 5 else timestamps
            if len(last_five_times) >= 3:
                time_window = (last_five_times[-1] - last_five_times[0]).total_seconds()
                if time_window < 4:  # 3+ messages in 4 seconds → suspicious
                    return True
        
        # 2. Fuzzy similarity repetition: last message similar to 2+ previous
        if len(normalized) >= 3:
            last = normalized[-1]
            matches = sum(similarity(last, msg) > 0.8 for msg in normalized[-5:-1])
            if matches >= 2:
                return True
        
        # 3. Template spam: messages with similar length (±3 chars)
        if len(normalized) >= 5:
            lengths = [len(m) for m in normalized[-5:]]
            if max(lengths) - min(lengths) <= 3 and min(lengths) > 0:
                return True
        
        # 4. Low entropy: too few unique normalized forms
        last_five = normalized[-5:] if len(normalized) >= 5 else normalized
        if len(last_five) >= 5 and len(set(last_five)) <= 2:
            return True
        
        # 5. Exact duplicates (original check)
        unique_messages = set(recent_messages[-5:])
        if len(recent_messages[-5:]) >= 5 and len(unique_messages) <= 2:
            return True
        
        return False
    
    def detect_command_repetition(self, window_seconds: int = 60) -> bool:
        """
        Detect repeated commands within time window.
        
        Args:
            window_seconds: Time window in seconds to check for repetition
        
        Returns:
            True if command repetition detected, False otherwise
        """
        if len(self.command_history) < 3:
            return False
        
        now = datetime.utcnow()
        cutoff_time = now - timedelta(seconds=window_seconds)
        
        # Get commands within time window
        recent_commands = [
            cmd for cmd, timestamp in self.command_history
            if timestamp >= cutoff_time
        ]
        
        if len(recent_commands) < 3:
            return False
        
        # Check for repeated commands
        unique_commands = set(recent_commands)
        if len(unique_commands) <= 2 and len(recent_commands) >= 3:
            # 3+ commands with only 1-2 unique values = repetition
            return True
        
        return False


class UserProfileService:
    """
    Service for managing user profiles and behavioral tracking.
    
    This service provides methods for creating, retrieving, and updating
    user profiles. It tracks room visits, command execution, board creation,
    and calculates behavioral baselines for anomaly detection.
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
    """
    
    def __init__(self, db: Session):
        """
        Initialize the user profile service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.profiles: Dict[int, UserProfile] = {}
    
    def get_profile(self, user_id: int) -> UserProfile:
        """
        Get or create user profile.
        
        This method retrieves a user profile from cache or database,
        creating a new profile if one doesn't exist.
        
        Args:
            user_id: User database ID
        
        Returns:
            UserProfile object for the user
        
        Requirements: 7.5 (read-only access for Vecna)
        """
        # Check cache first
        if user_id in self.profiles:
            return self.profiles[user_id]
        
        # Load from database
        profile_model = self.db.query(UserProfileModel).filter(
            UserProfileModel.user_id == user_id
        ).first()
        
        if profile_model:
            # Parse JSON fields
            interests = json.loads(profile_model.interests) if profile_model.interests else []
            frequent_rooms = json.loads(profile_model.frequent_rooms) if profile_model.frequent_rooms else {}
            recent_rooms = json.loads(profile_model.recent_rooms) if profile_model.recent_rooms else []
            activity_baseline = json.loads(profile_model.activity_baseline) if profile_model.activity_baseline else {}
            
            # Load command history (last 50 commands)
            command_records = self.db.query(CommandHistory).filter(
                CommandHistory.user_id == user_id
            ).order_by(CommandHistory.executed_at.desc()).limit(50).all()
            
            command_history = [
                (record.command, record.executed_at)
                for record in command_records
            ]
            
            # Load unfinished boards
            unfinished_board_records = self.db.query(BoardTracking).filter(
                BoardTracking.user_id == user_id,
                BoardTracking.completed == False
            ).all()
            
            unfinished_boards = [record.board_name for record in unfinished_board_records]
            
            # Create profile object
            profile = UserProfile(
                user_id=user_id,
                interests=interests,
                frequent_rooms=frequent_rooms,
                recent_rooms=recent_rooms,
                command_history=command_history,
                unfinished_boards=unfinished_boards,
                activity_baseline=activity_baseline,
                behavioral_patterns={}
            )
        else:
            # Create new profile
            profile = UserProfile(user_id=user_id)
            self._create_profile_in_db(profile)
        
        # Cache profile
        self.profiles[user_id] = profile
        return profile
    
    def _create_profile_in_db(self, profile: UserProfile) -> None:
        """
        Create a new profile in the database.
        
        Args:
            profile: UserProfile object to persist
        """
        profile_model = UserProfileModel(
            user_id=profile.user_id,
            interests=json.dumps(profile.interests),
            frequent_rooms=json.dumps(profile.frequent_rooms),
            recent_rooms=json.dumps(profile.recent_rooms),
            activity_baseline=json.dumps(profile.activity_baseline),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(profile_model)
        self.db.commit()
    
    def _update_profile_in_db(self, profile: UserProfile) -> None:
        """
        Update an existing profile in the database.
        
        Args:
            profile: UserProfile object to persist
        """
        profile_model = self.db.query(UserProfileModel).filter(
            UserProfileModel.user_id == profile.user_id
        ).first()
        
        if profile_model:
            profile_model.interests = json.dumps(profile.interests)
            profile_model.frequent_rooms = json.dumps(profile.frequent_rooms)
            profile_model.recent_rooms = json.dumps(profile.recent_rooms)
            profile_model.activity_baseline = json.dumps(profile.activity_baseline)
            profile_model.updated_at = datetime.utcnow()
            
            self.db.commit()
    
    def record_room_visit(self, user_id: int, room_name: str) -> None:
        """
        Record a room visit in user profile.
        
        This method updates both recent rooms (last 10) and frequent rooms
        (visit counts) for the user.
        
        Args:
            user_id: User database ID
            room_name: Name of the room visited
        
        Requirements: 7.1 (room visit tracking)
        """
        profile = self.get_profile(user_id)
        
        # Update recent rooms (keep last 10)
        if room_name in profile.recent_rooms:
            profile.recent_rooms.remove(room_name)
        profile.recent_rooms.insert(0, room_name)
        profile.recent_rooms = profile.recent_rooms[:10]
        
        # Update frequent rooms (increment count)
        if room_name in profile.frequent_rooms:
            profile.frequent_rooms[room_name] += 1
        else:
            profile.frequent_rooms[room_name] = 1
        
        # Persist to database
        self._update_profile_in_db(profile)
    
    def record_command(self, user_id: int, command: str) -> None:
        """
        Record a command execution.
        
        This method adds the command to the user's command history
        and persists it to the database.
        
        Args:
            user_id: User database ID
            command: Command text executed
        
        Requirements: 7.2 (command tracking)
        """
        profile = self.get_profile(user_id)
        
        # Add to command history
        timestamp = datetime.utcnow()
        profile.command_history.insert(0, (command, timestamp))
        
        # Keep only last 50 commands in memory
        profile.command_history = profile.command_history[:50]
        
        # Persist to database
        command_record = CommandHistory(
            user_id=user_id,
            command=command,
            executed_at=timestamp
        )
        self.db.add(command_record)
        self.db.commit()
    
    def record_board_creation(
        self, 
        user_id: int, 
        board_name: str, 
        completed: bool = False
    ) -> None:
        """
        Record board creation and completion status.
        
        This method tracks when users create boards and whether they
        complete them, which can be used for Psychic Grip narratives.
        
        Args:
            user_id: User database ID
            board_name: Name of the board created
            completed: Whether the board is completed (default: False)
        
        Requirements: 7.3 (board creation tracking)
        """
        profile = self.get_profile(user_id)
        
        # Check if board already exists
        existing_board = self.db.query(BoardTracking).filter(
            BoardTracking.user_id == user_id,
            BoardTracking.board_name == board_name
        ).first()
        
        if existing_board:
            # Update completion status
            if completed and not existing_board.completed:
                existing_board.completed = True
                existing_board.completed_at = datetime.utcnow()
                self.db.commit()
                
                # Remove from unfinished boards
                if board_name in profile.unfinished_boards:
                    profile.unfinished_boards.remove(board_name)
        else:
            # Create new board tracking record
            board_record = BoardTracking(
                user_id=user_id,
                board_name=board_name,
                created_at=datetime.utcnow(),
                completed=completed,
                completed_at=datetime.utcnow() if completed else None
            )
            self.db.add(board_record)
            self.db.commit()
            
            # Add to unfinished boards if not completed
            if not completed and board_name not in profile.unfinished_boards:
                profile.unfinished_boards.append(board_name)
    
    def update_interests(self, user_id: int, message: str) -> None:
        """
        Extract and update user interests from message content.
        
        This method performs simple keyword extraction to identify
        user interests from their messages.
        
        Args:
            user_id: User database ID
            message: Message text to analyze
        """
        profile = self.get_profile(user_id)
        
        # Simple keyword extraction (can be enhanced with NLP)
        # For now, extract words longer than 5 characters
        words = message.lower().split()
        potential_interests = [
            word.strip('.,!?;:') 
            for word in words 
            if len(word) > 5 and word.isalpha()
        ]
        
        # Add new interests (keep unique, limit to 20)
        for interest in potential_interests:
            if interest not in profile.interests:
                profile.interests.append(interest)
        
        # Keep only last 20 interests
        profile.interests = profile.interests[-20:]
        
        # Persist to database
        self._update_profile_in_db(profile)
    
    def update_activity_baseline(self, user_id: int) -> None:
        """
        Update activity baseline for anomaly detection.
        
        This method calculates statistical baselines for user activity
        including message frequency, command frequency, and room switching.
        
        Args:
            user_id: User database ID
        
        Requirements: 7.4 (baseline activity calculation)
        """
        profile = self.get_profile(user_id)
        
        # Calculate baseline metrics from command history
        if len(profile.command_history) >= 10:
            # Calculate commands per minute
            recent_commands = profile.command_history[:20]
            if len(recent_commands) >= 2:
                time_span = (recent_commands[0][1] - recent_commands[-1][1]).total_seconds()
                if time_span > 0:
                    commands_per_minute = (len(recent_commands) / time_span) * 60
                    profile.activity_baseline['commands_per_minute'] = commands_per_minute
        
        # Calculate room switches per hour
        if len(profile.recent_rooms) >= 3:
            # Estimate based on recent room diversity
            unique_recent_rooms = len(set(profile.recent_rooms[:10]))
            profile.activity_baseline['room_switches_per_hour'] = unique_recent_rooms * 6  # Rough estimate
        
        # Persist to database
        self._update_profile_in_db(profile)
