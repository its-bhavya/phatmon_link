# Instant Answer System - Logging Implementation

## Overview

This document describes the comprehensive logging and monitoring implementation for the Instant Answer Recall System. The logging system provides structured, contextual logs with performance metrics to enable effective monitoring, debugging, and optimization.

## Logging Format

All instant answer logs follow a structured format:
```
[INSTANT_ANSWER] <Operation> | key1=value1 key2=value2 ...
```

This format enables:
- Easy filtering by component (`[INSTANT_ANSWER]`, `[CLASSIFIER]`, `[SEARCH]`, `[SUMMARY]`, `[STORAGE]`, `[INDEXER]`)
- Structured parsing for log aggregation tools
- Quick identification of operations and their context

## Components and Logging

### 1. InstantAnswerService (service.py)

**Main orchestration logging:**

- **Process start**: Logs user, room, and message length
- **Classification complete**: Logs type, confidence, code detection, and duration
- **Tagging complete**: Logs topic count, keyword count, code language, and duration
- **Storage complete**: Logs storage duration
- **Question detection**: Logs confidence vs threshold
- **Search complete**: Logs result count and duration
- **Summary generation**: Logs sources, confidence, novelty, and duration
- **Total duration**: Logs end-to-end processing time

**Error logging:**
- Classification failures with fallback behavior
- Tagging failures with fallback behavior
- Storage failures (non-blocking)
- Search failures with fallback behavior
- Summary generation failures

**Example log output:**
```
[INSTANT_ANSWER] Processing message | user=alice room=Techline message_length=45
[INSTANT_ANSWER] Classification complete | type=question confidence=0.850 contains_code=False duration=0.234s
[INSTANT_ANSWER] Tagging complete | topics=2 tech_keywords=3 code_language=None duration=0.156s
[INSTANT_ANSWER] Storage complete | duration=0.089s
[INSTANT_ANSWER] Question detected | confidence=0.850 threshold=0.6
[INSTANT_ANSWER] Search complete | results_found=3 duration=0.312s
[INSTANT_ANSWER] Summary generated | sources=3 confidence=0.875 is_novel=false summary_duration=0.445s total_duration=1.236s
```

### 2. MessageClassifier (classifier.py)

**Classification logging:**

- **Start**: Logs message length and code detection
- **API timing**: Logs Gemini API call duration
- **Complete**: Logs type, confidence, code detection, API time, and total time
- **Failure**: Logs error, message preview, and duration

**Example log output:**
```
[CLASSIFIER] Starting classification | message_length=45 contains_code=False
[CLASSIFIER] Classification complete | type=question confidence=0.850 contains_code=False api_time=0.234s total_time=0.234s
```

### 3. SemanticSearchEngine (search_engine.py)

**Search logging:**

- **Start**: Logs query length, room filter, type filter, limit, and threshold
- **Embedding generated**: Logs dimensions and duration
- **ChromaDB query**: Logs raw result count and duration
- **Complete**: Logs result count, average similarity, top similarity, threshold, and total time
- **Failure**: Logs error, query preview, and duration

**Example log output:**
```
[SEARCH] Starting search | query_length=45 room=Techline type_filter=answer limit=5 min_similarity=0.7
[SEARCH] Embedding generated | dimensions=768 duration=0.123s
[SEARCH] ChromaDB query complete | raw_results=8 duration=0.089s
[SEARCH] Search complete | results=3 avg_similarity=0.825 top_similarity=0.891 threshold=0.7 total_time=0.312s
```

### 4. SummaryGenerator (summary_generator.py)

**Summary generation logging:**

- **Start**: Logs question length and search result count
- **Code extraction**: Logs number of code snippets found
- **API response**: Logs response length and API duration
- **Complete**: Logs confidence, sources, summary length, code snippets, and total time
- **Failure**: Logs error, result count, question preview, and duration

**Example log output:**
```
[SUMMARY] Starting generation | question_length=45 search_results=3
[SUMMARY] Code extraction | snippets_found=2
[SUMMARY] API response received | response_length=456 api_time=0.389s
[SUMMARY] Generation complete | confidence=0.875 sources=3 summary_length=512 code_snippets=2 total_time=0.445s
```

### 5. MessageStorageService (storage.py)

**Storage logging:**

- **Start**: Logs message ID, user, room, and type
- **Embedding generated**: Logs dimensions and duration
- **Complete**: Logs all metadata, embedding time, store time, and total time
- **Failure**: Logs error, user, room, and duration

**Example log output:**
```
[STORAGE] Starting storage | message_id=msg_abc123 user=alice room=Techline type=question
[STORAGE] Embedding generated | message_id=msg_abc123 dimensions=768 duration=0.067s
[STORAGE] Storage complete | message_id=msg_abc123 user=alice room=Techline type=question topics=2 keywords=3 embed_time=0.067s store_time=0.022s total_time=0.089s
```

### 6. MessageIndexer (indexer.py)

**Batch indexing logging:**

- **Start**: Logs room, total messages, and batch size
- **Batch progress**: Logs batch number, processed count, stored count, failed count, success rate, and batch time
- **Complete**: Logs final statistics, success rate, and total time
- **Message processing**: Logs individual message indexing with progress
- **Failures**: Logs errors with context

**Example log output:**
```
[INDEXER] Starting indexing | room=Techline total_messages=100 batch_size=10
[INDEXER] Processing batch | batch=1/10 messages=10
[INDEXER] Batch complete | batch=1/10 processed=10/100 stored=9 failed=1 success_rate=90.0% batch_time=2.345s
[INDEXER] Indexing complete | room=Techline processed=100 stored=95 failed=5 success_rate=95.0% total_time=23.456s
```

## Performance Metrics

All major operations track and log timing metrics:

1. **Classification time**: Time to classify message type
2. **Tagging time**: Time to extract tags and keywords
3. **Storage time**: Time to store message in ChromaDB
   - Embedding generation time
   - ChromaDB write time
4. **Search time**: Time to find similar messages
   - Embedding generation time
   - ChromaDB query time
5. **Summary generation time**: Time to generate AI summary
   - API call time
6. **Total end-to-end time**: Complete processing duration

## Error Context

All error logs include:

- **Error message**: The exception message
- **Context**: User, room, message preview, etc.
- **Duration**: How long the operation ran before failing
- **Stack trace**: Full exception traceback (for ERROR level)
- **Fallback behavior**: What action was taken after the error

## Log Levels

- **DEBUG**: Detailed operation steps, intermediate results
- **INFO**: Major operations, successful completions, metrics
- **WARNING**: Recoverable errors, fallback behaviors, low confidence
- **ERROR**: Unrecoverable errors, storage failures, API failures

## Monitoring Recommendations

### Key Metrics to Monitor

1. **End-to-end latency**: Total processing time per message
   - Target: < 10 seconds
   - Alert if: > 15 seconds

2. **Classification confidence**: Average confidence scores
   - Target: > 0.7
   - Alert if: < 0.5 for extended period

3. **Search result quality**: Average similarity scores
   - Target: > 0.75
   - Alert if: < 0.6 for extended period

4. **Storage success rate**: Percentage of successful stores
   - Target: > 95%
   - Alert if: < 90%

5. **Error rates**: Errors per 100 messages
   - Target: < 5%
   - Alert if: > 10%

### Log Aggregation Queries

**Average processing time:**
```
[INSTANT_ANSWER] * total_duration=* | parse "total_duration=*s" as duration | avg(duration)
```

**Classification confidence distribution:**
```
[INSTANT_ANSWER] Classification complete | parse "confidence=*" as conf | histogram(conf)
```

**Search result counts:**
```
[SEARCH] Search complete | parse "results=*" as count | avg(count)
```

**Error rate:**
```
[INSTANT_ANSWER] * error=* | count by error
```

## Requirements Validation

This logging implementation satisfies the following requirements:

- **8.1**: Logs Gemini API failures with context
- **8.2**: Logs ChromaDB failures with context
- **8.3**: Logs classification failures and fallback behavior
- **8.4**: Logs timeout handling with duration metrics
- **8.5**: Logs message preservation on any failure

All error conditions are logged with sufficient context for debugging and monitoring.
