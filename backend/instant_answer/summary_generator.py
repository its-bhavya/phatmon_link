"""
AI Summary Generator for Instant Answer Recall System.

This module provides AI-powered summary generation using Gemini API to
create coherent summaries from multiple search results, preserving code
snippets and including source attribution.

Requirements: 4.2, 4.4, 4.5
"""

import logging
import re
from dataclasses import dataclass
from typing import List

from backend.instant_answer.search_engine import SearchResult

logger = logging.getLogger(__name__)


@dataclass
class InstantAnswer:
    """
    Generated instant answer for a question.
    
    Attributes:
        summary: The AI-generated summary text
        source_messages: List of SearchResult objects used to generate summary
        confidence: Confidence score for the summary (0.0-1.0)
        is_novel_question: Whether this is a novel question with no relevant history
    
    Requirements: 4.2, 4.4, 4.5
    """
    summary: str
    source_messages: List[SearchResult]
    confidence: float
    is_novel_question: bool


class SummaryGenerator:
    """
    Generates AI summaries from search results using Gemini API.
    
    This generator creates coherent summaries that:
    - Combine insights from multiple past messages
    - Preserve code snippets from relevant answers
    - Include source attribution (timestamps and authors)
    - Detect novel questions with no relevant history
    
    Requirements: 4.2, 4.4, 4.5
    """
    
    def __init__(self, gemini_service, max_summary_tokens: int = 300):
        """
        Initialize the summary generator.
        
        Args:
            gemini_service: GeminiService instance for API calls
            max_summary_tokens: Maximum tokens for generated summaries
        """
        self.gemini_service = gemini_service
        self.max_summary_tokens = max_summary_tokens
    
    async def generate_summary(
        self,
        question: str,
        search_results: List[SearchResult]
    ) -> InstantAnswer:
        """
        Generate coherent summary from multiple search results.
        
        This method:
        1. Checks if there are relevant search results
        2. Extracts key insights and code snippets from results
        3. Generates a coherent summary using Gemini API
        4. Preserves code snippets in the summary
        5. Includes source attribution (authors and timestamps)
        6. Detects novel questions (no relevant results)
        
        Args:
            question: The user's question
            search_results: List of SearchResult objects from semantic search
        
        Returns:
            InstantAnswer with summary, sources, confidence, and novelty flag
        
        Raises:
            Exception: If summary generation fails (caller should handle gracefully)
        
        Requirements: 4.2, 4.4, 4.5
        """
        try:
            # Check if this is a novel question (no relevant results)
            if not search_results:
                logger.info("Novel question detected - no relevant search results")
                return InstantAnswer(
                    summary="This appears to be a novel question! No similar discussions found in the history.",
                    source_messages=[],
                    confidence=1.0,
                    is_novel_question=True
                )
            
            # Extract code snippets from search results
            code_snippets = self._extract_code_snippets(search_results)
            
            # Create summary prompt
            prompt = self._create_summary_prompt(question, search_results, code_snippets)
            
            # Call Gemini API
            logger.info(f"Generating summary from {len(search_results)} search results")
            response = await self.gemini_service._generate_content(
                prompt,
                operation="summary_generation"
            )
            
            # Add source attribution
            summary_with_sources = self._add_source_attribution(response, search_results)
            
            # Calculate confidence based on search result quality
            confidence = self._calculate_confidence(search_results)
            
            logger.info(
                f"Generated summary with confidence {confidence:.2f} "
                f"from {len(search_results)} sources"
            )
            
            return InstantAnswer(
                summary=summary_with_sources,
                source_messages=search_results,
                confidence=confidence,
                is_novel_question=False
            )
        
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            raise
    
    def _extract_code_snippets(self, search_results: List[SearchResult]) -> List[str]:
        """
        Extract code snippets from search results.
        
        Looks for:
        - Markdown fenced code blocks (```...```)
        - Inline code (`...`)
        - Indented code blocks
        
        Args:
            search_results: List of SearchResult objects
        
        Returns:
            List of extracted code snippet strings
        
        Requirements: 4.2
        """
        code_snippets = []
        
        for result in search_results:
            message = result.message_text
            
            # Extract fenced code blocks
            fenced_blocks = re.findall(r'```[\s\S]*?```', message)
            code_snippets.extend(fenced_blocks)
            
            # Extract inline code (at least 10 characters to avoid false positives)
            inline_code = re.findall(r'`[^`]{10,}`', message)
            code_snippets.extend(inline_code)
        
        return code_snippets
    
    def _create_summary_prompt(
        self,
        question: str,
        search_results: List[SearchResult],
        code_snippets: List[str]
    ) -> str:
        """
        Create the summary generation prompt for Gemini API.
        
        Args:
            question: The user's question
            search_results: List of SearchResult objects
            code_snippets: Extracted code snippets
        
        Returns:
            Formatted prompt string
        
        Requirements: 4.2, 4.4
        """
        # Build context from search results
        context_messages = []
        for i, result in enumerate(search_results[:5], 1):  # Limit to top 5
            context_messages.append(
                f"Message {i} (by {result.username}, similarity: {result.similarity_score:.2f}):\n"
                f"{result.message_text}\n"
            )
        
        context = "\n".join(context_messages)
        
        # Build code snippets section
        code_section = ""
        if code_snippets:
            code_section = "\n\nCode snippets found in past answers:\n" + "\n".join(code_snippets[:3])
        
        prompt = f"""You are helping answer a technical question by summarizing relevant past discussions.

User's Question:
"{question}"

Relevant Past Messages:
{context}
{code_section}

Generate a helpful, coherent summary that:
1. Directly answers the user's question based on the past messages
2. Combines insights from multiple sources into a unified response
3. PRESERVES any code snippets exactly as they appear (use markdown code blocks)
4. Keeps the response concise (2-3 paragraphs maximum)
5. Uses a helpful, friendly tone
6. Focuses on actionable information

Do NOT mention "past messages" or "previous discussions" - write as if you're directly answering.
Do NOT add phrases like "Based on the search results" - just provide the answer.
If code snippets are relevant, include them in your response.

Generate the summary now:
"""
        return prompt
    
    def _add_source_attribution(
        self,
        summary: str,
        search_results: List[SearchResult]
    ) -> str:
        """
        Add source attribution to the summary.
        
        Appends a section listing the original message authors and timestamps
        that were used to generate the summary.
        
        Args:
            summary: The generated summary text
            search_results: List of SearchResult objects used
        
        Returns:
            Summary with source attribution appended
        
        Requirements: 4.4
        """
        if not search_results:
            return summary
        
        # Build source list
        sources = []
        for result in search_results[:5]:  # Limit to top 5 sources
            timestamp_str = result.timestamp.strftime("%Y-%m-%d %H:%M")
            sources.append(f"- {result.username} ({timestamp_str})")
        
        source_section = "\n\n---\n**Sources:**\n" + "\n".join(sources)
        
        return summary + source_section
    
    def _calculate_confidence(self, search_results: List[SearchResult]) -> float:
        """
        Calculate confidence score for the summary.
        
        Confidence is based on:
        - Number of search results
        - Average similarity score
        - Presence of code in results
        
        Args:
            search_results: List of SearchResult objects
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not search_results:
            return 0.0
        
        # Average similarity score
        avg_similarity = sum(r.similarity_score for r in search_results) / len(search_results)
        
        # Bonus for multiple results
        result_count_factor = min(len(search_results) / 5.0, 1.0)
        
        # Bonus for code presence
        has_code = any(r.tags.contains_code for r in search_results)
        code_bonus = 0.1 if has_code else 0.0
        
        # Combine factors
        confidence = (avg_similarity * 0.7) + (result_count_factor * 0.2) + code_bonus
        
        # Clamp to valid range
        return max(0.0, min(1.0, confidence))
