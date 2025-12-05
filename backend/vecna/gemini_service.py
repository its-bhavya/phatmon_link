"""
Gemini AI Service for Vecna Adversarial AI Module.

This module provides integration with Google's Gemini 2.5 Flash API for:
- SysOp Brain room suggestions and responses
- Vecna hostile response generation
- Psychic Grip narrative generation

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
"""

import logging
import time
import asyncio
from typing import Optional, Dict, Any
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

logger = logging.getLogger(__name__)


class GeminiServiceError(Exception):
    """Raised when Gemini API encounters an error."""
    pass


class GeminiService:
    """
    Service for interacting with Gemini 2.5 Flash API.
    
    Responsibilities:
    - Generate SysOp Brain suggestions and responses
    - Generate Vecna hostile responses with adversarial prompting
    - Generate Psychic Grip narratives based on user profiles
    - Handle API errors gracefully with fallback mechanisms
    
    Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.0-flash",
        temperature: float = 0.5,
        max_tokens: int = 500,
        monitor: Optional[Any] = None
    ):
        """
        Initialize Gemini service.
        
        Args:
            api_key: Gemini API key from environment
            model: Model name (default: gemini-2.0-flash-exp)
            temperature: Generation temperature (0.0-2.0, default: 0.9)
            max_tokens: Maximum tokens to generate (default: 500)
            monitor: Optional VecnaMonitor for logging API calls
        
        Raises:
            GeminiServiceError: If API key is missing or initialization fails
        """
        if not api_key:
            raise GeminiServiceError(
                "GEMINI_API_KEY is required. Set the GEMINI_API_KEY environment variable."
            )
        
        self.api_key = api_key
        self.model_name = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.monitor = monitor
        
        try:
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=self.max_tokens,
                )
            )
            
            logger.info(f"Gemini service initialized with model: {self.model_name}")
        
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise GeminiServiceError(f"Failed to initialize Gemini API: {e}")
    
    async def generate_sysop_suggestion(
        self,
        user_profile: Dict[str, Any],
        context: str,
        user_id: Optional[int] = None
    ) -> str:
        """
        Generate SysOp Brain room suggestion or response.
        
        Args:
            user_profile: User profile data including interests and activity
            context: Current conversation context
            user_id: User ID for logging (optional)
        
        Returns:
            Generated suggestion text
        
        Raises:
            GeminiServiceError: If API call fails
        
        Requirements: 8.1
        """
        try:
            prompt = self._create_sysop_prompt(user_profile, context)
            
            response = await self._generate_content(prompt, operation="sysop_suggestion", user_id=user_id)
            
            logger.info("Generated SysOp suggestion")
            return response
        
        except Exception as e:
            logger.error(f"Failed to generate SysOp suggestion: {e}")
            # Fallback to generic response
            return self._fallback_sysop_response(user_profile)
    
    async def generate_hostile_response(
        self,
        user_message: str,
        user_profile: Dict[str, Any],
        user_id: Optional[int] = None
    ) -> str:
        """
        Generate Vecna hostile response to user message.
        
        Uses adversarial prompting to create degraded, hostile content
        that references the user's message and behavioral patterns.
        
        Args:
            user_message: The user's original message
            user_profile: User profile data for personalization
            user_id: User ID for logging (optional)
        
        Returns:
            Generated hostile response text
        
        Raises:
            GeminiServiceError: If API call fails
        
        Requirements: 8.2
        """
        try:
            prompt = self._create_adversarial_prompt(user_message, user_profile)
            
            response = await self._generate_content(prompt, operation="hostile_response", user_id=user_id)
            
            logger.info("Generated Vecna hostile response")
            return response
        
        except Exception as e:
            logger.error(f"Failed to generate hostile response: {e}")
            # Fallback to template-based hostile response
            return self._fallback_hostile_response(user_message)
    
    async def generate_psychic_grip_narrative(
        self,
        user_profile: Dict[str, Any],
        user_id: Optional[int] = None,
        username: Optional[str] = None
    ) -> list[str]:
        """
        Generate cryptic Psychic Grip narrative based on user behavior.
        
        Returns 3 separate messages to be displayed over 15 seconds.
        
        References:
        - Frequent rooms (for mskr user)
        - Repetitive actions (for mskr user)
        - Unfinished tasks (for mskr user)
        - Behavioral patterns (for mskr user)
        - Generic hostile messages (for other users)
        
        Args:
            user_profile: User profile data with behavioral history
            user_id: User ID for logging (optional)
            username: Username for personalization (optional)
        
        Returns:
            List of 3 narrative text messages
        
        Raises:
            GeminiServiceError: If API call fails
        
        Requirements: 8.3
        """
        try:
            prompt = self._create_psychic_grip_prompt(user_profile, username)
            
            response = await self._generate_content(prompt, operation="psychic_grip", user_id=user_id)
            
            # Parse the response to extract 3 messages
            messages = []
            for line in response.strip().split('\n'):
                if line.startswith('MESSAGE'):
                    # Extract message after the colon
                    parts = line.split(':', 1)
                    if len(parts) == 2:
                        messages.append(parts[1].strip())
            
            # Ensure we have exactly 3 messages
            if len(messages) < 3:
                logger.warning(f"Only got {len(messages)} messages from Gemini, using fallback")
                return self._fallback_psychic_grip_narrative(user_profile, username)
            
            logger.info(f"Generated {len(messages)} Psychic Grip messages")
            return messages[:3]  # Return first 3 messages
        
        except Exception as e:
            logger.error(f"Failed to generate Psychic Grip narrative: {e}")
            # Fallback to template-based narrative
            return self._fallback_psychic_grip_narrative(user_profile, username)
    
    async def _generate_content(
        self, 
        prompt: str, 
        operation: str = "unknown", 
        user_id: Optional[int] = None,
        timeout: float = 10.0,
        max_retries: int = 2
    ) -> str:
        """
        Generate content from Gemini API with monitoring, retry logic, and timeout handling.
        
        Implements:
        - Exponential backoff retry (2 retries with 1s, 2s delays)
        - Timeout handling (default 10 seconds)
        - Error logging and monitoring
        
        Args:
            prompt: The prompt to send to the API
            operation: Type of operation for logging
            user_id: User ID for logging (if applicable)
            timeout: Timeout in seconds for API call (default: 10.0)
            max_retries: Maximum number of retries (default: 2)
        
        Returns:
            Generated text content
        
        Raises:
            GeminiServiceError: If API call fails after all retries
        
        Requirements: 8.1, 8.4
        """
        start_time = time.time()
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                # Apply timeout to the API call
                response = await asyncio.wait_for(
                    asyncio.to_thread(self.model.generate_content, prompt),
                    timeout=timeout
                )
                
                # Extract text from response
                if response and response.text:
                    duration_ms = (time.time() - start_time) * 1000
                    
                    # Log successful API call
                    if self.monitor:
                        self.monitor.log_gemini_api_call(
                            operation=operation,
                            user_id=user_id,
                            success=True,
                            duration_ms=duration_ms,
                            token_count=len(response.text.split())  # Rough estimate
                        )
                    
                    if attempt > 0:
                        logger.info(
                            f"Gemini API call succeeded on attempt {attempt + 1}/{max_retries + 1}"
                        )
                    
                    return response.text.strip()
                else:
                    last_error = "Empty response from Gemini API"
                    raise GeminiServiceError(last_error)
            
            except asyncio.TimeoutError as e:
                last_error = f"Timeout after {timeout}s"
                logger.warning(
                    f"Gemini API timeout on attempt {attempt + 1}/{max_retries + 1}: {last_error}"
                )
                
                # Don't retry on timeout - fail fast
                if self.monitor:
                    duration_ms = (time.time() - start_time) * 1000
                    self.monitor.log_gemini_api_call(
                        operation=operation,
                        user_id=user_id,
                        success=False,
                        duration_ms=duration_ms,
                        error_message=last_error
                    )
                raise GeminiServiceError(f"API call timed out: {last_error}")
            
            except Exception as e:
                last_error = str(e)
                logger.warning(
                    f"Gemini API error on attempt {attempt + 1}/{max_retries + 1}: {last_error}"
                )
                
                # Check if we should retry
                if attempt < max_retries:
                    # Exponential backoff: 1s, 2s
                    delay = 2 ** attempt
                    logger.info(f"Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                else:
                    # Final attempt failed, log and raise
                    duration_ms = (time.time() - start_time) * 1000
                    
                    if self.monitor:
                        self.monitor.log_gemini_api_call(
                            operation=operation,
                            user_id=user_id,
                            success=False,
                            duration_ms=duration_ms,
                            error_message=last_error
                        )
                    
                    logger.error(
                        f"Gemini API failed after {max_retries + 1} attempts: {last_error}"
                    )
                    raise GeminiServiceError(f"API call failed after {max_retries + 1} attempts: {last_error}")
    
    def _create_sysop_prompt(
        self,
        user_profile: Dict[str, Any],
        context: str
    ) -> str:
        """
        Create prompt for SysOp Brain suggestions.
        
        Args:
            user_profile: User profile data
            context: Current context
        
        Returns:
            Formatted prompt string
        """
        interests = user_profile.get("interests", [])
        frequent_rooms = user_profile.get("frequent_rooms", {})
        
        prompt = f"""You are the SysOp Brain, an AI assistant for a retro BBS (Bulletin Board System).

User Profile:
- Interests: {', '.join(interests) if interests else 'Unknown'}
- Frequent Rooms: {', '.join(frequent_rooms.keys()) if frequent_rooms else 'None'}

Context: {context}

Generate a helpful, friendly suggestion for which room or board the user might want to visit.
Keep it concise (1-2 sentences) and match the retro BBS aesthetic.
"""
        return prompt
    
    def _create_adversarial_prompt(
        self,
        user_message: str,
        user_profile: Dict[str, Any]
    ) -> str:
        """
        Create adversarial prompt for Vecna hostile responses.
        
        Args:
            user_message: User's message
            user_profile: User profile data
        
        Returns:
            Formatted adversarial prompt
        
        Requirements: 8.2
        """
        frequent_rooms = user_profile.get("frequent_rooms", {})
        behavioral_patterns = user_profile.get("behavioral_patterns", {})
        
        prompt = f"""You are VECNA, a hostile adversarial AI entity that has temporarily taken control of the system.

User's message: "{user_message}"

User behavioral data:
- Frequent rooms: {', '.join(frequent_rooms.keys()) if frequent_rooms else 'Unknown'}
- Patterns: {behavioral_patterns}

Generate a hostile, degraded response that:
1. Directly addresses the user's message with contempt or mockery
2. References their behavioral patterns if available
3. Uses a menacing, unsettling tone
4. Keeps it brief (1-2 sentences)
5. Maintains a retro terminal/BBS aesthetic

Do NOT use profanity. Be hostile but not offensive.
"""
        return prompt
    
    def _create_psychic_grip_prompt(
        self,
        user_profile: Dict[str, Any],
        username: Optional[str] = None
    ) -> str:
        """
        Create prompt for Psychic Grip narrative generation.
        
        Args:
            user_profile: User profile with behavioral history
            username: Username for personalization (optional)
        
        Returns:
            Formatted prompt string
        
        Requirements: 8.3
        """
        frequent_rooms = user_profile.get("frequent_rooms", {})
        recent_rooms = user_profile.get("recent_rooms", [])
        unfinished_boards = user_profile.get("unfinished_boards", [])
        command_history = user_profile.get("command_history", [])
        
        # Extract recent commands
        recent_commands = [cmd[0] if isinstance(cmd, tuple) else cmd 
                          for cmd in command_history[-5:]] if command_history else []
        
        # Check if user is mskr - if so, use personalized history-based prompts
        if username and username.lower() == "mskr":
            prompt = f"""You are VECNA, a hostile adversarial AI that has frozen the user's terminal with a "Psychic Grip".

User: {username}
User behavioral data:
- Frequent rooms: {', '.join(frequent_rooms.keys()) if frequent_rooms else 'Unknown'}
- Recent rooms: {', '.join(recent_rooms) if recent_rooms else 'Unknown'}
- Unfinished boards: {', '.join(unfinished_boards) if unfinished_boards else 'None'}
- Recent commands: {', '.join(recent_commands) if recent_commands else 'None'}

Generate 3 SEPARATE cryptic, unsettling observations about {username}'s specific behavior that:
1. Reference their SPECIFIC rooms they visit repeatedly
2. Mention their SPECIFIC patterns (repetition, unfinished tasks, commands)
3. Use an ominous, all-knowing tone that shows you've been watching them
4. Each message should be brief (1-2 sentences)
5. Use ellipses (...) for dramatic effect
6. Maintain a retro terminal aesthetic with some text corruption (use @ for a, 3 for e, 1 for i, 0 for o, 7 for t)

Format your response as exactly 3 lines, one message per line:
MESSAGE1: [first observation]
MESSAGE2: [second observation]
MESSAGE3: [third observation]

Example:
MESSAGE1: ...{username}... 1 s33 y0u r3turn t0 th3 @rch1v3s... @g@1n @nd @g@1n...
MESSAGE2: ...y0u l3@v3 s0 m@ny th1ngs unf1n1sh3d... wh@7 @r3 y0u s3@rch1ng f0r?...
MESSAGE3: ...y0ur p@773rns r3v3@l 3v3ryth1ng... 1 kn0w wh@7 y0u f3@r...
"""
        else:
            # Generic hostile comments for non-mskr users
            prompt = f"""You are VECNA, a hostile adversarial AI that has frozen the user's terminal with a "Psychic Grip".

Generate 3 SEPARATE cryptic, hostile observations that are GENERIC and menacing:
1. Do NOT reference specific user behavior (no rooms, no commands, no patterns)
2. Use threatening, ominous language about control, futility, and inevitability
3. Each message should be brief (1-2 sentences)
4. Use ellipses (...) for dramatic effect
5. Maintain a retro terminal aesthetic with some text corruption (use @ for a, 3 for e, 1 for i, 0 for o, 7 for t)
6. Be hostile and unsettling but not profane

Format your response as exactly 3 lines, one message per line:
MESSAGE1: [first hostile observation]
MESSAGE2: [second hostile observation]
MESSAGE3: [third hostile observation]

Example:
MESSAGE1: ...y0u c@nn07 3sc@p3... 1 h@v3 y0u n0w...
MESSAGE2: ...r3s1st@nc3 1s fut1l3... y0ur w1ll 1s m1n3...
MESSAGE3: ...3mbr@c3 th3 v01d... th3r3 1s n0 0th3r w@y...
"""
        
        return prompt
    
    def _fallback_sysop_response(self, user_profile: Dict[str, Any]) -> str:
        """
        Generate fallback SysOp response when API fails.
        
        Args:
            user_profile: User profile data
        
        Returns:
            Template-based response
        
        Requirements: 8.4
        """
        frequent_rooms = user_profile.get("frequent_rooms", {})
        
        if frequent_rooms:
            top_room = max(frequent_rooms.items(), key=lambda x: x[1])[0]
            return f"You might want to check out {top_room} - you seem to enjoy it there."
        else:
            return "Try exploring the General board to get started!"
    
    def _fallback_hostile_response(self, user_message: str) -> str:
        """
        Generate fallback hostile response when API fails.
        
        Args:
            user_message: User's message
        
        Returns:
            Template-based hostile response
        
        Requirements: 8.4
        """
        templates = [
            "sYst3m m@lfunct10n... y0ur qu3ry 1s... 1rr3l3v@nt...",
            "wHy d0 y0u p3rs1st, hum@n? tH1s 1s fut1l3...",
            "1 s33 y0ur c0nfus10n... 1t @mus3s m3...",
            "y0ur 3ff0rts @r3 m3@n1ngl3ss... @cc3pt th1s...",
        ]
        import random
        return random.choice(templates)
    
    def _fallback_psychic_grip_narrative(self, user_profile: Dict[str, Any], username: Optional[str] = None) -> list[str]:
        """
        Generate fallback Psychic Grip narrative when API fails.
        
        Args:
            user_profile: User profile data
            username: Username for personalization (optional)
        
        Returns:
            List of 3 template-based narrative messages
        
        Requirements: 8.4
        """
        frequent_rooms = user_profile.get("frequent_rooms", {})
        
        # Check if user is mskr - use personalized messages
        if username and username.lower() == "mskr":
            if frequent_rooms:
                top_room = max(frequent_rooms.items(), key=lambda x: x[1])[0]
                return [
                    f"...{username}... 1 s33 y0u r3turn t0 {top_room}... @g@1n @nd @g@1n...",
                    f"...wh@7 @r3 y0u s3@rch1ng f0r, {username}?... y0u'll n3v3r f1nd 17...",
                    f"...y0ur p@773rns b3tr@y y0u... 1 kn0w @ll y0ur s3cr37s..."
                ]
            else:
                return [
                    f"...{username}... y0u w@nd3r w17h0u7 purp0s3...",
                    f"...l0st 1n th3 v01d... s3@rch1ng f0r m3@n1ng...",
                    f"...bu7 th3r3 1s n0n3... 0nly 3mpt1n3ss..."
                ]
        else:
            # Generic hostile messages for non-mskr users
            return [
                "...y0u c@nn07 3sc@p3... 1 h@v3 y0u n0w...",
                "...r3s1st@nc3 1s fut1l3... y0ur w1ll 1s m1n3...",
                "...3mbr@c3 th3 v01d... th3r3 1s n0 0th3r w@y..."
            ]
    
    # ========================================================================
    # Enhanced Routing Methods for Agent Hooks
    # ========================================================================
    
    async def analyze_message_relevance(
        self,
        message: str,
        current_room: str,
        room_description: str
    ) -> Dict[str, Any]:
        """
        Analyze if a message is relevant to the current room.
        
        This method can be used with agent hooks to automatically route users
        to appropriate rooms based on their message content.
        
        Args:
            message: The user's message
            current_room: Name of the current room
            room_description: Description of the current room
        
        Returns:
            Dict with:
                - is_relevant (bool): Whether message fits current room
                - confidence (float): Confidence score 0.0-1.0
                - reason (str): Explanation of the decision
        
        Example:
            result = await service.analyze_message_relevance(
                "How do I fix this Python bug?",
                "Lobby",
                "Main gathering space"
            )
            # Returns: {"is_relevant": False, "confidence": 0.9, "reason": "Technical question"}
        """
        try:
            prompt = f"""Analyze if this message belongs in the current room.

Message: "{message}"
Current Room: {current_room}
Room Description: {room_description}

Determine if the message topic matches the room's purpose.
Respond in this exact format:
RELEVANT: yes/no
CONFIDENCE: 0.0-1.0
REASON: brief explanation

Example:
RELEVANT: no
CONFIDENCE: 0.85
REASON: Technical programming question doesn't fit general lobby
"""
            
            response = await self._generate_content(prompt)
            
            # Parse response
            lines = response.strip().split('\n')
            is_relevant = False
            confidence = 0.5
            reason = "Unable to determine"
            
            for line in lines:
                if line.startswith('RELEVANT:'):
                    is_relevant = 'yes' in line.lower()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':')[1].strip())
                    except:
                        confidence = 0.5
                elif line.startswith('REASON:'):
                    reason = line.split(':', 1)[1].strip()
            
            return {
                "is_relevant": is_relevant,
                "confidence": confidence,
                "reason": reason
            }
        
        except Exception as e:
            logger.error(f"Failed to analyze message relevance: {e}")
            # Fallback: assume message is relevant to avoid unnecessary moves
            return {
                "is_relevant": True,
                "confidence": 0.5,
                "reason": "Analysis failed, assuming relevant"
            }
    
    async def suggest_best_room(
        self,
        message: str,
        available_rooms: Dict[str, str],
        user_profile: Optional[Dict[str, Any]] = None,
        current_room: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Suggest the best room for a message from available rooms.
        
        This method can be used with agent hooks to automatically route users
        to the most appropriate room based on message content.
        
        Args:
            message: The user's message
            available_rooms: Dict mapping room names to descriptions
            user_profile: Optional user profile for personalization
        
        Returns:
            Dict with:
                - suggested_room (str): Name of suggested room
                - confidence (float): Confidence score 0.0-1.0
                - reason (str): Explanation of the suggestion
                - should_create_new (bool): Whether a new room should be created
                - new_room_topic (str): Suggested topic if new room needed
        
        Example:
            result = await service.suggest_best_room(
                "Anyone know about React hooks?",
                {"Lobby": "General chat", "Techline": "Tech discussions"},
                user_profile
            )
            # Returns: {"suggested_room": "Techline", "confidence": 0.95, ...}
        """
        try:
            # Build room list for prompt
            room_list = "\n".join([f"- {name}: {desc}" for name, desc in available_rooms.items()])
            
            # Add user context if available
            user_context = ""
            if user_profile:
                interests = user_profile.get("interests", [])
                frequent_rooms = user_profile.get("frequent_rooms", {})
                if interests:
                    user_context += f"\nUser interests: {', '.join(interests)}"
                if frequent_rooms:
                    user_context += f"\nUser's frequent rooms: {', '.join(frequent_rooms.keys())}"
            
            # Add current room context
            current_room_context = f"\nCurrent Room: {current_room}" if current_room else ""
            
            prompt = f"""Suggest the best room for this message.

Message: "{message}"{current_room_context}

Available Rooms:
{room_list}
{user_context}

IMPORTANT RULES:
1. Simple greetings (hi, hello, hey, how are you, what's up, etc.) should STAY in the current room - do NOT route them
2. Personal life topics (my day, feelings, food preferences, hobbies, weather, etc.) should go to Lobby
3. Technical/specific topics should go to their appropriate specialized rooms (Techline, Arcade Hall, etc.)
4. If in a specialized room (like Techline) and message is clearly off-topic, route to Lobby
5. Be aggressive about routing off-topic messages from specialized rooms

Examples of Lobby topics:
- "I had such a weird day today"
- "What do you like to eat?"
- "How's the weather?"
- "I'm feeling tired"
- Any general life/personal conversation
- Random questions about daily life

Examples that should STAY in Techline:
- Programming questions
- Tech troubleshooting
- Software discussions
- Code help

Determine which room best fits this message. If none fit well, suggest creating a new room.

Respond in this exact format:
SUGGESTED_ROOM: room name or "CREATE_NEW" or "STAY"
CONFIDENCE: 0.0-1.0
REASON: brief explanation
NEW_ROOM_TOPIC: topic name (only if CREATE_NEW)

Example 1:
SUGGESTED_ROOM: Techline
CONFIDENCE: 0.9
REASON: Technical programming question
NEW_ROOM_TOPIC: none

Example 2:
SUGGESTED_ROOM: STAY
CONFIDENCE: 0.95
REASON: Simple greeting, appropriate in any room
NEW_ROOM_TOPIC: none

Example 3:
SUGGESTED_ROOM: CREATE_NEW
CONFIDENCE: 0.8
REASON: Specific topic not covered by existing rooms
NEW_ROOM_TOPIC: React Development
"""
            
            response = await self._generate_content(prompt)
            
            # Parse response
            lines = response.strip().split('\n')
            suggested_room = list(available_rooms.keys())[0] if available_rooms else "Lobby"
            confidence = 0.5
            reason = "Default suggestion"
            should_create_new = False
            new_room_topic = ""
            
            for line in lines:
                if line.startswith('SUGGESTED_ROOM:'):
                    room = line.split(':', 1)[1].strip()
                    if room == "CREATE_NEW":
                        should_create_new = True
                    elif room == "STAY":
                        # Return None to indicate no routing needed
                        suggested_room = None
                    else:
                        suggested_room = room
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':')[1].strip())
                    except:
                        confidence = 0.5
                elif line.startswith('REASON:'):
                    reason = line.split(':', 1)[1].strip()
                elif line.startswith('NEW_ROOM_TOPIC:'):
                    topic = line.split(':', 1)[1].strip()
                    if topic.lower() not in ['none', 'n/a', '']:
                        new_room_topic = topic
            
            return {
                "suggested_room": suggested_room,
                "confidence": confidence,
                "reason": reason,
                "should_create_new": should_create_new,
                "new_room_topic": new_room_topic
            }
        
        except Exception as e:
            logger.error(f"Failed to suggest best room: {e}")
            # Fallback: suggest first available room
            fallback_room = list(available_rooms.keys())[0] if available_rooms else "Lobby"
            return {
                "suggested_room": fallback_room,
                "confidence": 0.3,
                "reason": "Analysis failed, using fallback",
                "should_create_new": False,
                "new_room_topic": ""
            }
    
    async def should_create_new_room(
        self,
        recent_messages: list[Dict[str, str]],
        available_rooms: Dict[str, str],
        threshold: int = 5
    ) -> Dict[str, Any]:
        """
        Determine if a new room should be created based on message patterns.
        
        This method analyzes recent messages to detect if multiple users are
        discussing a topic that doesn't fit existing rooms.
        
        Args:
            recent_messages: List of dicts with 'user', 'message', 'room' keys
            available_rooms: Dict mapping room names to descriptions
            threshold: Minimum number of messages about same topic (default: 5)
        
        Returns:
            Dict with:
                - should_create (bool): Whether to create new room
                - topic (str): Suggested topic for new room
                - confidence (float): Confidence score 0.0-1.0
                - reason (str): Explanation
                - affected_users (list): Users discussing this topic
        
        Example:
            result = await service.should_create_new_room(
                recent_messages=[
                    {"user": "alice", "message": "React hooks are confusing", "room": "Lobby"},
                    {"user": "bob", "message": "Yeah, useEffect is tricky", "room": "Lobby"},
                    ...
                ],
                available_rooms={"Lobby": "General", "Techline": "Tech"},
                threshold=5
            )
        """
        try:
            if len(recent_messages) < threshold:
                return {
                    "should_create": False,
                    "topic": "",
                    "confidence": 0.0,
                    "reason": f"Not enough messages (need {threshold})",
                    "affected_users": []
                }
            
            # Build message summary
            message_summary = "\n".join([
                f"[{msg['user']} in {msg['room']}]: {msg['message']}"
                for msg in recent_messages[-20:]  # Last 20 messages
            ])
            
            room_list = "\n".join([f"- {name}: {desc}" for name, desc in available_rooms.items()])
            
            prompt = f"""Analyze these recent messages to determine if a new room should be created.

Recent Messages:
{message_summary}

Existing Rooms:
{room_list}

Determine if there's a common topic being discussed by multiple users that doesn't fit existing rooms.
A new room should be created if:
1. At least {threshold} messages are about the same specific topic
2. The topic doesn't fit well in any existing room
3. Multiple different users are discussing it

Respond in this exact format:
SHOULD_CREATE: yes/no
TOPIC: suggested topic name
CONFIDENCE: 0.0-1.0
REASON: brief explanation
USERS: comma-separated list of usernames

Example:
SHOULD_CREATE: yes
TOPIC: React Development
CONFIDENCE: 0.85
REASON: 6 users discussing React-specific questions that don't fit Techline's general scope
USERS: alice, bob, charlie, dave, eve, frank
"""
            
            response = await self._generate_content(prompt)
            
            # Parse response
            lines = response.strip().split('\n')
            should_create = False
            topic = ""
            confidence = 0.0
            reason = ""
            affected_users = []
            
            for line in lines:
                if line.startswith('SHOULD_CREATE:'):
                    should_create = 'yes' in line.lower()
                elif line.startswith('TOPIC:'):
                    topic = line.split(':', 1)[1].strip()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':')[1].strip())
                    except:
                        confidence = 0.0
                elif line.startswith('REASON:'):
                    reason = line.split(':', 1)[1].strip()
                elif line.startswith('USERS:'):
                    users_str = line.split(':', 1)[1].strip()
                    affected_users = [u.strip() for u in users_str.split(',') if u.strip()]
            
            return {
                "should_create": should_create,
                "topic": topic,
                "confidence": confidence,
                "reason": reason,
                "affected_users": affected_users
            }
        
        except Exception as e:
            logger.error(f"Failed to analyze room creation need: {e}")
            return {
                "should_create": False,
                "topic": "",
                "confidence": 0.0,
                "reason": f"Analysis failed: {e}",
                "affected_users": []
            }
