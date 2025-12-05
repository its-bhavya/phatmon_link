"""
SysOp Brain Service for Phantom Link BBS.

This module provides the primary AI routing system that handles normal
BBS operations including message routing, dynamic board creation, and
room suggestions based on user profiles.

The SysOp Brain is the baseline AI that operates when Vecna is not active.
It uses Gemini 2.5 Flash for intelligent routing decisions and room suggestions.

Requirements: 1.1, 1.2, 1.4, 1.5
"""

import logging
from typing import Dict, List, Any, Optional
from backend.database import User
from backend.vecna.gemini_service import GeminiService
from backend.rooms.service import RoomService
from backend.rooms.models import Room
from backend.vecna.user_profile import UserProfile

logger = logging.getLogger(__name__)


class SysOpBrain:
    """
    Primary AI routing system for normal BBS operations.
    
    The SysOp Brain handles:
    - Message routing and processing
    - Dynamic board creation based on conversation topics
    - Room suggestions based on user profile analysis
    - Workflow management for normal operations
    
    This service operates as the baseline AI and always resumes control
    after Vecna activations.
    
    Requirements: 1.1, 1.2, 1.4, 1.5
    """
    
    def __init__(self, gemini_service: GeminiService, room_service: RoomService):
        """
        Initialize the SysOp Brain.
        
        Args:
            gemini_service: Gemini AI service for content generation
            room_service: Room service for room management
        """
        self.gemini = gemini_service
        self.room_service = room_service
        logger.info("SysOp Brain initialized")
    
    async def process_message(
        self,
        user: User,
        message: str,
        current_room: str,
        user_profile: Optional[UserProfile] = None
    ) -> Dict[str, Any]:
        """
        Process incoming message with normal routing logic.
        
        This method performs the primary message routing and board creation
        operations. It analyzes the message content and user profile to
        determine appropriate actions.
        
        Args:
            user: User object who sent the message
            message: Message text content
            current_room: Name of the room where message was sent
            user_profile: Optional user profile for personalized routing
        
        Returns:
            Dict containing:
                - action: Type of action taken ('route', 'create_board', 'suggest_room')
                - room: Target room name (if routing)
                - board: Created board object (if board created)
                - suggestion: Room suggestion text (if suggesting)
                - message: Response message to user
        
        Requirements: 1.1 (normal routing), 1.2 (use user profile data)
        """
        try:
            logger.info(f"SysOp Brain processing message from {user.username} in {current_room}")
            
            # Get user profile data for context
            profile_data = self._extract_profile_data(user_profile) if user_profile else {}
            
            # Get current room info
            room = self.room_service.get_room(current_room)
            room_description = room.description if room else "Unknown room"
            
            # Always check if there's a better room for this message
            # (Skip relevance check to ensure routing always happens)
            # Get available rooms
            available_rooms = {
                r.name: r.description 
                for r in self.room_service.get_rooms()
            }
            
            # Suggest best room for this message
            suggestion = await self.gemini.suggest_best_room(
                message=message,
                available_rooms=available_rooms,
                user_profile=profile_data,
                current_room=current_room
            )
            
            # Only route if suggested room is different from current room
            # If suggested_room is None, it means stay in current room (e.g., simple greeting)
            if suggestion["suggested_room"] and suggestion["suggested_room"] != current_room:
                
                # Check if we should create a new board
                if suggestion["should_create_new"] and suggestion["new_room_topic"]:
                    # Create dynamic board
                    new_board = await self.create_dynamic_board(
                        topic=suggestion["new_room_topic"],
                        user=user
                    )
                    
                    if new_board:
                        return {
                            "action": "create_board",
                            "board": new_board,
                            "message": f"[SYSOP] Created new board '{new_board.name}' for this topic. Moving you there now.",
                            "room": new_board.name
                        }
                
                # Suggest existing room
                return {
                    "action": "suggest_room",
                    "room": suggestion["suggested_room"],
                    "suggestion": f"[SYSOP] This might fit better in {suggestion['suggested_room']}. {suggestion['reason']}",
                    "message": f"[SYSOP] Suggestion: Try {suggestion['suggested_room']} - {suggestion['reason']}"
                }
            
            # Message is relevant to current room, continue normal operation
            return {
                "action": "route",
                "room": current_room,
                "message": None  # No special message, just route normally
            }
        
        except Exception as e:
            logger.error(f"Error in SysOp Brain message processing: {e}")
            # Fallback to simple routing
            return {
                "action": "route",
                "room": current_room,
                "message": None
            }
    
    async def suggest_rooms(self, user_profile: UserProfile) -> List[str]:
        """
        Generate room suggestions based on user interests and activity.
        
        This method analyzes the user's profile including interests,
        frequent rooms, and recent activity to suggest rooms they might
        be interested in visiting.
        
        Args:
            user_profile: User profile with interests and activity data
        
        Returns:
            List of room names suggested for the user
        
        Requirements: 1.4 (auto-suggest rooms based on user profile)
        """
        try:
            logger.info(f"Generating room suggestions for user {user_profile.user_id}")
            
            # Get available rooms
            available_rooms = self.room_service.get_rooms()
            
            if not available_rooms:
                return []
            
            # Extract profile data
            profile_data = self._extract_profile_data(user_profile)
            
            # Build context for Gemini
            context = f"User is looking for interesting rooms to visit. "
            
            if profile_data.get("interests"):
                context += f"Their interests include: {', '.join(profile_data['interests'][:5])}. "
            
            if profile_data.get("frequent_rooms"):
                top_rooms = sorted(
                    profile_data["frequent_rooms"].items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
                context += f"They frequently visit: {', '.join([r[0] for r in top_rooms])}. "
            
            # Get AI suggestion
            suggestion_text = await self.gemini.generate_sysop_suggestion(
                user_profile=profile_data,
                context=context
            )
            
            # Extract room names from suggestion
            # Simple heuristic: look for room names in the suggestion text
            suggested_rooms = []
            for room in available_rooms:
                if room.name in suggestion_text:
                    suggested_rooms.append(room.name)
            
            # If no rooms found in text, suggest based on profile
            if not suggested_rooms:
                # Suggest rooms user hasn't visited recently
                recent_rooms = set(user_profile.recent_rooms)
                unvisited_rooms = [
                    room.name for room in available_rooms
                    if room.name not in recent_rooms
                ]
                
                if unvisited_rooms:
                    suggested_rooms = unvisited_rooms[:3]
                else:
                    # Suggest least visited rooms
                    frequent_rooms = user_profile.frequent_rooms
                    suggested_rooms = sorted(
                        [room.name for room in available_rooms],
                        key=lambda r: frequent_rooms.get(r, 0)
                    )[:3]
            
            logger.info(f"Suggested rooms: {suggested_rooms}")
            return suggested_rooms
        
        except Exception as e:
            logger.error(f"Error generating room suggestions: {e}")
            # Fallback: return first 3 rooms
            return [room.name for room in self.room_service.get_rooms()[:3]]
    
    async def create_dynamic_board(
        self,
        topic: str,
        user: User
    ) -> Optional[Room]:
        """
        Create a new board dynamically based on conversation topic.
        
        This method creates a new room/board when the AI detects that
        a conversation topic doesn't fit existing rooms. The board is
        persisted for future sessions.
        
        Args:
            topic: Topic name for the new board
            user: User who triggered the board creation
        
        Returns:
            Room object if created successfully, None otherwise
        
        Requirements: 1.5 (persist board state for future sessions)
        """
        try:
            logger.info(f"Creating dynamic board for topic: {topic}")
            
            # Sanitize topic name (remove special characters, limit length)
            board_name = self._sanitize_board_name(topic)
            
            # Check if board already exists
            existing_room = self.room_service.get_room(board_name)
            if existing_room:
                logger.info(f"Board '{board_name}' already exists")
                return existing_room
            
            # Generate board description using AI
            profile_data = {"interests": [], "frequent_rooms": {}}
            description_prompt = f"Generate a brief, engaging description (1 sentence) for a BBS board about: {topic}"
            
            try:
                description = await self.gemini.generate_sysop_suggestion(
                    user_profile=profile_data,
                    context=description_prompt
                )
            except Exception as e:
                logger.warning(f"Failed to generate AI description: {e}")
                description = f"Discussion board for {topic}"
            
            # Create the room
            new_room = Room(name=board_name, description=description)
            self.room_service.rooms[board_name] = new_room
            
            logger.info(f"Created new board: {board_name}")
            return new_room
        
        except Exception as e:
            logger.error(f"Error creating dynamic board: {e}")
            return None
    
    def _extract_profile_data(self, user_profile: UserProfile) -> Dict[str, Any]:
        """
        Extract profile data into a dictionary format for Gemini.
        
        Args:
            user_profile: UserProfile object
        
        Returns:
            Dict with profile data
        
        Requirements: 1.2 (use user profile data)
        """
        return {
            "interests": user_profile.interests,
            "frequent_rooms": user_profile.frequent_rooms,
            "recent_rooms": user_profile.recent_rooms,
            "behavioral_patterns": user_profile.behavioral_patterns
        }
    
    def _sanitize_board_name(self, topic: str) -> str:
        """
        Sanitize topic name to create valid board name.
        
        Args:
            topic: Raw topic string
        
        Returns:
            Sanitized board name
        """
        # Remove special characters, keep alphanumeric and spaces
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9\s]', '', topic)
        
        # Convert to title case and limit length
        sanitized = sanitized.strip().title()
        
        # Limit to 30 characters
        if len(sanitized) > 30:
            sanitized = sanitized[:30].strip()
        
        # Replace spaces with underscores for room name
        # But keep it readable
        if ' ' in sanitized:
            # Keep spaces for readability
            pass
        
        return sanitized if sanitized else "New Board"
