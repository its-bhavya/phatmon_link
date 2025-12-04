"""
Auto-Tagging Service for Instant Answer Recall System.

This module provides AI-powered automatic tagging using Gemini API to
extract topic tags, tech keywords, and code language from messages.

Requirements: 5.1, 5.2, 5.4
"""

import logging
import re
from dataclasses import dataclass
from typing import Optional, List

logger = logging.getLogger(__name__)


@dataclass
class MessageTags:
    """
    Auto-generated tags for a message.
    
    Attributes:
        topic_tags: General topic tags (e.g., ["authentication", "security"])
        tech_keywords: Technology names and frameworks (e.g., ["Python", "FastAPI", "JWT"])
        contains_code: Whether the message contains code blocks or snippets
        code_language: Detected programming language (e.g., "python", "javascript")
    
    Requirements: 5.1, 5.2, 5.4
    """
    topic_tags: List[str]
    tech_keywords: List[str]
    contains_code: bool
    code_language: Optional[str]


class AutoTagger:
    """
    Automatically tags messages with metadata using Gemini API.
    
    This tagger extracts:
    - Topic tags: General subject matter (authentication, debugging, deployment)
    - Tech keywords: Specific technologies (Python, React, Docker, AWS)
    - Code language: Programming language if code is present
    
    Requirements: 5.1, 5.2, 5.4
    """
    
    def __init__(self, gemini_service):
        """
        Initialize the auto-tagger.
        
        Args:
            gemini_service: GeminiService instance for API calls
        """
        self.gemini_service = gemini_service
    
    async def tag_message(self, message: str) -> MessageTags:
        """
        Extract tags and metadata from message using Gemini API.
        
        Analyzes the message to extract:
        - Topic tags (general subjects)
        - Tech keywords (specific technologies)
        - Code language (if code is present)
        
        Args:
            message: The message text to tag
        
        Returns:
            MessageTags with extracted tags and metadata
        
        Raises:
            Exception: If tagging fails (caller should handle gracefully)
        
        Requirements: 5.1, 5.2, 5.4
        """
        try:
            # Detect code blocks and language first
            contains_code = self._detect_code_blocks(message)
            code_language = self._detect_code_language(message) if contains_code else None
            
            # Create tagging prompt
            prompt = self._create_tagging_prompt(message)
            
            # Call Gemini API
            response = await self.gemini_service._generate_content(
                prompt,
                operation="message_tagging"
            )
            
            # Parse the response
            topic_tags, tech_keywords = self._parse_tagging_response(response)
            
            logger.info(
                f"Tagged message with {len(topic_tags)} topics, "
                f"{len(tech_keywords)} tech keywords, "
                f"code_language: {code_language}"
            )
            
            return MessageTags(
                topic_tags=topic_tags,
                tech_keywords=tech_keywords,
                contains_code=contains_code,
                code_language=code_language
            )
        
        except Exception as e:
            logger.error(f"Tagging failed: {e}")
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
        
        Requirements: 5.4
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
    
    def _detect_code_language(self, message: str) -> Optional[str]:
        """
        Detect programming language from code blocks.
        
        Looks for:
        - Markdown fenced code blocks with language specifier
        - Language-specific syntax patterns
        
        Args:
            message: The message text to analyze
        
        Returns:
            Detected language name (lowercase) or None
        
        Requirements: 5.4
        """
        # Check for markdown fenced code blocks with language specifier
        fenced_match = re.search(r'```(\w+)', message)
        if fenced_match:
            lang = fenced_match.group(1).lower()
            # Normalize common language names
            lang_map = {
                'py': 'python',
                'js': 'javascript',
                'ts': 'typescript',
                'rb': 'ruby',
                'sh': 'bash',
                'yml': 'yaml',
            }
            return lang_map.get(lang, lang)
        
        # Pattern-based language detection
        language_patterns = {
            'python': [
                r'\bdef\s+\w+\s*\(',
                r'\bimport\s+\w+',
                r'\bfrom\s+\w+\s+import',
                r'@\w+\s*\n\s*def',  # Decorators
            ],
            'javascript': [
                r'\bfunction\s+\w+\s*\(',
                r'\bconst\s+\w+\s*=',
                r'\blet\s+\w+\s*=',
                r'=>\s*{',
                r'console\.log\(',
            ],
            'typescript': [
                r':\s*(string|number|boolean|any)\s*[=;]',
                r'interface\s+\w+\s*{',
                r'type\s+\w+\s*=',
            ],
            'java': [
                r'\bpublic\s+class\s+\w+',
                r'\bprivate\s+\w+\s+\w+',
                r'System\.out\.println\(',
            ],
            'go': [
                r'\bfunc\s+\w+\s*\(',
                r'\bpackage\s+\w+',
                r':=\s*',
            ],
            'rust': [
                r'\bfn\s+\w+\s*\(',
                r'\blet\s+mut\s+',
                r'println!\(',
            ],
            'sql': [
                r'\bSELECT\s+.*\s+FROM\s+',
                r'\bINSERT\s+INTO\s+',
                r'\bUPDATE\s+.*\s+SET\s+',
                r'\bCREATE\s+TABLE\s+',
            ],
        }
        
        # Count pattern matches for each language
        scores = {}
        for lang, patterns in language_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, message, re.IGNORECASE))
            if score > 0:
                scores[lang] = score
        
        # Return language with highest score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return None
    
    def _create_tagging_prompt(self, message: str) -> str:
        """
        Create the tagging prompt for Gemini API.
        
        Args:
            message: The message to tag
        
        Returns:
            Formatted prompt string
        
        Requirements: 5.1, 5.2
        """
        prompt = f"""Extract topic tags and technology keywords from this technical chat message.

Message:
"{message}"

Extract:
1. TOPIC TAGS - General subject matter (2-5 tags)
   Examples: authentication, debugging, deployment, performance, security, testing, database, api, frontend, backend

2. TECH KEYWORDS - Specific technologies, frameworks, languages, tools mentioned
   Examples: Python, JavaScript, React, FastAPI, Docker, AWS, PostgreSQL, Redis, Git, JWT

Guidelines:
- Use lowercase for all tags and keywords
- Be specific but not overly granular
- Only include technologies explicitly mentioned or clearly implied
- If no clear topics/technologies, return empty lists

Respond in this EXACT format:
TOPICS: tag1, tag2, tag3
TECH: keyword1, keyword2, keyword3

Example 1:
Message: "How do I implement JWT authentication in FastAPI?"
TOPICS: authentication, security, api
TECH: jwt, fastapi, python

Example 2:
Message: "My React app is slow when rendering large lists"
TOPICS: performance, frontend, debugging
TECH: react, javascript

Example 3:
Message: "Thanks for the help!"
TOPICS: 
TECH: 
"""
        return prompt
    
    def _parse_tagging_response(self, response: str) -> tuple[List[str], List[str]]:
        """
        Parse the Gemini API tagging response.
        
        Args:
            response: Raw response from Gemini API
        
        Returns:
            Tuple of (topic_tags, tech_keywords)
        """
        lines = response.strip().split('\n')
        
        topic_tags = []
        tech_keywords = []
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('TOPICS:'):
                tags_str = line.split(':', 1)[1].strip()
                if tags_str:
                    # Split by comma and clean up
                    topic_tags = [
                        tag.strip().lower() 
                        for tag in tags_str.split(',') 
                        if tag.strip()
                    ]
            
            elif line.startswith('TECH:'):
                tech_str = line.split(':', 1)[1].strip()
                if tech_str:
                    # Split by comma and clean up
                    tech_keywords = [
                        keyword.strip().lower() 
                        for keyword in tech_str.split(',') 
                        if keyword.strip()
                    ]
        
        # Deduplicate while preserving order
        topic_tags = list(dict.fromkeys(topic_tags))
        tech_keywords = list(dict.fromkeys(tech_keywords))
        
        return topic_tags, tech_keywords
