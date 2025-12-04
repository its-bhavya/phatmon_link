"""
Message Classification Service for Instant Answer Recall System.

This module provides AI-powered message classification using Gemini API to
categorize messages as questions, answers, or discussion, and detect code blocks.

Requirements: 2.1, 2.2, 2.3, 2.5
"""

import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Message type classification."""
    QUESTION = "question"
    ANSWER = "answer"
    DISCUSSION = "discussion"


@dataclass
class MessageClassification:
    """
    Classification result for a message.
    
    Attributes:
        message_type: The classified type (QUESTION, ANSWER, DISCUSSION)
        confidence: Confidence score between 0.0 and 1.0
        contains_code: Whether the message contains code blocks or snippets
        reasoning: Explanation of the classification decision
    
    Requirements: 2.1, 2.2, 2.3, 2.5
    """
    message_type: MessageType
    confidence: float
    contains_code: bool
    reasoning: str


class MessageClassifier:
    """
    Classifies messages as questions, answers, or discussion using Gemini API.
    
    This classifier analyzes message content to determine:
    - Whether it's a question (interrogative patterns, help-seeking)
    - Whether it's an answer (solutions, code examples, explanations)
    - Whether it's discussion (general commentary, conversational)
    - Whether it contains code blocks or snippets
    
    Requirements: 2.1, 2.2, 2.3, 2.5
    """
    
    def __init__(self, gemini_service):
        """
        Initialize the message classifier.
        
        Args:
            gemini_service: GeminiService instance for API calls
        """
        self.gemini_service = gemini_service
    
    async def classify(self, message: str) -> MessageClassification:
        """
        Classify a message using Gemini API.
        
        Analyzes the message to determine its type (question/answer/discussion),
        confidence level, and whether it contains code.
        
        Args:
            message: The message text to classify
        
        Returns:
            MessageClassification with type, confidence, code detection, and reasoning
        
        Raises:
            Exception: If classification fails (caller should handle gracefully)
        
        Requirements: 2.1, 2.2, 2.3, 2.5
        """
        try:
            # Detect code blocks first (independent of AI classification)
            contains_code = self._detect_code_blocks(message)
            
            # Create classification prompt
            prompt = self._create_classification_prompt(message)
            
            # Call Gemini API
            response = await self.gemini_service._generate_content(
                prompt,
                operation="message_classification"
            )
            
            # Parse the response
            message_type, confidence, reasoning = self._parse_classification_response(response)
            
            logger.info(
                f"Classified message as {message_type.value} "
                f"(confidence: {confidence:.2f}, contains_code: {contains_code})"
            )
            
            return MessageClassification(
                message_type=message_type,
                confidence=confidence,
                contains_code=contains_code,
                reasoning=reasoning
            )
        
        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise
    
    def _detect_code_blocks(self, message: str) -> bool:
        """
        Detect if message contains code blocks or snippets.
        
        Looks for:
        - Markdown fenced code blocks (```...```)
        - Inline code (`...`)
        - Indented code blocks (4+ spaces)
        - Common code patterns (function calls, operators, etc.)
        
        Args:
            message: The message text to analyze
        
        Returns:
            True if code detected, False otherwise
        
        Requirements: 2.5, 5.4
        """
        # Check for markdown fenced code blocks
        if re.search(r'```[\s\S]*?```', message):
            return True
        
        # Check for inline code (at least 3 characters to avoid false positives)
        if re.search(r'`[^`]{3,}`', message):
            return True
        
        # Check for indented code blocks (lines starting with 4+ spaces)
        lines = message.split('\n')
        indented_lines = [line for line in lines if line.startswith('    ') and line.strip()]
        if len(indented_lines) >= 2:  # At least 2 indented lines
            return True
        
        # Check for common code patterns
        code_patterns = [
            r'\b(def|class|function|const|let|var|import|from|return)\s+\w+',  # Keywords
            r'\w+\([^)]*\)\s*{',  # Function definitions
            r'\w+\([^)]*\);',  # Function calls with semicolon
            r'=>\s*{',  # Arrow functions
            r'[\w\.]+\s*=\s*[\w\.\[\]]+',  # Assignments
            r'if\s*\([^)]+\)\s*{',  # If statements
            r'for\s*\([^)]+\)\s*{',  # For loops
        ]
        
        for pattern in code_patterns:
            if re.search(pattern, message):
                return True
        
        return False
    
    def _create_classification_prompt(self, message: str) -> str:
        """
        Create the classification prompt for Gemini API.
        
        Args:
            message: The message to classify
        
        Returns:
            Formatted prompt string
        
        Requirements: 2.1, 2.2, 2.3
        """
        prompt = f"""Classify this message from a technical chat room as one of three types:

1. QUESTION - Messages that:
   - Ask for help, information, or clarification
   - Contain interrogative words (how, what, why, when, where, who)
   - End with question marks
   - Express confusion or need for assistance
   - Seek recommendations or suggestions

2. ANSWER - Messages that:
   - Provide solutions, explanations, or instructions
   - Contain code examples or technical details
   - Respond to previous questions
   - Offer guidance or recommendations
   - Use phrases like "you can", "try this", "here's how"

3. DISCUSSION - Messages that:
   - General commentary or observations
   - Conversational content without questions or solutions
   - Acknowledgments, greetings, or social interaction
   - Opinions or thoughts without seeking/providing help

Message to classify:
"{message}"

Respond in this EXACT format:
TYPE: question/answer/discussion
CONFIDENCE: 0.0-1.0
REASONING: brief explanation (one sentence)

Example 1:
TYPE: question
CONFIDENCE: 0.95
REASONING: Contains "how do I" and seeks technical help

Example 2:
TYPE: answer
CONFIDENCE: 0.88
REASONING: Provides code example and explains solution

Example 3:
TYPE: discussion
CONFIDENCE: 0.92
REASONING: General comment without question or solution
"""
        return prompt
    
    def _parse_classification_response(self, response: str) -> tuple[MessageType, float, str]:
        """
        Parse the Gemini API classification response.
        
        Args:
            response: Raw response from Gemini API
        
        Returns:
            Tuple of (message_type, confidence, reasoning)
        
        Raises:
            ValueError: If response format is invalid
        """
        lines = response.strip().split('\n')
        
        message_type = MessageType.DISCUSSION  # Default fallback
        confidence = 0.5  # Default confidence
        reasoning = "Unable to parse classification"
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('TYPE:'):
                type_str = line.split(':', 1)[1].strip().lower()
                if type_str == 'question':
                    message_type = MessageType.QUESTION
                elif type_str == 'answer':
                    message_type = MessageType.ANSWER
                elif type_str == 'discussion':
                    message_type = MessageType.DISCUSSION
            
            elif line.startswith('CONFIDENCE:'):
                try:
                    conf_str = line.split(':', 1)[1].strip()
                    confidence = float(conf_str)
                    # Clamp to valid range
                    confidence = max(0.0, min(1.0, confidence))
                except (ValueError, IndexError):
                    logger.warning(f"Failed to parse confidence: {line}")
                    confidence = 0.5
            
            elif line.startswith('REASONING:'):
                reasoning = line.split(':', 1)[1].strip()
        
        return message_type, confidence, reasoning
