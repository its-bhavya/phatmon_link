# Instant Answer Recall System - Architecture Documentation

## Overview

The Instant Answer Recall System is an AI-powered knowledge management feature that provides users with immediate, contextually relevant answers by searching historical conversations. The system operates transparently alongside normal chat functionality, automatically classifying messages, searching past conversations using semantic similarity, and delivering AI-generated summaries privately to users while still posting questions publicly to encourage community engagement.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        WebSocket Handler                         │
│                   (backend/main.py - chat_message)               │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ├─ Room Check (Techline only)
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    InstantAnswerService                          │
│              (backend/instant_answer/service.py)                 │
│                                                                   │
│  Orchestrates: Classification → Tagging → Storage → Search       │
└────────────────────┬────────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┬────────────┬────────────┐
        │            │            │            │            │
        ▼            ▼            ▼            ▼            ▼
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Classifier│  │AutoTagger│  │  Search  │  │ Summary  │  │ Storage  │
│          │  │          │  │  Engine  │  │Generator │  │ Service  │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │             │
     └─────────────┴─────────────┴─────────────┴─────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
            ┌──────────────┐         ┌──────────────┐
            │  Gemini API  │         │   ChromaDB   │
            │  (Embeddings │         │   (Vector    │
            │   & AI Gen)  │         │   Storage)   │
            └──────────────┘         └──────────────┘
```

### Component Architecture

#### 1. InstantAnswerService (Orchestrator)

**Location**: `backend/instant_answer/service.py`

**Responsibilities**:
- Coordinates all sub-services
- Implements room filtering (Techline only)
- Handles graceful error degradation
- Ensures message preservation on failures
- Enforces configuration thresholds

**Key Methods**:
```python
async def process_message(message: str, user: User, room: str) -> Optional[InstantAnswer]
    # 1. Check if enabled and room matches
    # 2. Classify message type
    # 3. Tag message with metadata
    # 4. Store message in ChromaDB
    # 5. If question, search and generate instant answer
    # 6. Return instant answer or None
```

**Error Handling**:
- Classification failure → Default to DISCUSSION type
- Tagging failure → Use empty tags
- Storage failure → Log error, continue processing
- Search failure → Return empty results (novel question)
- Summary failure → Return None (no instant answer)

#### 2. MessageClassifier

**Location**: `backend/instant_answer/classifier.py`

**Responsibilities**:
- Classifies messages as QUESTION, ANSWER, or DISCUSSION
- Detects code blocks in messages
- Provides confidence scores
- Uses Gemini API for classification

**Data Model**:
```python
class MessageClassification:
    message_type: MessageType  # QUESTION, ANSWER, DISCUSSION
    confidence: float          # 0.0 - 1.0
    contains_code: bool
    reasoning: str
```

**Classification Logic**:
- Questions: Interrogative patterns, help-seeking language
- Answers: Solution indicators, code examples, explanatory content
- Discussion: General commentary, conversational content

#### 3. AutoTagger

**Location**: `backend/instant_answer/tagger.py`

**Responsibilities**:
- Extracts topic tags from messages
- Identifies tech keywords (Python, FastAPI, React, etc.)
- Detects code language
- Uses Gemini API for tag extraction

**Data Model**:
```python
class MessageTags:
    topic_tags: List[str]        # ["authentication", "security"]
    tech_keywords: List[str]     # ["Python", "FastAPI", "JWT"]
    contains_code: bool
    code_language: Optional[str] # "python", "javascript", etc.
```

#### 4. SemanticSearchEngine

**Location**: `backend/instant_answer/search_engine.py`

**Responsibilities**:
- Generates embeddings using Gemini API
- Performs vector similarity search in ChromaDB
- Applies metadata filters (room, message type, tags)
- Ranks results by similarity score
- Filters by similarity threshold

**Data Model**:
```python
class SearchResult:
    message_id: str
    message_text: str
    username: str
    timestamp: datetime
    similarity_score: float  # 0.0 - 1.0
    tags: MessageTags
    room: str
```

**Search Process**:
1. Generate embedding for query (768-dim vector)
2. Query ChromaDB for similar vectors
3. Apply metadata filters (room, message type)
4. Rank by similarity score (descending)
5. Filter by minimum similarity threshold
6. Return top N results

#### 5. SummaryGenerator

**Location**: `backend/instant_answer/summary_generator.py`

**Responsibilities**:
- Generates coherent summaries from search results
- Preserves code snippets
- Adds source attribution (authors, timestamps)
- Detects novel questions
- Calculates confidence scores

**Data Model**:
```python
class InstantAnswer:
    summary: str
    source_messages: List[SearchResult]
    confidence: float
    is_novel_question: bool
```

**Summary Generation**:
- Uses Gemini API with custom prompt
- Includes top 5 search results as context
- Preserves markdown code blocks
- Appends source attribution section
- Confidence based on similarity scores and result count

#### 6. MessageStorageService

**Location**: `backend/instant_answer/storage.py`

**Responsibilities**:
- Stores messages with embeddings in ChromaDB
- Stores all metadata (classification, tags, room)
- Handles batch storage for efficiency
- Provides message retrieval by ID

**Storage Schema**:
```python
{
    "id": "msg_<uuid>",
    "embedding": [0.1, 0.2, ...],  # 768-dim vector
    "metadata": {
        "message_text": "How do I implement JWT auth?",
        "username": "alice",
        "user_id": 1,
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

### Data Flow

#### Message Processing Flow

```
1. User posts message in Techline
   ↓
2. WebSocket handler receives message
   ↓
3. InstantAnswerService.process_message() called
   ↓
4. MessageClassifier classifies message type
   ↓
5. AutoTagger extracts tags and keywords
   ↓
6. MessageStorageService stores with embedding
   ↓
7. If QUESTION:
   a. SemanticSearchEngine searches ChromaDB
   b. SummaryGenerator creates summary
   c. Return InstantAnswer
   ↓
8. WebSocket handler sends instant answer privately
   ↓
9. WebSocket handler posts question publicly
```

#### Search Flow

```
1. Question detected
   ↓
2. Generate embedding for question
   ↓
3. Query ChromaDB with filters:
   - room = "Techline"
   - message_type = "ANSWER"
   - similarity > threshold
   ↓
4. Rank results by similarity
   ↓
5. Return top N results
   ↓
6. Generate summary from results
```

### External Dependencies

#### Gemini API

**Purpose**: AI classification, tagging, embeddings, and summary generation

**Models Used**:
- `gemini-2.0-flash`: Classification, tagging, summary generation
- `models/embedding-001`: Embedding generation (768 dimensions)

**API Calls Per Message**:
- Classification: 1 call
- Tagging: 1 call
- Embedding: 1 call
- Summary (if question): 1 call
- **Total**: 3-4 calls per message

**Rate Limits**: Handled with retry logic (2 retries with exponential backoff)

#### ChromaDB

**Purpose**: Vector database for storing and searching message embeddings

**Configuration**:
- Host: Configurable (default: localhost)
- Port: Configurable (default: 8001)
- Collection: `techline_messages`

**Operations**:
- Insert: Store message with embedding and metadata
- Query: Vector similarity search with metadata filters
- Update: Update message embeddings (for edits)
- Delete: Remove messages (for deletions)

**Performance**:
- Embedding generation: ~100-200ms
- Vector search: ~50-100ms
- Total search time: ~200-300ms

### Configuration

**Location**: `backend/instant_answer/config.py`

**Configuration Model**:
```python
class InstantAnswerConfig:
    enabled: bool = True
    target_room: str = "Techline"
    min_similarity_threshold: float = 0.7
    max_search_results: int = 5
    classification_confidence_threshold: float = 0.6
    max_summary_tokens: int = 300
    chroma_collection_name: str = "techline_messages"
    embedding_model: str = "models/embedding-001"
```

**Environment Variables**:
- `INSTANT_ANSWER_ENABLED`: Enable/disable system
- `INSTANT_ANSWER_MIN_SIMILARITY`: Similarity threshold (0.0-1.0)
- `INSTANT_ANSWER_MAX_RESULTS`: Max search results (1-10)
- `INSTANT_ANSWER_CONFIDENCE_THRESHOLD`: Classification confidence (0.0-1.0)
- `INSTANT_ANSWER_MAX_SUMMARY_TOKENS`: Max summary length
- `CHROMADB_HOST`: ChromaDB hostname
- `CHROMADB_PORT`: ChromaDB port
- `CHROMADB_COLLECTION_NAME`: Collection name
- `INSTANT_ANSWER_TARGET_ROOM`: Target room name

### Error Handling Strategy

#### Error Categories

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

#### Fallback Behaviors

| Component | Failure Mode | Fallback Behavior |
|-----------|--------------|-------------------|
| Classification | API error | Default to DISCUSSION |
| Tagging | API error | Empty tags |
| Storage | ChromaDB error | Log error, continue |
| Search | API/DB error | Empty results |
| Summary | API error | No instant answer |

**Critical Principle**: Message preservation is guaranteed. Even if all AI processing fails, the user's message is always posted to the room.

#### Retry Logic

- **Gemini API calls**: 2 retries with exponential backoff (1s, 2s)
- **ChromaDB operations**: 1 retry with 500ms delay
- **Timeout values**:
  - Classification: 3 seconds
  - Embedding generation: 2 seconds
  - Search: 2 seconds
  - Summary generation: 5 seconds

### Security Considerations

1. **Privacy**:
   - Instant answers sent privately only to question author
   - No message content logged (only hashed IDs)
   - ChromaDB access restricted to application

2. **Rate Limiting**:
   - Existing chat rate limits apply
   - No additional rate limits for instant answers
   - Gemini API rate limits handled with retries

3. **Input Validation**:
   - Room name validation
   - Message content sanitization
   - Metadata validation before storage

4. **Access Control**:
   - Only authenticated users can trigger instant answers
   - ChromaDB not exposed to public
   - Gemini API key stored securely in environment

### Performance Characteristics

#### Latency

- **Classification**: ~500-1000ms
- **Tagging**: ~500-1000ms
- **Embedding**: ~100-200ms
- **Search**: ~50-100ms
- **Summary**: ~1000-2000ms
- **Total (question)**: ~2-5 seconds
- **Total (non-question)**: ~1-2 seconds

#### Throughput

- **Messages per second**: ~10-20 (limited by Gemini API)
- **Concurrent users**: Limited by WebSocket capacity (~10,000)
- **ChromaDB capacity**: Millions of messages

#### Scalability

**Current Limitations**:
- Single Gemini API key (rate limited)
- Single ChromaDB instance
- In-memory service state

**Future Scaling Options**:
- Multiple Gemini API keys with load balancing
- ChromaDB clustering for high availability
- Redis for distributed caching
- Message queue for async processing

### Monitoring and Observability

#### Logging

All operations are logged with structured logging:

```python
logger.info("Processing message", extra={
    "user_id": user.user_id,
    "room": room,
    "message_type": classification.message_type,
    "confidence": classification.confidence
})
```

**Log Levels**:
- INFO: Normal operations (classification, search, summary)
- WARNING: Fallback behaviors (classification failure, empty results)
- ERROR: Unexpected errors (API failures, storage errors)

#### Metrics

Key metrics to monitor:

- Classification success rate
- Search result counts
- Summary generation success rate
- Average latency per component
- Error rates by type
- ChromaDB collection size

### Testing Strategy

#### Unit Tests

- Individual component testing with mocks
- 80%+ code coverage
- Fast execution (<5 seconds)

#### Integration Tests

- End-to-end flows with real APIs
- ChromaDB integration
- WebSocket integration

#### Property-Based Tests

- Using Hypothesis framework
- 100+ iterations per property
- Tests universal properties across random inputs

**Test Coverage**:
- 50+ unit tests
- 20+ integration tests
- 14 property-based tests

### Deployment Considerations

#### Prerequisites

1. **ChromaDB**: Must be running and accessible
2. **Gemini API Key**: Valid API key with sufficient quota
3. **Database**: SQLite or PostgreSQL for message storage
4. **Python 3.11+**: Required for async/await features

#### Startup Sequence

1. Load configuration from environment
2. Initialize Gemini service
3. Connect to ChromaDB
4. Create/verify collection
5. Initialize InstantAnswerService
6. (Optional) Index historical messages
7. Start WebSocket handler

#### Health Checks

Monitor these endpoints/services:

- ChromaDB connection: `GET http://chromadb:8001/api/v1/heartbeat`
- Gemini API: Test embedding generation
- Message storage: Test insert/query operations

#### Backup and Recovery

**ChromaDB Backup**:
- Regular backups of ChromaDB data directory
- Export collection to JSON for portability
- Test restore procedures

**Message History**:
- Primary source: SQLite/PostgreSQL database
- ChromaDB can be rebuilt from message history
- Use indexing scripts for recovery

### Future Enhancements

1. **Multi-Room Support**: Extend beyond Techline
2. **User Feedback**: Allow users to rate instant answers
3. **Learning**: Improve search based on user feedback
4. **Caching**: Cache frequent queries for faster responses
5. **Analytics**: Track usage patterns and effectiveness
6. **Personalization**: Tailor answers based on user history
7. **Multi-Language**: Support non-English conversations

## Related Documentation

- **User Guide**: `USER_GUIDE_INSTANT_ANSWER.md`
- **Configuration**: `backend/CONFIG.md`
- **Troubleshooting**: `TROUBLESHOOTING_INSTANT_ANSWER.md`
- **ChromaDB Setup**: `CHROMADB_SETUP.md`
- **Indexing Guide**: `backend/instant_answer/INDEXING_GUIDE.md`
- **Service Implementation**: `backend/instant_answer/SERVICE_IMPLEMENTATION.md`
- **Search Engine**: `backend/instant_answer/SEARCH_ENGINE_IMPLEMENTATION.md`
- **Summary Generator**: `backend/instant_answer/SUMMARY_GENERATOR_IMPLEMENTATION.md`

## Conclusion

The Instant Answer Recall System provides a sophisticated AI-powered knowledge management solution that enhances user experience without disrupting normal chat functionality. The architecture is designed for reliability, with comprehensive error handling and graceful degradation ensuring that chat functionality is never compromised by AI processing failures.
