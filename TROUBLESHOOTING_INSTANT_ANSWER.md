# Instant Answer Recall - Troubleshooting Guide

## Overview

This guide helps you diagnose and resolve issues with the Instant Answer Recall system. It covers common problems, their causes, and step-by-step solutions.

## Quick Diagnostics

### Is the System Working?

Run this quick check:

1. **Check if enabled**: Look for `INSTANT_ANSWER_ENABLED=true` in `.env`
2. **Check ChromaDB**: Visit `http://localhost:8001/api/v1/heartbeat`
3. **Check Gemini API**: Verify `GEMINI_API_KEY` is set
4. **Check room**: Ensure you're in the Techline room
5. **Check logs**: Look for instant answer processing in application logs

### Quick Test

Post this question in Techline:

```
How do I implement JWT authentication?
```

**Expected behavior**:
- You receive a private instant answer (or novel question message)
- Your question is posted publicly
- No errors in logs

## Common Issues

### 1. No Instant Answers Appearing

#### Symptoms
- Questions posted but no instant answer received
- No private messages from the system
- Questions appear publicly but no AI response

#### Possible Causes

**A. System Disabled**

Check `.env` file:
```bash
INSTANT_ANSWER_ENABLED=true
```

**Solution**: Set to `true` and restart the server

**B. Wrong Room**

Instant answers only work in the configured target room (default: Techline).

**Solution**: 
- Check `INSTANT_ANSWER_TARGET_ROOM` in `.env`
- Ensure you're in the correct room
- Use `/join techline` to switch rooms

**C. Not a Question**

The system only triggers for messages classified as questions.

**Solution**: Phrase your message as a question:
- Use question words: "How", "What", "Why", "Can", "Should"
- Include a question mark: "?"
- Be specific: "How do I implement X?" vs "Need help with X"

**D. Low Confidence Classification**

If the classifier isn't confident it's a question, instant answers are skipped.

**Solution**:
- Lower `INSTANT_ANSWER_CONFIDENCE_THRESHOLD` (try 0.5)
- Make questions more explicit
- Check logs for classification confidence scores

**E. ChromaDB Not Running**

**Check**: Visit `http://localhost:8001/api/v1/heartbeat`

**Solution**:
```bash
# Start ChromaDB
docker run -d -p 8001:8000 chromadb/chroma

# Or if installed locally
chroma run --host localhost --port 8001
```

**F. Gemini API Issues**

**Check**: Look for API errors in logs

**Solution**:
- Verify `GEMINI_API_KEY` is set and valid
- Check API quota at https://makersuite.google.com/
- Check for rate limiting errors
- Verify internet connectivity

### 2. Instant Answers Are Irrelevant

#### Symptoms
- Receiving instant answers that don't match the question
- Answers about wrong topics or technologies
- Low-quality or generic responses

#### Possible Causes

**A. Similarity Threshold Too Low**

**Check**: `INSTANT_ANSWER_MIN_SIMILARITY` in `.env`

**Solution**: Increase the threshold for stricter matching:
```bash
# Current (default)
INSTANT_ANSWER_MIN_SIMILARITY=0.7

# Try higher for more precision
INSTANT_ANSWER_MIN_SIMILARITY=0.8
```

**B. Insufficient Historical Data**

If the knowledge base is small, matches may be poor.

**Solution**:
- Index more historical messages
- Wait for more conversations to build the knowledge base
- See "Indexing Historical Messages" section below

**C. Poor Question Phrasing**

Vague questions get vague answers.

**Solution**: Be more specific:
- Include framework names: "FastAPI" not "my framework"
- Include technical terms: "JWT authentication" not "login"
- Provide context: "How do I handle CORS in FastAPI?" not "CORS help"

**D. Too Many Results**

Including too many search results can dilute the summary.

**Solution**: Reduce `INSTANT_ANSWER_MAX_RESULTS`:
```bash
# Current (default)
INSTANT_ANSWER_MAX_RESULTS=5

# Try fewer for more focused answers
INSTANT_ANSWER_MAX_RESULTS=3
```

### 3. Instant Answers Are Too Slow

#### Symptoms
- Long delay before receiving instant answer
- Timeout errors in logs
- Questions posted but instant answer arrives late

#### Possible Causes

**A. Too Many Search Results**

**Solution**: Reduce `INSTANT_ANSWER_MAX_RESULTS`:
```bash
INSTANT_ANSWER_MAX_RESULTS=3
```

**B. Summary Too Long**

**Solution**: Reduce `INSTANT_ANSWER_MAX_SUMMARY_TOKENS`:
```bash
# Current (default)
INSTANT_ANSWER_MAX_SUMMARY_TOKENS=300

# Try shorter
INSTANT_ANSWER_MAX_SUMMARY_TOKENS=200
```

**C. Gemini API Latency**

**Check**: Look for slow API response times in logs

**Solution**:
- Check internet connection
- Try different Gemini model (if available)
- Check Gemini API status
- Consider caching frequent queries (future enhancement)

**D. ChromaDB Performance**

**Check**: Look for slow ChromaDB queries in logs

**Solution**:
- Ensure ChromaDB has sufficient resources
- Check ChromaDB collection size
- Consider ChromaDB optimization (indexing, memory)
- Monitor ChromaDB logs for errors

### 4. ChromaDB Connection Errors

#### Symptoms
- "Connection refused" errors
- "ChromaDB unreachable" in logs
- Instant answers not working

#### Diagnosis

**Check ChromaDB status**:
```bash
curl http://localhost:8001/api/v1/heartbeat
```

**Expected response**: `{"nanosecond heartbeat": ...}`

#### Solutions

**A. ChromaDB Not Running**

**Start ChromaDB**:
```bash
# Using Docker (recommended)
docker run -d -p 8001:8000 chromadb/chroma

# Or locally
chroma run --host localhost --port 8001
```

**B. Wrong Host/Port**

**Check `.env`**:
```bash
CHROMADB_HOST=localhost
CHROMADB_PORT=8001
```

**Solution**: Update to match your ChromaDB configuration

**C. Firewall Blocking Connection**

**Solution**:
- Check firewall rules
- Ensure port 8001 is open
- Try `telnet localhost 8001` to test connectivity

**D. ChromaDB Crashed**

**Check logs**:
```bash
docker logs <chromadb-container-id>
```

**Solution**:
- Restart ChromaDB
- Check for disk space issues
- Check for memory issues
- Review ChromaDB logs for errors

### 5. Gemini API Errors

#### Symptoms
- "API key invalid" errors
- "Rate limit exceeded" errors
- "Service unavailable" errors
- Classification or summary generation failures

#### Solutions

**A. Invalid API Key**

**Check**: `GEMINI_API_KEY` in `.env`

**Solution**:
- Get a valid API key from https://makersuite.google.com/
- Set in `.env`: `GEMINI_API_KEY=your-key-here`
- Restart the server

**B. Rate Limiting**

**Symptoms**: "429 Too Many Requests" errors

**Solution**:
- Wait for rate limit to reset (usually 1 minute)
- Reduce message volume
- Consider upgrading Gemini API quota
- System has built-in retry logic (2 retries with backoff)

**C. API Quota Exceeded**

**Check**: Gemini API dashboard for quota usage

**Solution**:
- Wait for quota to reset (usually daily)
- Upgrade to higher quota tier
- Reduce `INSTANT_ANSWER_MAX_RESULTS` to use fewer API calls

**D. Service Unavailable**

**Symptoms**: "503 Service Unavailable" errors

**Solution**:
- Check Gemini API status page
- Wait for service to recover
- System will gracefully degrade (post message without instant answer)

### 6. Messages Not Being Indexed

#### Symptoms
- Novel question messages for all questions
- Empty search results
- ChromaDB collection is empty

#### Diagnosis

**Check collection size**:
```python
# In Python console
import chromadb
client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_collection("techline_messages")
print(f"Messages in collection: {collection.count()}")
```

#### Solutions

**A. Indexing Not Running**

**Solution**: Run manual indexing:
```bash
# Standard indexing
python index_historical_messages.py --room Techline --limit 1000

# Fast indexing (recommended)
python index_historical_messages.py --fast --room Techline --limit 1000
```

**B. Indexing Failures**

**Check logs** for indexing errors

**Common causes**:
- Gemini API errors (see section 5)
- ChromaDB errors (see section 4)
- Invalid message data

**Solution**:
- Fix underlying API/DB issues
- Re-run indexing
- Check message data quality

**C. Wrong Collection Name**

**Check `.env`**:
```bash
CHROMADB_COLLECTION_NAME=techline_messages
```

**Solution**: Ensure collection name matches across configuration

### 7. Instant Answers Missing Code

#### Symptoms
- Code snippets not preserved in summaries
- Formatting lost in instant answers
- Code blocks not displayed properly

#### Possible Causes

**A. Source Messages Don't Contain Code**

**Check**: Search results may not include code examples

**Solution**: This is expected behavior. Not all answers contain code.

**B. Summary Generation Issue**

**Check logs** for summary generation errors

**Solution**:
- Verify Gemini API is working
- Check `INSTANT_ANSWER_MAX_SUMMARY_TOKENS` isn't too low
- Review summary generation prompts

**C. Frontend Display Issue**

**Check**: Browser console for rendering errors

**Solution**:
- Verify markdown rendering is working
- Check CSS for code block styling
- Test with browser dev tools

### 8. High Error Rates

#### Symptoms
- Frequent errors in logs
- Many failed classifications
- Storage failures
- Search failures

#### Diagnosis

**Check error logs**:
```bash
# Look for patterns
grep "ERROR" application.log | tail -50

# Check specific components
grep "Classification failed" application.log
grep "Storage failed" application.log
grep "Search failed" application.log
```

#### Solutions

**A. Gemini API Issues**

**Solution**: See section 5 (Gemini API Errors)

**B. ChromaDB Issues**

**Solution**: See section 4 (ChromaDB Connection Errors)

**C. Network Issues**

**Check**: Internet connectivity, DNS resolution

**Solution**:
- Verify network connectivity
- Check firewall rules
- Test API endpoints manually

**D. Resource Constraints**

**Check**: CPU, memory, disk usage

**Solution**:
- Increase server resources
- Reduce concurrent load
- Optimize configuration (fewer results, shorter summaries)

## Advanced Troubleshooting

### Enable Debug Logging

Add to `.env`:
```bash
LOG_LEVEL=DEBUG
```

Restart server and check logs for detailed information.

### Test Individual Components

**Test Classification**:
```bash
python -m backend.instant_answer.demo_classifier
```

**Test Tagging**:
```bash
python -m backend.instant_answer.demo_tagger
```

**Test Search**:
```bash
python -m backend.instant_answer.demo_search
```

**Test Summary**:
```bash
python -m backend.instant_answer.demo_summary
```

**Test Full Service**:
```bash
python -m backend.instant_answer.demo_service
```

### Verify ChromaDB Data

```python
import chromadb

# Connect
client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_collection("techline_messages")

# Check count
print(f"Total messages: {collection.count()}")

# Sample data
results = collection.peek(limit=5)
print(f"Sample messages: {results}")

# Query test
results = collection.query(
    query_texts=["How do I implement JWT?"],
    n_results=5
)
print(f"Search results: {len(results['ids'][0])}")
```

### Check Configuration

```python
from backend.instant_answer.config import InstantAnswerConfig

config = InstantAnswerConfig.from_env()
print(f"Enabled: {config.enabled}")
print(f"Target room: {config.target_room}")
print(f"Min similarity: {config.min_similarity_threshold}")
print(f"Max results: {config.max_search_results}")
print(f"Confidence threshold: {config.classification_confidence_threshold}")
```

### Monitor API Usage

**Gemini API**:
- Visit https://makersuite.google.com/
- Check quota usage
- Monitor rate limits

**ChromaDB**:
```bash
# Check collection stats
curl http://localhost:8001/api/v1/collections/techline_messages
```

## Performance Tuning

### For Faster Responses

```bash
# Reduce search results
INSTANT_ANSWER_MAX_RESULTS=3

# Shorter summaries
INSTANT_ANSWER_MAX_SUMMARY_TOKENS=200

# Higher confidence threshold (fewer instant answers)
INSTANT_ANSWER_CONFIDENCE_THRESHOLD=0.7
```

### For Better Quality

```bash
# Higher similarity threshold
INSTANT_ANSWER_MIN_SIMILARITY=0.8

# More search results
INSTANT_ANSWER_MAX_RESULTS=7

# Longer summaries
INSTANT_ANSWER_MAX_SUMMARY_TOKENS=400
```

### For More Instant Answers

```bash
# Lower confidence threshold
INSTANT_ANSWER_CONFIDENCE_THRESHOLD=0.5

# Lower similarity threshold
INSTANT_ANSWER_MIN_SIMILARITY=0.6
```

## Indexing Historical Messages

### Standard Indexing

```bash
python index_historical_messages.py --room Techline --limit 1000
```

**Use when**:
- Small datasets (<100 messages)
- Testing indexing process
- Debugging indexing issues

### Fast Indexing (Recommended)

```bash
python index_historical_messages.py --fast --room Techline --limit 1000
```

**Use when**:
- Large datasets (>100 messages)
- Initial setup
- Re-indexing after updates

**Performance**: 10-15x faster than standard indexing

### Verify Indexing

```python
import chromadb

client = chromadb.HttpClient(host="localhost", port=8001)
collection = client.get_collection("techline_messages")

print(f"Messages indexed: {collection.count()}")
```

### Re-indexing

If you need to re-index (after configuration changes, data corruption, etc.):

```bash
# Delete collection
python -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8001)
client.delete_collection('techline_messages')
"

# Re-index
python index_historical_messages.py --fast --room Techline --limit 1000
```

## Getting Help

### Check Documentation

- **Architecture**: `backend/instant_answer/ARCHITECTURE.md`
- **User Guide**: `USER_GUIDE_INSTANT_ANSWER.md`
- **Configuration**: `backend/CONFIG.md`
- **ChromaDB Setup**: `CHROMADB_SETUP.md`
- **Indexing**: `backend/instant_answer/INDEXING_GUIDE.md`

### Check Logs

Application logs contain detailed information about:
- Classification results
- Search queries and results
- Summary generation
- Errors and warnings

### Run Diagnostics

```bash
# Test all components
python diagnose_instant_answer.py
```

### Contact Support

If issues persist:

1. **Gather information**:
   - Error messages from logs
   - Configuration settings
   - Steps to reproduce
   - Expected vs actual behavior

2. **Check GitHub issues**: Search for similar problems

3. **Create new issue**: Include all gathered information

## Common Error Messages

### "Classification failed: API error"

**Cause**: Gemini API unavailable or rate limited

**Solution**: See section 5 (Gemini API Errors)

### "ChromaDB unreachable"

**Cause**: ChromaDB not running or wrong configuration

**Solution**: See section 4 (ChromaDB Connection Errors)

### "No results found for query"

**Cause**: Empty knowledge base or very specific question

**Solution**: Index historical messages or wait for knowledge base to grow

### "Confidence below threshold"

**Cause**: Classifier not confident message is a question

**Solution**: Lower `INSTANT_ANSWER_CONFIDENCE_THRESHOLD` or phrase as clearer question

### "Storage failed: collection not found"

**Cause**: ChromaDB collection doesn't exist

**Solution**: Restart application (collection created automatically) or run indexing

### "Embedding generation timeout"

**Cause**: Gemini API slow or network issues

**Solution**: Check network connectivity, increase timeout, or retry

## Prevention

### Regular Maintenance

1. **Monitor logs**: Check for errors daily
2. **Check ChromaDB**: Verify collection size and health
3. **Monitor API usage**: Track Gemini API quota
4. **Backup ChromaDB**: Regular backups of data directory
5. **Update dependencies**: Keep libraries up to date

### Best Practices

1. **Use fast indexing**: For large datasets
2. **Set appropriate thresholds**: Balance quality vs quantity
3. **Monitor performance**: Track latency and error rates
4. **Test after changes**: Verify system works after configuration changes
5. **Document issues**: Keep track of problems and solutions

## Conclusion

Most issues with the Instant Answer Recall system can be resolved by:

1. Verifying ChromaDB is running
2. Checking Gemini API key and quota
3. Ensuring correct room and configuration
4. Indexing historical messages
5. Adjusting thresholds for your use case

If problems persist, check the detailed documentation and logs for more information.
