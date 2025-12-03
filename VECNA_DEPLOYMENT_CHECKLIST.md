# Vecna Adversarial AI - Deployment Checklist

## ✅ Implementation Complete

All 20 tasks from the implementation plan have been completed successfully. The Vecna Adversarial AI Module is fully integrated with the Phantom Link BBS system.

## Pre-Deployment Checklist

### 1. Environment Configuration
- [ ] Set `GEMINI_API_KEY` in production `.env` file
- [ ] Verify `VECNA_ENABLED=true` in configuration
- [ ] Review and adjust rate limiting thresholds:
  - `VECNA_MAX_ACTIVATIONS_PER_HOUR=5`
  - `VECNA_COOLDOWN_SECONDS=60`
- [ ] Set `VECNA_EMOTIONAL_THRESHOLD=0.7` (adjust based on desired sensitivity)

### 2. Database Migration
- [ ] Ensure database includes new tables:
  - `user_profiles`
  - `command_history`
  - `board_tracking`
  - `vecna_activations`
- [ ] Verify indexes are created for performance
- [ ] Run database migration if needed

### 3. Testing
- [ ] Run full test suite: `python -m pytest backend/tests/ -v`
- [ ] Verify 93%+ test pass rate
- [ ] Perform manual visual effects testing:
  - [ ] Test emotional trigger with corrupted text
  - [ ] Test Psychic Grip with screen effects
  - [ ] Verify effect cleanup after activation
- [ ] Test with real Gemini API key (not mock)

### 4. Frontend Verification
- [ ] Verify `vecnaEffects.js` is loaded in `main.js`
- [ ] Verify `vecnaHandler.js` is loaded in `main.js`
- [ ] Verify CSS classes in `terminal.css` are present
- [ ] Test WebSocket message routing for new Vecna message types

### 5. Monitoring Setup
- [ ] Enable Vecna activation logging
- [ ] Set up alerts for unusual activation patterns
- [ ] Configure Gemini API usage monitoring
- [ ] Set up dashboard for activation metrics

### 6. Security Review
- [ ] Verify API key is not hardcoded anywhere
- [ ] Confirm rate limiting is active
- [ ] Test admin disable controls
- [ ] Review activation logs for sensitive data

## Deployment Steps

### Step 1: Staging Deployment
1. Deploy to staging environment
2. Set staging `GEMINI_API_KEY`
3. Run integration tests
4. Perform manual testing with real users
5. Monitor for 24-48 hours

### Step 2: Production Deployment
1. Deploy to production environment
2. Set production `GEMINI_API_KEY`
3. Enable monitoring and logging
4. Start with conservative rate limits
5. Monitor activation patterns

### Step 3: Post-Deployment
1. Monitor Vecna activation rates
2. Gather user feedback
3. Adjust thresholds based on usage
4. Review Gemini API costs
5. Optimize based on metrics

## Quick Start Commands

### Run All Tests
```bash
python -m pytest backend/tests/ -v
```

### Run Vecna-Specific Tests
```bash
python -m pytest backend/tests/test_vecna_*.py -v
```

### Start Server
```bash
python start_server.py
```

### Check Vecna Status
```python
from backend.vecna.monitoring import VecnaMonitor
monitor = VecnaMonitor()
metrics = monitor.get_metrics()
print(metrics)
```

## Configuration Reference

### Recommended Production Settings
```env
# Gemini API
GEMINI_API_KEY=your_production_api_key_here
GEMINI_MODEL=gemini-2.5-flash
GEMINI_TEMPERATURE=0.9
GEMINI_MAX_TOKENS=500

# Vecna Configuration
VECNA_ENABLED=true
VECNA_EMOTIONAL_THRESHOLD=0.7
VECNA_SPAM_THRESHOLD=3
VECNA_COMMAND_REPEAT_THRESHOLD=3
VECNA_MAX_ACTIVATIONS_PER_HOUR=5
VECNA_COOLDOWN_SECONDS=60

# Profile Tracking
PROFILE_RETENTION_DAYS=30
PROFILE_CACHE_TTL_SECONDS=300
```

### Adjusting Sensitivity

**More Aggressive Vecna:**
- Lower `VECNA_EMOTIONAL_THRESHOLD` to 0.5
- Lower `VECNA_SPAM_THRESHOLD` to 2
- Increase `VECNA_MAX_ACTIVATIONS_PER_HOUR` to 10

**Less Aggressive Vecna:**
- Raise `VECNA_EMOTIONAL_THRESHOLD` to 0.8
- Raise `VECNA_SPAM_THRESHOLD` to 5
- Decrease `VECNA_MAX_ACTIVATIONS_PER_HOUR` to 3

## Troubleshooting

### Vecna Not Activating
1. Check `VECNA_ENABLED=true` in config
2. Verify `GEMINI_API_KEY` is set
3. Check rate limiting hasn't been exceeded
4. Review activation logs for errors

### Visual Effects Not Showing
1. Verify frontend files are loaded
2. Check browser console for JavaScript errors
3. Verify WebSocket connection is active
4. Test with different browsers

### Gemini API Errors
1. Verify API key is valid
2. Check API quota and billing
3. Review error logs for specific issues
4. Ensure fallback responses are working

### High API Costs
1. Review activation frequency
2. Adjust rate limiting thresholds
3. Consider caching similar responses
4. Monitor per-user activation rates

## Support and Documentation

### Key Documentation Files
- `backend/vecna/README_AUTO_ROUTING.md` - Auto-routing integration
- `backend/vecna/CORRUPTION_IMPLEMENTATION.md` - Text corruption details
- `backend/vecna/MONITORING_GUIDE.md` - Monitoring and logging
- `backend/vecna/ABUSE_PREVENTION.md` - Abuse prevention mechanisms
- `backend/websocket/VECNA_MESSAGE_TYPES.md` - WebSocket message types
- `frontend/js/VECNA_EFFECTS_IMPLEMENTATION.md` - Visual effects details

### Test Reports
- `INTEGRATION_TEST_REPORT.md` - Complete integration test results

### Contact
For questions or issues, refer to the spec documents in `.kiro/specs/vecna-adversarial-ai/`:
- `requirements.md` - Feature requirements
- `design.md` - System design and architecture
- `tasks.md` - Implementation task list

## Success Criteria

The deployment is successful when:
- ✅ All tests pass (93%+ pass rate)
- ✅ Vecna activates on appropriate triggers
- ✅ Visual effects display correctly
- ✅ No existing functionality is broken
- ✅ Rate limiting prevents abuse
- ✅ Monitoring shows expected activation patterns
- ✅ User feedback is positive
- ✅ API costs are within budget

---

**Last Updated:** December 3, 2025  
**Version:** 1.0  
**Status:** Ready for Deployment
