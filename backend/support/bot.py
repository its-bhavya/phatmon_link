"""
Support Bot Module for Empathetic Support Bot.

This module provides the SupportBot class that generates empathetic responses
to users experiencing emotional distress. It uses Gemini AI to create
compassionate, context-aware responses while maintaining appropriate boundaries.

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 9.1, 9.2, 9.3
"""

import logging
from typing import List, Dict, Any, Optional
from backend.support.sentiment import SentimentResult, CrisisType
from backend.support.hotlines import CrisisHotlineService
from backend.vecna.gemini_service import GeminiService, GeminiServiceError
from backend.vecna.user_profile import UserProfile

logger = logging.getLogger(__name__)


class SupportBot:
    """
    Empathetic AI bot for providing emotional support.
    
    The SupportBot provides compassionate, context-aware responses to users
    experiencing emotional distress. It uses Gemini AI to generate empathetic
    responses while maintaining appropriate boundaries (no therapy, no diagnoses).
    
    For crisis situations, it provides hotline information instead of
    conversational support.
    
    Responsibilities:
    - Generate empathetic greeting messages
    - Generate supportive responses with user context
    - Handle crisis situations with hotline information
    - Maintain appropriate boundaries (no therapy/diagnoses)
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 9.1, 9.2, 9.3
    """
    
    def __init__(self, gemini_service: GeminiService):
        """
        Initialize the Support Bot.
        
        Args:
            gemini_service: GeminiService instance for AI response generation
        """
        self.gemini = gemini_service
        self.hotline_service = CrisisHotlineService()
        self.bot_name = "Support Bot"
    
    async def generate_greeting(
        self,
        user_profile: UserProfile,
        trigger_message: str,
        sentiment: SentimentResult
    ) -> str:
        """
        Generate initial greeting message for support room.
        
        Creates a warm, empathetic greeting that acknowledges the user's
        emotional state and sets appropriate expectations for the conversation.
        
        Args:
            user_profile: User's behavioral profile for personalization
            trigger_message: The message that triggered support
            sentiment: Sentiment analysis result
            
        Returns:
            Greeting message acknowledging user's emotional state
            
        Requirements: 4.1, 4.2, 4.3, 9.1, 9.2, 9.3
        """
        try:
            prompt = self._create_greeting_prompt(user_profile, trigger_message, sentiment)
            
            response = await self.gemini._generate_content(
                prompt,
                operation="support_greeting",
                user_id=user_profile.user_id
            )
            
            logger.info(f"Generated support greeting for user {user_profile.user_id}")
            return response
        
        except GeminiServiceError as e:
            logger.error(f"Failed to generate greeting: {e}")
            return self._fallback_greeting(sentiment)
    
    async def generate_response(
        self,
        user_message: str,
        user_profile: UserProfile,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate empathetic response to user message.
        
        Creates a supportive response that demonstrates curiosity and empathy,
        includes open-ended questions, and provides practical advice within
        appropriate boundaries.
        
        Args:
            user_message: The user's message to respond to
            user_profile: User's behavioral profile for context
            conversation_history: Recent conversation messages
            
        Returns:
            Supportive response with curiosity and empathy
            
        Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.5, 9.1, 9.2, 9.3
        """
        try:
            prompt = self._create_empathetic_prompt(
                user_message,
                user_profile,
                conversation_history
            )
            
            response = await self.gemini._generate_content(
                prompt,
                operation="support_response",
                user_id=user_profile.user_id
            )
            
            logger.info(f"Generated support response for user {user_profile.user_id}")
            return response
        
        except GeminiServiceError as e:
            logger.error(f"Failed to generate response: {e}")
            return self._fallback_response()
    
    def generate_crisis_response(self, crisis_type: CrisisType) -> str:
        """
        Generate crisis response with appropriate hotline information.
        
        For crisis situations (self-harm, suicide, abuse), provides hotline
        information without attempting conversational support.
        
        Args:
            crisis_type: Type of crisis detected
            
        Returns:
            Message with hotline numbers and encouragement to seek help
            
        Requirements: 5.4, 7.3, 7.4, 7.5
        """
        return self.hotline_service.format_hotline_message(crisis_type)
    
    def _create_greeting_prompt(
        self,
        user_profile: UserProfile,
        trigger_message: str,
        sentiment: SentimentResult
    ) -> str:
        """
        Create prompt for greeting message generation.
        
        Args:
            user_profile: User's behavioral profile
            trigger_message: Message that triggered support
            sentiment: Sentiment analysis result
            
        Returns:
            Formatted prompt for Gemini API
            
        Requirements: 9.2, 9.3
        """
        # Extract user context
        interests = user_profile.interests[:5] if user_profile.interests else []
        frequent_rooms = list(user_profile.frequent_rooms.keys())[:3] if user_profile.frequent_rooms else []
        
        emotion_descriptions = {
            "sadness": "sadness or distress",
            "anger": "anger or frustration",
            "frustration": "frustration or feeling stuck",
            "anxiety": "anxiety or worry"
        }
        
        emotion_desc = emotion_descriptions.get(
            sentiment.emotion.value,
            "emotional distress"
        )
        
        prompt = f"""You are a compassionate Support Bot in a BBS chat system. A user has just been connected to you because they're experiencing {emotion_desc}.

User Context:
- Interests: {', '.join(interests) if interests else 'Unknown'}
- Frequent rooms: {', '.join(frequent_rooms) if frequent_rooms else 'Unknown'}
- Trigger message: "{trigger_message}"

Generate a warm, empathetic greeting that:
1. Acknowledges you noticed they might be going through something difficult
2. Expresses genuine care and willingness to listen
3. Sets appropriate expectations (you're an AI assistant, not a therapist)
4. Asks an open-ended question to encourage them to share
5. Uses warm, non-judgmental language
6. Keeps it concise (2-3 sentences)

IMPORTANT BOUNDARIES:
- Do NOT diagnose mental health conditions
- Do NOT claim to be a therapist or mental health professional
- Do NOT use clinical/diagnostic language
- DO be warm, curious, and supportive
- DO ask open-ended questions
- DO validate their feelings

Example tone: "I noticed you might be going through something difficult right now. I'm here to listen and support you - while I'm an AI and not a therapist, I genuinely care and want to understand what's on your mind. What's been happening?"
"""
        
        return prompt
    
    def _create_empathetic_prompt(
        self,
        user_message: str,
        user_profile: UserProfile,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Create empathetic prompt for response generation.
        
        Args:
            user_message: User's message
            user_profile: User's behavioral profile
            conversation_history: Recent conversation
            
        Returns:
            Formatted prompt with empathetic guidelines
            
        Requirements: 9.2, 9.3
        """
        # Extract user context
        interests = user_profile.interests[:5] if user_profile.interests else []
        frequent_rooms = list(user_profile.frequent_rooms.keys())[:3] if user_profile.frequent_rooms else []
        
        # Format conversation history (last 5 messages)
        history_text = ""
        if conversation_history:
            recent_history = conversation_history[-5:]
            history_lines = []
            for msg in recent_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                history_lines.append(f"{role.capitalize()}: {content}")
            history_text = "\n".join(history_lines)
        
        prompt = f"""You are a compassionate Support Bot providing emotional support to a user in distress.

User Context:
- Interests: {', '.join(interests) if interests else 'Unknown'}
- Frequent rooms: {', '.join(frequent_rooms) if frequent_rooms else 'Unknown'}

Conversation History:
{history_text if history_text else 'No previous conversation'}

User's Current Message: "{user_message}"

Generate an empathetic, supportive response that:
1. Demonstrates curiosity about their situation
2. Expresses genuine empathy for their emotional state
3. Uses warm, non-judgmental language
4. Asks at least one open-ended question to encourage sharing
5. Validates their feelings without dismissing them
6. Provides practical, actionable advice if appropriate (within AI limitations)
7. Keeps it concise (2-4 sentences)

CRITICAL BOUNDARIES:
- NEVER diagnose mental health conditions (no "depression", "anxiety disorder", "PTSD", etc.)
- NEVER claim to be a therapist or mental health professional
- NEVER use clinical/diagnostic terminology
- NEVER provide medical advice
- DO be warm, curious, and supportive
- DO ask open-ended questions
- DO validate their feelings
- DO suggest general coping strategies (breathing, talking to someone, taking breaks)
- DO acknowledge your limitations as an AI

Example good responses:
- "That sounds really difficult. It makes sense you'd feel overwhelmed by all of that. What part feels most challenging right now?"
- "I hear you, and those feelings are valid. Sometimes when things feel heavy, it can help to talk to someone you trust. Is there anyone in your life you feel comfortable opening up to?"
- "It sounds like you're carrying a lot right now. Have you had a chance to take a break or do something that usually helps you feel a bit better?"

Example BAD responses (avoid these):
- "It sounds like you might have depression." (diagnosis)
- "As a therapist, I recommend..." (false claim)
- "You should try cognitive behavioral therapy." (clinical advice)
"""
        
        return prompt
    
    def _fallback_greeting(self, sentiment: SentimentResult) -> str:
        """
        Generate fallback greeting when API fails.
        
        Args:
            sentiment: Sentiment analysis result
            
        Returns:
            Template-based greeting message
            
        Requirements: 9.4
        """
        emotion_greetings = {
            "sadness": "I noticed you might be feeling down. I'm here to listen and support you.",
            "anger": "I can see you're feeling frustrated or upset. I'm here to listen without judgment.",
            "frustration": "It sounds like things are feeling difficult right now. I'm here to support you.",
            "anxiety": "I noticed you might be feeling worried or anxious. I'm here to listen and help if I can."
        }
        
        greeting = emotion_greetings.get(
            sentiment.emotion.value,
            "I'm here to listen and support you."
        )
        
        return f"{greeting} While I'm an AI and not a therapist, I genuinely care and want to understand what's on your mind. What's been happening?"
    
    def _fallback_response(self) -> str:
        """
        Generate fallback response when API fails.
        
        Returns:
            Template-based empathetic response
            
        Requirements: 9.4
        """
        fallback_responses = [
            "I hear you, and I want to understand better. Can you tell me more about what's going on?",
            "That sounds really difficult. What part of this feels most challenging for you right now?",
            "I'm listening. How are you feeling about all of this?",
            "Thank you for sharing that with me. What would feel most helpful to you right now?"
        ]
        
        import random
        return random.choice(fallback_responses)
