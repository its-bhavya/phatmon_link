# Quick Start: Auto-Routing

## Setup (2 minutes)

### 1. Get Gemini API Key
Visit: https://makersuite.google.com/app/apikey

### 2. Add to `.env` file
```bash
GEMINI_API_KEY=your_api_key_here
VECNA_ENABLED=true
```

### 3. Start Server
```bash
python start_server.py
```

## How to Test

### Open Browser
Navigate to: http://localhost:8000

### Test Scenarios

**Scenario 1: Tech Question in Lobby**
```
1. Login as user
2. You'll be in Lobby by default
3. Type: "How do I fix this Python import error?"
4. Watch: You'll be auto-moved to Techline
5. See notification: "[SYSOP] Your message seems to be about..."
```

**Scenario 2: General Chat in Techline**
```
1. Join Techline room
2. Type: "What's everyone doing this weekend?"
3. Watch: You'll be auto-moved to Lobby
4. See notification explaining the move
```

**Scenario 3: Gaming in Lobby**
```
1. In Lobby
2. Type: "Anyone want to play Minecraft?"
3. Watch: You'll be auto-moved to Arcade Hall
4. See notification about gaming topic
```

## Configuration

### Default Settings (in `.env`)
```bash
GEMINI_MODEL=gemini-2.0-flash
GEMINI_TEMPERATURE=0.5
GEMINI_MAX_TOKENS=500
```

### Adjust Routing Sensitivity

**More Aggressive** (moves users more often):
```bash
GEMINI_TEMPERATURE=0.7
```

**More Conservative** (moves users less often):
```bash
GEMINI_TEMPERATURE=0.3
```

## Troubleshooting

### Auto-routing not working?

**Check 1: API Key**
```bash
# In .env file
GEMINI_API_KEY=your_actual_key_here  # Not empty!
```

**Check 2: Vecna Enabled**
```bash
# In .env file
VECNA_ENABLED=true  # Not false!
```

**Check 3: Server Logs**
```bash
# Should see on startup:
Gemini service initialized for auto-routing
```

**Check 4: Test API Key**
```bash
python -c "from backend.vecna.gemini_service import GeminiService; import os; GeminiService(os.getenv('GEMINI_API_KEY'))"
```

### Still not working?

**Disable and re-enable:**
```bash
# In .env
VECNA_ENABLED=false  # Save and restart
VECNA_ENABLED=true   # Save and restart again
```

**Check console for errors:**
```bash
# Look for:
Auto-routing error: <error message>
```

## Disable Auto-Routing

### Temporary (this session)
```bash
# In .env
VECNA_ENABLED=false
# Restart server
```

### Permanent
```bash
# Remove or comment out in .env
# GEMINI_API_KEY=...
# VECNA_ENABLED=false
```

## What Happens When Auto-Routing is Disabled?

- Messages work normally
- Users stay in their current rooms
- No automatic room changes
- No AI analysis of messages
- Everything else works the same

## Advanced: Adjust Confidence Threshold

Edit `backend/vecna/auto_router.py`:

```python
# Line ~50
async def auto_route_user(
    user: User,
    message: str,
    current_room: str,
    room_service: RoomService,
    gemini_service: GeminiService,
    confidence_threshold: float = 0.7  # Change this value
):
```

**Values:**
- `0.6` = Very aggressive (moves often)
- `0.7` = Default (balanced)
- `0.8` = Conservative (moves rarely)
- `0.9` = Very conservative (almost never moves)

## Support

### Documentation
- Full details: `backend/vecna/AUTO_ROUTING_INTEGRATION.md`
- Implementation: `INTEGRATION_SUMMARY.md`
- Agent hooks: `backend/vecna/AGENT_HOOKS_GUIDE.md`

### Logs
Enable detailed logging:
```python
# Add to start_server.py
import logging
logging.basicConfig(level=logging.INFO)
```

### Test Suite
```bash
python -m pytest backend/tests/test_gemini_service.py -v
```

## Example Session

```
[User connects to Lobby]
System: Welcome to Gatekeeper, alice!

[User types: "How do I debug Python code?"]
System: [SYSOP] Your message seems to be about technical programming question. Moving you to Techline.
System: === Techline ===
Technology and programming discussions

[User is now in Techline]
alice: How do I debug Python code?
bob: Use pdb or print statements!
```

## That's It!

Auto-routing is now active. Users will be automatically moved to appropriate rooms based on their message content. The system learns from room descriptions and user behavior to make intelligent routing decisions.
