# Background Message Indexing Guide

## Overview

The background message indexing feature allows you to process and store historical chat messages into ChromaDB for semantic search. This is useful for:

- Indexing existing message history when first deploying the Instant Answer system
- Re-indexing messages after system updates
- Backfilling the knowledge base with historical conversations

## Features

- **Batch Processing**: Messages are processed in configurable batches for efficiency
- **Progress Logging**: Detailed logging of indexing progress and statistics
- **Error Handling**: Graceful handling of classification, tagging, and storage failures
- **Message Filtering**: Automatically skips system messages and empty content
- **Automatic Startup Indexing**: Optional automatic indexing on application startup

## Configuration

### Environment Variables

Add these to your `.env` file:

```bash
# Enable/disable automatic indexing on startup
INSTANT_ANSWER_AUTO_INDEX_ON_STARTUP=false

# Target room to index (default: Techline)
INSTANT_ANSWER_TARGET_ROOM=Techline
```

### Automatic Indexing on Startup

To enable automatic indexing when the application starts:

1. Set `INSTANT_ANSWER_AUTO_INDEX_ON_STARTUP=true` in your `.env` file
2. Restart the application
3. Check logs for indexing progress

**Note**: This will index up to 1000 recent messages from the target room.

## Manual Indexing

### Via API Endpoint

You can trigger indexing manually using the API endpoint:

```bash
POST /api/instant-answer/index?token=YOUR_JWT_TOKEN&room=Techline
```

**Parameters**:
- `token` (required): Valid JWT authentication token
- `room` (optional): Room name to index (default: "Techline")

**Example using curl**:

```bash
curl -X POST "http://localhost:8000/api/instant-answer/index?token=YOUR_TOKEN&room=Techline"
```

**Response**:

```json
{
  "status": "indexing_started",
  "room": "Techline",
  "message": "Background indexing started for room 'Techline'"
}
```

### Programmatically

You can also trigger indexing programmatically:

```python
from backend.instant_answer.indexer import index_historical_messages

# In an async context
stats = await index_historical_messages(
    instant_answer_service=app.state.instant_answer_service,
    room_service=app.state.room_service,
    target_room="Techline",
    batch_size=10
)

print(f"Indexed {stats['stored']}/{stats['processed']} messages")
```

## How It Works

### Processing Pipeline

1. **Fetch Messages**: Retrieves up to 1000 recent messages from room history
2. **Filter Messages**: Skips system messages, errors, and empty content
3. **Classify**: Uses Gemini API to classify message type (question/answer/discussion)
4. **Tag**: Extracts topic tags, tech keywords, and code information
5. **Generate Embedding**: Creates vector embedding using Gemini API
6. **Store**: Saves message with metadata and embedding to ChromaDB

### Batch Processing

Messages are processed in batches (default: 10 messages per batch) to:
- Reduce memory usage
- Provide incremental progress updates
- Allow for better error recovery

### Error Handling

The indexer handles errors gracefully:

- **Classification Failures**: Falls back to "DISCUSSION" type
- **Tagging Failures**: Uses empty tags
- **Storage Failures**: Logs error and continues with next message
- **Invalid Messages**: Skips and counts as failed

## Monitoring

### Log Output

The indexer provides detailed logging:

```
INFO: Starting indexing for room 'Techline' (150 messages)
INFO: Processing batch 1/15 (10 messages)
INFO: Progress: 10/150 processed, 9 stored, 1 failed
INFO: Processing batch 2/15 (10 messages)
INFO: Progress: 20/150 processed, 18 stored, 2 failed
...
INFO: Indexing complete for room 'Techline': 145/150 messages stored successfully
```

### Statistics

After indexing completes, you'll receive statistics:

```python
{
    "processed": 150,  # Total messages processed
    "stored": 145,     # Successfully stored in ChromaDB
    "failed": 5        # Failed to process/store
}
```

## Performance Considerations

### Batch Size

- **Smaller batches (5-10)**: More frequent progress updates, lower memory usage
- **Larger batches (20-50)**: Faster overall processing, higher memory usage

Adjust based on your needs:

```python
await index_historical_messages(
    instant_answer_service=service,
    room_service=room_service,
    target_room="Techline",
    batch_size=20  # Adjust this value
)
```

### API Rate Limits

The indexer makes Gemini API calls for:
- Message classification (1 call per message)
- Message tagging (1 call per message)
- Embedding generation (1 call per message)

**Total**: ~3 API calls per message

For 100 messages, expect ~300 API calls. Consider Gemini API rate limits when indexing large message histories.

### Processing Time

Approximate processing times:
- 10 messages: ~30-60 seconds
- 100 messages: ~5-10 minutes
- 1000 messages: ~50-100 minutes

Times vary based on:
- API response times
- Network latency
- Batch size
- Message complexity

## Troubleshooting

### No Messages Indexed

**Problem**: Statistics show 0 stored messages

**Solutions**:
1. Check that the room exists and has messages
2. Verify ChromaDB is running and accessible
3. Check Gemini API key is valid
4. Review logs for specific errors

### Slow Indexing

**Problem**: Indexing takes too long

**Solutions**:
1. Increase batch size for faster processing
2. Check network connectivity to Gemini API
3. Verify ChromaDB performance
4. Consider indexing during off-peak hours

### High Failure Rate

**Problem**: Many messages fail to index

**Solutions**:
1. Check Gemini API quota and rate limits
2. Verify ChromaDB connection is stable
3. Review error logs for specific failure patterns
4. Ensure messages have valid content

### Memory Issues

**Problem**: Application runs out of memory

**Solutions**:
1. Reduce batch size
2. Index in smaller chunks (fewer messages at a time)
3. Increase available memory
4. Process messages during low-traffic periods

## Best Practices

1. **Initial Indexing**: Run during off-peak hours or before launch
2. **Regular Updates**: Messages are indexed automatically as they arrive
3. **Re-indexing**: Only needed after system updates or data corruption
4. **Monitoring**: Watch logs during indexing to catch issues early
5. **Testing**: Test with small message sets first

## Requirements

This feature implements requirements:
- 6.1: Message embedding generation
- 6.2: Message storage with metadata
- 6.3: ChromaDB integration
