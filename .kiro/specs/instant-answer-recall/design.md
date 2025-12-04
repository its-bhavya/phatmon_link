# Design Document: Instant Answer Recall System

## Overview

The Instant Answer Recall system is an AI-powered knowledge management feature for the Techline room that provides users with immediate, contextually relevant answers by searching historical conversations. The system operates in parallel with normal chat functionality: when a user posts a question, it automatically classifies the message, searches past conversations using semantic similarity, generates an AI summary of relevant answers, and delivers it privately to the user—while still posting the question publicly to encourage fresh perspectives and continued community engagement.

The system creates a continuously improving knowledge base by auto-tagging every message with topic tags, tech keywords, message type classification, and code presence flags. This metadata enables powerful semantic search that finds relevant answers even when wording differs from previous questions.

## Architecture

The system follows a layered architecture that integrates with the existing FastAPI backend:

```
┌─────────────────────────────────────────────────────────────┐
│                    WebSocket Handler                         │
│              (backend/main.py - websocket_endpoint)          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ├─ Message Classification
                     │  (Gemini API)
                     │
                     ├─ Semantic Search
                     │  (ChromaDB + Gemini Embeddings)
                     │
                     ├─ AI Summary Generation
                     │  (Gemini API)
                     │
                     └─ Message Storage
                        (ChromaDB with metadata)
```

### Component Layers

1. **Message Ingestion Layer**: Intercepts messages in Techline room, triggers classification
2. **Classification Layer**: Uses Gemini API to classify messages as question/answer/discussion
3. **Storage Layer**: Stores messages with embeddings and metadata in ChromaDB
4. **Search Layer**: Performs semantic search using vector similarity and metadata filters
5. **Generation Layer**: Creates AI summaries from relevant past messages
6. **Delivery Layer**: Sends private instant answers while posting questions publicly

## Components and Interfaces

### 1. InstantAnswerService

Main orchestrator that coordinates all instant answer operations.

```python
class InstantAnswerService:
    """
    Main service for instant answer recall functionality.
    
    Coordinates message classification, search, and summary generation.
    """
    
    def __init__(
        self,
        gemini_service: GeminiService,
        chroma_client: chromadb.Client,
        config: InstantAnswerConfig
    ):
        """Initialize with dependencies."""
        self.gemini_service = gemini_service
        self.classifier = MessageClassifier(gemini_service)
        self.search_engine = SemanticSearchEngine(gemini_service, chroma_client)
        self.summary_generator = SummaryGenerator(gemini_service)
        self.auto_tagger = AutoTagger(gemini_service)
        self.config = config
    
    async def process_message(
        self,
        message: str,
        user: User,
        room: str
    ) -> Optional[InstantAnswer]:
        """
        Process a message and generate instant answer if applicable.
        
        Returns InstantAnswer if question detected, None otherwise.
        """
        pass
    
    async def store_message(
        self,
        message: str,
        user: User,
        room: str,
        classification: MessageClassification,
        tags: MessageTags
    ) -> None:
        """Store message with embeddings and metadata in ChromaDB."""
        pass
```

### 2. MessageClassifier

Classifies messages using Gemini API.

```python
class MessageClassification:
    """Classification result for a message."""
    message_type: MessageType  # QUESTION, ANSWER, DISCUSSION
    confidence: float
    contains_code: bool
    reasoning: str

class MessageClassifier:
    """Classifies messages as questions, answers, or discussion."""
    
    async def classify(self, message: str) -> MessageClassification:
        """
        Classify a message using Gemini API.
        
        Returns classification with confidence score.
        """
        pass
```

### 3. SemanticSearchEngine

Performs vector search using ChromaDB and Gemini embeddings.

```python
class SearchResult:
    """Single search result from ChromaDB."""
    message_id: str
    message_text: str
    username: str
    timestamp: datetime
    similarity_score: float
    tags: MessageTags
    room: str

class SemanticSearchEngine:
    """Semantic search using ChromaDB and Gemini embeddings."""
    
    async def search(
        self,
        query: str,
        room_filter: str = "Techline",
        message_type_filter: Optional[MessageType] = MessageType.ANSWER,
        limit: int = 5,
        min_similarity: float = 0.7
    ) -> List[SearchResult]:
        """
        Search for similar messages using vector similarity.
        
        Applies metadata filters and returns ranked results.
        """
        pass
    
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding vector using Gemini API."""
        pass
```

### 4. SummaryGenerator

Generates AI summaries from search results.

```python
class InstantAnswer:
    """Generated instant answer for a question."""
    summary: str
    source_messages: List[SearchResult]
    confidence: float
    is_novel_question: bool

class SummaryGenerator:
    """Generates AI summaries from search results."""
    
    async def generate_summary(
        self,
        question: str,
        search_results: List[SearchResult]
    ) -> InstantAnswer:
        """
        Generate coherent summary from multiple search results.
        
        Preserves code snippets and includes source references.
        """
        pass
```

### 5. AutoTagger

Automatically tags messages with metadata.

```python
class MessageTags:
    """Auto-generated tags for a message."""
    topic_tags: List[str]  # e.g., ["authentication", "security"]
    tech_keywords: List[str]  # e.g., ["Python", "FastAPI", "JWT"]
    contains_code: bool
    code_language: Optional[str]  # e.g., "python", "javascript"

class AutoTagger:
    """Automatically tags messages with metadata."""
    
    async def tag_message(self, message: str) -> MessageTags:
        """
        Extract tags and metadata from message using Gemini API.
        
        Returns structured tags for storage in ChromaDB.
        """
        pass
```

### 6. ChromaDB Integration

Vector database for storing and searching message embeddings.

```python
# Collection schema in ChromaDB
{
    "id": "msg_<uuid>",
    "embedding": [0.1, 0.2, ...],  # 768-dim vector from Gemini
    "metadata": {
        "message_text": "How do I implement JWT auth?",
        "username": "alice",
        "room": "Techline",
        "timestamp": "2025-12-05T10:30:00Z",
        "message_type": "question",
        "topic_tags": ["authentication", "security"],
        "tech_keywords": ["JWT", "FastAPI"],
        "contains_code": false,
        "code_language": null
    }
}
```

## Data Models

### Message Storage Model

```python
@dataclass
class StoredMessage:
    """Message stored in ChromaDB."""
    id: str
    message_text: str
    username: str
    user_id: int
    room: str
    timestamp: datetime
    message_type: MessageType
    topic_tags: List[str]
    tech_keywords: List[str]
    contains_code: bool
    code_language: Optional[str]
    embedding: List[float]
```

### Configuration Model

```python
@dataclass
class InstantAnswerConfig:
    """Configuration for instant answer system."""
    enabled: bool = True
    target_room: str = "Techline"
    min_similarity_threshold: float = 0.7
    max_search_results: int = 5
    classification_confidence_threshold: float = 0.6
    max_summary_tokens: int = 300
    chroma_collection_name: str = "techline_messages"
    embedding_model: str = "models/embedding-001"
```

### WebSocket Message Types

```python
# New message type for instant answers
{
    "type": "instant_answer",
    "content": "Based on past discussions...",
    "sources": [
        {
            "username": "bob",
            "timestamp": "2025-12-01T15:30:00Z",
            "snippet": "You can use FastAPI's OAuth2..."
        }
    ],
    "is_novel": false,
    "timestamp": "2025-12-05T10:30:00Z"
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Question classification triggers search
*For any* message classified as a question, the semantic search should be initiated on the knowledge base
**Validates: Requirements 1.2**

### Property 2: Instant answer delivery ordering
*For any* question that generates an instant answer, the summary should be delivered to the user before the question is posted publicly
**Validates: Requirements 1.4**

### Property 3: Public posting after instant answer
*For any* message classified as a question, the original message should be posted publicly to the room after instant answer delivery (or immediately if no instant answer generated)
**Validates: Requirements 1.5, 7.3**

### Property 4: Question classification accuracy
*For any* message containing interrogative patterns (e.g., "how", "what", "why", "?"), the message classifier should tag it as a question
**Validates: Requirements 2.1**

### Property 5: Answer classification accuracy
*For any* message containing solution indicators (e.g., "you can", "try this", "here's how") and code examples, the message classifier should tag it as an answer
**Validates: Requirements 2.2**

### Property 6: Discussion classification accuracy
*For any* message containing conversational patterns without questions or solutions, the message classifier should tag it as discussion
**Validates: Requirements 2.3**

### Property 7: Classification metadata storage
*For any* classified message, retrieving it from storage should return the same classification metadata
**Validates: Requirements 2.4, 5.3**

### Property 8: Code detection accuracy
*For any* message containing code blocks (markdown fenced code or indented code), the contains_code flag should be true
**Validates: Requirements 2.5, 5.4**

### Property 9: Embedding generation for questions
*For any* message classified as a question, an embedding vector should be generated using the Gemini API
**Validates: Requirements 3.1**

### Property 10: ChromaDB query after embedding
*For any* embedding generated, a query should be executed against ChromaDB to find similar messages
**Validates: Requirements 3.2**

### Property 11: Metadata filter application
*For any* search with metadata filters (message type, topic tags, tech keywords), all returned results should match the filter criteria
**Validates: Requirements 3.3**

### Property 12: Search result ranking
*For any* search that returns multiple results, the results should be ordered by descending semantic similarity score
**Validates: Requirements 3.4**

### Property 13: Empty results for low similarity
*For any* search where no messages exceed the similarity threshold, an empty result set should be returned
**Validates: Requirements 3.5**

### Property 14: Code snippet preservation
*For any* summary generated from search results containing code, the code snippets should be preserved in the summary
**Validates: Requirements 4.2**

### Property 15: Source attribution in summaries
*For any* generated summary, references to original message timestamps and authors should be included
**Validates: Requirements 4.4**

### Property 16: Novel question indication
*For any* question where no relevant past messages are found, the is_novel_question flag should be true
**Validates: Requirements 4.5**

### Property 17: Topic tag extraction
*For any* message, topic tags should be extracted and stored in metadata
**Validates: Requirements 5.1**

### Property 18: Tech keyword extraction
*For any* message containing technology names (e.g., "Python", "React", "FastAPI"), those names should appear in tech_keywords
**Validates: Requirements 5.2**

### Property 19: Tag storage with embeddings
*For any* message with generated tags, the tags should be stored in ChromaDB alongside the embedding
**Validates: Requirements 5.5**

### Property 20: Embedding generation for all messages
*For any* message posted to Techline, an embedding should be generated for the message content
**Validates: Requirements 6.1**

### Property 21: Embedding storage with metadata
*For any* generated embedding, it should be stored in ChromaDB with message ID, timestamp, author, room, and all tags
**Validates: Requirements 6.2, 6.3**

### Property 22: Private instant answer delivery
*For any* generated instant answer, it should be sent as a private message only to the question author
**Validates: Requirements 7.1**

### Property 23: AI-generated disclaimer inclusion
*For any* instant answer delivered, it should include a disclaimer that it is AI-generated from past discussions
**Validates: Requirements 7.2**

### Property 24: Original message preservation
*For any* question posted publicly, the content and timestamp should match the original message
**Validates: Requirements 7.4**

### Property 25: Graceful degradation on Gemini API failure
*For any* message when Gemini API is unavailable, the message should be posted publicly without generating an instant answer
**Validates: Requirements 8.1**

### Property 26: Graceful degradation on ChromaDB failure
*For any* message when ChromaDB is unreachable, the message should be posted publicly normally
**Validates: Requirements 8.2**

### Property 27: Classification failure fallback
*For any* message where classification fails, the system should default to treating it as discussion and post normally
**Validates: Requirements 8.3**

### Property 28: Embedding timeout handling
*For any* message where embedding generation times out, the instant answer should be skipped and message posted normally
**Validates: Requirements 8.4**

### Property 29: Message preservation on any failure
*For any* component failure, the user's message should still be posted to the room
**Validates: Requirements 8.5**

### Property 30: Similarity threshold enforcement
*For any* search operation, no results with similarity score below the configured minimum threshold should be returned
**Validates: Requirements 9.2**

### Property 31: Maximum source messages limit
*For any* generated summary, the number of source messages should not exceed the configured maximum
**Validates: Requirements 9.3**

### Property 32: Confidence threshold application
*For any* classification with confidence below the configured threshold, the result should be treated as uncertain
**Validates: Requirements 9.4**

### Property 33: Techline room activation
*For any* message posted to the Techline room, all classification and search features should activate
**Validates: Requirements 10.1, 10.3**

### Property 34: Non-Techline room inactivity
*For any* message posted to a room other than Techline, the instant answer system should remain inactive
**Validates: Requirements 10.2**

### Property 35: Room-filtered search
*For any* search query, only messages from the Techline room should be returned
**Validates: Requirements 10.4**

### Property 36: Room identifier storage
*For any* stored message, the room identifier should be included in the metadata
**Validates: Requirements 10.5**

## Error Handling

### Error Categories

1. **Gemini API Errors**
   - Rate limiting (429)
   - Authentication failures (401)
   - Service unavailable (503)
   - Timeout errors

2. **ChromaDB Errors**
   - Connection failures
   - Collection not found
   - Query errors
   - Storage failures

3. **Classification Errors**
   - Low confidence scores
   - Malformed responses
   - Timeout during classification

4. **Search Errors**
   - Embedding generation failures
   - No results found
   - Query timeout

5. **Summary Generation Errors**
   - Empty search results
   - Generation timeout
   - Malformed output

### Error Handling Strategy

```python
class InstantAnswerError(Exception):
    """Base exception for instant answer system."""
    pass

class ClassificationError(InstantAnswerError):
    """Error during message classification."""
    pass

class SearchError(InstantAnswerError):
    """Error during semantic search."""
    pass

class SummaryError(InstantAnswerError):
    """Error during summary generation."""
    pass

# Error handling pattern
async def process_message_with_fallback(message: str, user: User, room: str):
    """Process message with graceful error handling."""
    try:
        # Attempt instant answer generation
        result = await instant_answer_service.process_message(message, user, room)
        if result:
            await send_instant_answer(user, result)
    except ClassificationError as e:
        logger.warning(f"Classification failed: {e}")
        # Continue with normal message posting
    except SearchError as e:
        logger.warning(f"Search failed: {e}")
        # Continue with normal message posting
    except SummaryError as e:
        logger.warning(f"Summary generation failed: {e}")
        # Continue with normal message posting
    except Exception as e:
        logger.error(f"Unexpected error in instant answer: {e}")
        # Always continue with normal message posting
    finally:
        # Always post the message publicly
        await post_message_to_room(message, user, room)
```

### Retry Logic

- **Gemini API calls**: 2 retries with exponential backoff (1s, 2s)
- **ChromaDB operations**: 1 retry with 500ms delay
- **Timeout values**:
  - Classification: 3 seconds
  - Embedding generation: 2 seconds
  - Search: 2 seconds
  - Summary generation: 5 seconds

### Logging

All errors are logged with context:
- User ID and username
- Message content (hashed for privacy)
- Error type and message
- Timestamp
- Room name

## Testing Strategy

### Unit Testing

Unit tests verify individual components in isolation:

1. **MessageClassifier Tests**
   - Test classification of clear questions
   - Test classification of clear answers
   - Test classification of discussion messages
   - Test code detection in messages
   - Test confidence score ranges

2. **AutoTagger Tests**
   - Test topic tag extraction
   - Test tech keyword extraction
   - Test code language detection
   - Test handling of messages without tags

3. **SemanticSearchEngine Tests**
   - Test embedding generation
   - Test similarity calculation
   - Test metadata filtering
   - Test result ranking

4. **SummaryGenerator Tests**
   - Test summary generation from single result
   - Test summary generation from multiple results
   - Test code snippet preservation
   - Test source attribution

5. **InstantAnswerService Tests**
   - Test end-to-end message processing
   - Test error handling and fallbacks
   - Test room filtering
   - Test configuration enforcement

### Property-Based Testing

Property-based tests verify universal properties using [Hypothesis](https://hypothesis.readthedocs.io/) for Python:

**Framework**: Hypothesis (Python property-based testing library)
**Configuration**: Each property test runs minimum 100 iterations

**Test Generators**:
```python
# Message generators
@st.composite
def message_strategy(draw):
    """Generate random messages with various characteristics."""
    message_type = draw(st.sampled_from(["question", "answer", "discussion"]))
    has_code = draw(st.booleans())
    tech_terms = draw(st.lists(st.sampled_from(["Python", "JavaScript", "React", "FastAPI"]), max_size=3))
    
    # Generate message based on type
    if message_type == "question":
        return generate_question(has_code, tech_terms)
    elif message_type == "answer":
        return generate_answer(has_code, tech_terms)
    else:
        return generate_discussion(has_code, tech_terms)

# Search result generators
@st.composite
def search_results_strategy(draw):
    """Generate random search results."""
    num_results = draw(st.integers(min_value=0, max_value=10))
    return [generate_search_result() for _ in range(num_results)]
```

**Property Test Implementations**:

1. **Property 1: Message classification consistency**
   - **Feature: instant-answer-recall, Property 1: Message classification consistency**
   - Generate random messages, classify twice, verify same message_type

2. **Property 2: Embedding generation determinism**
   - **Feature: instant-answer-recall, Property 2: Embedding generation determinism**
   - Generate random text, create embeddings twice, verify cosine similarity >= 0.99

3. **Property 3: Search result relevance**
   - **Feature: instant-answer-recall, Property 3: Search result relevance**
   - Generate random queries, verify all results meet similarity threshold

4. **Property 4: Metadata filter correctness**
   - **Feature: instant-answer-recall, Property 4: Metadata filter correctness**
   - Generate random searches with room filter, verify all results match filter

5. **Property 5: Summary source attribution**
   - **Feature: instant-answer-recall, Property 5: Summary source attribution**
   - Generate random search results, create summary, verify all code snippets traceable

6. **Property 6: Tag extraction completeness**
   - **Feature: instant-answer-recall, Property 6: Tag extraction completeness**
   - Generate messages with known tech terms, verify all terms in tech_keywords

7. **Property 7: Code detection accuracy**
   - **Feature: instant-answer-recall, Property 7: Code detection accuracy**
   - Generate messages with code blocks, verify contains_code flag is true

8. **Property 8: Storage-retrieval round trip**
   - **Feature: instant-answer-recall, Property 8: Storage-retrieval round trip**
   - Generate random messages, store then search, verify top result is original

9. **Property 9: Private delivery exclusivity**
   - **Feature: instant-answer-recall, Property 9: Private delivery exclusivity**
   - Generate random questions, verify instant answer sent only to author

10. **Property 10: Public question posting**
    - **Feature: instant-answer-recall, Property 10: Public question posting**
    - Generate random questions, verify original posted publicly after instant answer

11. **Property 11: Error handling graceful degradation**
    - **Feature: instant-answer-recall, Property 11: Error handling graceful degradation**
    - Inject random failures, verify message still posted normally

12. **Property 12: Room-specific activation**
    - **Feature: instant-answer-recall, Property 12: Room-specific activation**
    - Generate messages in random rooms, verify system only active in Techline

13. **Property 13: Configuration threshold enforcement**
    - **Feature: instant-answer-recall, Property 13: Configuration threshold enforcement**
    - Generate random thresholds, verify no results below threshold

14. **Property 14: Novel question detection**
    - **Feature: instant-answer-recall, Property 14: Novel question detection**
    - Generate questions with no similar history, verify is_novel_question flag

### Integration Testing

Integration tests verify component interactions:

1. **End-to-End Flow Test**
   - Post question to Techline
   - Verify classification occurs
   - Verify search executes
   - Verify summary generated
   - Verify private delivery
   - Verify public posting

2. **ChromaDB Integration Test**
   - Store messages with embeddings
   - Perform searches
   - Verify metadata filtering
   - Test collection management

3. **Gemini API Integration Test**
   - Test classification API calls
   - Test embedding generation
   - Test summary generation
   - Test error handling

4. **WebSocket Integration Test**
   - Test instant answer message delivery
   - Test public message broadcasting
   - Test room filtering

### Performance Testing

Performance tests verify system meets latency requirements:

1. **Classification Latency**: < 2 seconds
2. **Search Latency**: < 2 seconds
3. **Summary Generation Latency**: < 5 seconds
4. **Total End-to-End Latency**: < 10 seconds

### Test Coverage Goals

- Unit test coverage: > 80%
- Property test coverage: All 14 properties
- Integration test coverage: All major flows
- Error path coverage: All error handlers
