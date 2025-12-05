# Quick Start: Indexing Historical Messages

## Prerequisites

1. **Start ChromaDB server**:
   ```cmd
   start_chromadb.bat
   ```
   Keep this terminal open.

2. **Verify environment variables** in `.env`:
   ```bash
   GEMINI_API_KEY=your_key_here
   CHROMADB_HOST=localhost
   CHROMADB_PORT=8001
   INSTANT_ANSWER_ENABLED=true
   ```

## Index Messages

### Fast Indexing (Recommended)

For large message histories (100+ messages):

```cmd
python index_historical_messages.py --fast --room Techline --limit 1000
```

This uses:
- Parallel batch embedding (10-15x faster)
- Bulk ChromaDB inserts
- 10 parallel workers

### Standard Indexing

For small datasets or testing:

```cmd
python index_historical_messages.py --room Techline --limit 100
```

## Options

- `--fast` - Use parallel batch processing (recommended)
- `--room ROOM_NAME` - Room to index (default: Techline)
- `--limit N` - Max messages to index (default: 1000)

## What Gets Indexed

For each message, the system:
1. ✓ Classifies type (question/answer/discussion)
2. ✓ Extracts topic tags and tech keywords
3. ✓ Detects code blocks and language
4. ✓ Generates vector embedding
5. ✓ Stores in ChromaDB with metadata

## Performance

**Fast indexing speeds**:
- 100 messages: ~1-2 minutes
- 500 messages: ~3-5 minutes
- 1000 messages: ~5-10 minutes

**Standard indexing speeds**:
- 100 messages: ~5-10 minutes
- 500 messages: ~25-50 minutes
- 1000 messages: ~50-100 minutes

## Verify Results

After indexing, check the output:

```
============================================================
INDEXING COMPLETE
============================================================
Processed: 150
Stored:    145
Failed:    5

Total messages in ChromaDB: 145

✓ Messages successfully indexed!
```

## Troubleshooting

**ChromaDB connection failed**:
- Make sure `start_chromadb.bat` is running
- Check port 8001 is not in use

**No messages found**:
- Verify the room name is correct
- Check that the room has messages in the database

**High failure rate**:
- Check Gemini API key is valid
- Verify API quota is not exceeded
- Review logs for specific errors

## Next Steps

Once indexed, the instant answer system will:
- Automatically search these messages when users ask questions
- Generate AI summaries from relevant past discussions
- Continue indexing new messages in real-time

See `backend/instant_answer/INDEXING_GUIDE.md` for detailed documentation.
