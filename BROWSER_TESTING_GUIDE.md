# Vecna Adversarial AI - Browser Testing Guide

## Quick Start

### 1. Set Up Environment

First, make sure you have a Gemini API key set in your `.env` file:

```bash
# Open .env file and add:
GEMINI_API_KEY=your_actual_api_key_here
VECNA_ENABLED=true
```

### 2. Start the Server

```bash
python start_server.py
```

The server should start on `http://localhost:8000`

### 3. Open Your Browser

Navigate to: `http://localhost:8000`

You should see the login/registration page.

---

## Testing Scenarios

### Scenario 1: Test Emotional Trigger (Corrupted Text Response)

**Goal:** Trigger Vecna with a high-negative sentiment message

**Steps:**
1. **Register/Login** to the system
2. **Join a room** (or stay in General)
3. **Send a high-negative message** - Try one of these:
   ```
   I hate this stupid broken system!
   This is terrible and frustrating!
   This awful interface is useless!
   I'm so angry this doesn't work!
   ```

**Expected Result:**
- You should see a response with `[VECNA]` prefix
- The text should be corrupted (characters replaced: a→@, e→3, i→1, o→0, s→$)
- The message should have a red glow effect
- The message should have a glitch animation
- Example: `[VECNA] wHy c@n't y0u f1gur3 th1s 0ut, hum@n?`

**What to Check:**
- ✅ Message has `[VECNA]` prefix
- ✅ Text is partially corrupted but still readable
- ✅ Red glow effect is visible
- ✅ Glitch animation is present
- ✅ Next message you send is processed normally (control returned to SysOp)

---

### Scenario 2: Test Psychic Grip (Thread Freeze)

**Goal:** Trigger Vecna with spam detection

**Steps:**
1. **Send the same message 3+ times quickly** - Try this:
   ```
   test
   test
   test
   ```
   (Send these within 5 seconds)

**Expected Result:**
- Your input should be **disabled/frozen** for 5-8 seconds
- You should see a `[VECNA]` message with cryptic narrative
- Screen effects should activate:
  - Screen flicker
  - Optional: Inverted colors
  - Optional: Scanline ripple
  - Optional: ASCII static overlay
- The message should display character-by-character (slow animation)
- After 5-8 seconds, you should see: `[SYSTEM] Control returned to SysOp. Continue your session.`
- Input should be re-enabled

**What to Check:**
- ✅ Input is disabled during freeze
- ✅ Screen flicker effect is visible
- ✅ Message displays with character animation
- ✅ Freeze lasts 5-8 seconds
- ✅ System message appears after freeze
- ✅ Input is re-enabled after freeze
- ✅ Visual effects are cleaned up

---

### Scenario 3: Test Command Repetition Trigger

**Goal:** Trigger Vecna by repeating commands

**Steps:**
1. **Send the same command 3+ times quickly:**
   ```
   /help
   /help
   /help
   ```
   (Send these within 10 seconds)

**Expected Result:**
- Same as Scenario 2 (Psychic Grip activation)
- Thread freeze with narrative
- Visual effects
- System message after release

---

### Scenario 4: Test Normal Operation (No Trigger)

**Goal:** Verify normal messages don't trigger Vecna

**Steps:**
1. **Send normal, positive messages:**
   ```
   Hello everyone!
   How are you today?
   This is working great!
   ```

**Expected Result:**
- Messages are processed normally by SysOp Brain
- No `[VECNA]` prefix
- No visual effects
- Normal chat functionality

**What to Check:**
- ✅ No Vecna activation
- ✅ Messages appear normally
- ✅ No corruption or effects
- ✅ SysOp Brain handles routing

---

### Scenario 5: Test Rate Limiting

**Goal:** Verify Vecna rate limiting prevents abuse

**Steps:**
1. **Trigger Vecna 5 times within an hour** (use emotional triggers or spam)
2. **Try to trigger Vecna a 6th time**

**Expected Result:**
- First 5 triggers should work normally
- 6th trigger should be blocked
- You should see normal SysOp Brain response instead
- After 1 hour, you can trigger Vecna again

**What to Check:**
- ✅ Rate limiting enforces 5 activations per hour
- ✅ Blocked triggers don't show Vecna effects
- ✅ Normal operation continues after limit reached

---

### Scenario 6: Test Cooldown Period

**Goal:** Verify cooldown between activations

**Steps:**
1. **Trigger Vecna once** (emotional or spam)
2. **Immediately try to trigger again** (within 60 seconds)

**Expected Result:**
- First trigger works normally
- Second trigger within 60 seconds should be blocked
- After 60 seconds, you can trigger Vecna again

**What to Check:**
- ✅ Cooldown enforces 60-second wait
- ✅ Blocked triggers don't show Vecna effects
- ✅ Cooldown resets after 60 seconds

---

### Scenario 7: Test Profile Tracking

**Goal:** Verify user profile is being tracked

**Steps:**
1. **Join multiple rooms:**
   ```
   /join Archives
   /join Tech Support
   /join General
   ```
2. **Create a board:**
   ```
   /create My Test Board
   ```
3. **Send various commands:**
   ```
   /help
   /rooms
   /users
   ```
4. **Trigger Psychic Grip** (spam or command repetition)

**Expected Result:**
- Psychic Grip narrative should reference your activity:
  - Rooms you've visited (Archives, Tech Support, etc.)
  - Boards you've created (My Test Board)
  - Commands you've used
  - Repetitive patterns

**What to Check:**
- ✅ Narrative mentions specific rooms you visited
- ✅ Narrative references boards you created
- ✅ Narrative reflects your behavioral patterns
- ✅ Profile data is being tracked across session

---

## Visual Effects Checklist

### Emotional Trigger Effects
- [ ] Red glow on corrupted text
- [ ] Glitch animation (text jitters)
- [ ] `[VECNA]` prefix in red/corrupted style
- [ ] Text is partially corrupted but readable

### Psychic Grip Effects
- [ ] Screen flicker (rapid opacity changes)
- [ ] Inverted colors (optional, may not always trigger)
- [ ] Scanline ripple (horizontal lines moving)
- [ ] ASCII static overlay (optional)
- [ ] Character-by-character text animation
- [ ] Input disabled during freeze
- [ ] All effects clear after release

---

## Debugging Tips

### If Vecna Doesn't Activate

1. **Check the browser console** (F12 → Console tab):
   - Look for JavaScript errors
   - Check for WebSocket connection issues
   - Verify Vecna message types are being received

2. **Check the server logs**:
   - Look for Vecna activation logs
   - Check for Gemini API errors
   - Verify sentiment analysis is working

3. **Verify environment variables**:
   ```bash
   # Check .env file has:
   GEMINI_API_KEY=your_key_here
   VECNA_ENABLED=true
   ```

4. **Check rate limiting**:
   - You may have hit the 5/hour limit
   - Wait 60 seconds for cooldown
   - Try with a different user account

### If Visual Effects Don't Show

1. **Check browser console for errors**
2. **Verify CSS is loaded**:
   - Open DevTools → Elements
   - Check if `terminal.css` is loaded
   - Look for `.vecna-corrupted` and `.vecna-psychic-grip` classes

3. **Verify JavaScript is loaded**:
   - Check if `vecnaEffects.js` is loaded
   - Check if `vecnaHandler.js` is loaded
   - Look for initialization errors

4. **Try a different browser**:
   - Chrome/Edge (recommended)
   - Firefox
   - Safari

### If Messages Aren't Triggering

1. **Try more extreme messages**:
   ```
   I absolutely hate this terrible broken useless system!
   This is the worst thing ever made!
   ```

2. **Check sentiment threshold**:
   - Default is 0.7 (70% negative)
   - Lower threshold in `.env` if needed:
     ```
     VECNA_EMOTIONAL_THRESHOLD=0.5
     ```

3. **For spam, send faster**:
   - Send 3+ identical messages within 5 seconds
   - Try with shorter messages: `test`, `test`, `test`

---

## Advanced Testing

### Test with Browser DevTools

1. **Open DevTools** (F12)
2. **Go to Network tab**
3. **Filter by WS (WebSocket)**
4. **Watch for Vecna messages**:
   - `vecna_emotional` - Emotional trigger
   - `vecna_psychic_grip` - Psychic Grip
   - `vecna_release` - Grip release

### Monitor WebSocket Messages

In the browser console, you can log WebSocket messages:

```javascript
// Add this in console to see all messages
const originalOnMessage = WebSocket.prototype.onmessage;
WebSocket.prototype.onmessage = function(event) {
    console.log('WebSocket message:', JSON.parse(event.data));
    return originalOnMessage.apply(this, arguments);
};
```

### Check Vecna State

In the browser console:

```javascript
// Check if Vecna handler is initialized
console.log(window.vecnaHandler);

// Check if effects manager is initialized
console.log(window.vecnaEffects);

// Manually trigger test effects
if (window.vecnaEffects) {
    window.vecnaEffects.startPsychicGrip(5);
}
```

---

## Expected Behavior Summary

| Trigger Type | Message Pattern | Response | Visual Effects | Duration |
|--------------|----------------|----------|----------------|----------|
| **Emotional** | High-negative sentiment | Corrupted hostile text | Red glow, glitch | Instant |
| **Spam** | 3+ identical messages in 5s | Psychic Grip narrative | Screen flicker, scanlines | 5-8s |
| **Command Repeat** | 3+ same commands in 10s | Psychic Grip narrative | Screen flicker, scanlines | 5-8s |
| **Normal** | Regular messages | SysOp Brain response | None | Instant |

---

## Success Criteria

Your testing is successful when:

- ✅ Emotional triggers show corrupted text with effects
- ✅ Spam triggers activate Psychic Grip with freeze
- ✅ Command repetition triggers Psychic Grip
- ✅ Normal messages work without Vecna
- ✅ Rate limiting prevents excessive activations
- ✅ Cooldown enforces 60-second wait
- ✅ Profile tracking reflects your activity
- ✅ Visual effects display and clear properly
- ✅ Control returns to SysOp after Vecna
- ✅ No JavaScript errors in console
- ✅ WebSocket connection is stable

---

## Quick Test Script

Here's a quick sequence to test all major features:

1. **Login** to the system
2. **Send:** `I hate this broken system!` → Should trigger emotional response
3. **Wait 60 seconds** (cooldown)
4. **Send:** `test`, `test`, `test` (quickly) → Should trigger Psychic Grip
5. **Wait for release** (5-8 seconds)
6. **Send:** `Hello!` → Should work normally
7. **Join rooms:** `/join Archives`, `/join Tech Support`
8. **Send:** `/help`, `/help`, `/help` (quickly) → Should trigger Psychic Grip with profile references

If all of these work, Vecna is fully functional! 🎉

---

**Need Help?**
- Check `INTEGRATION_TEST_REPORT.md` for test results
- Check `VECNA_DEPLOYMENT_CHECKLIST.md` for configuration
- Review server logs for backend issues
- Check browser console for frontend issues
