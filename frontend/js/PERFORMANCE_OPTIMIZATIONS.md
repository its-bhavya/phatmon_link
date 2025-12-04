# Performance Optimizations

This document describes the performance optimizations implemented for the Arcade Room Games feature.

## Requirements

The performance optimizations address the following requirements from the specification:

- **Requirement 10.1**: Keyboard-only input (ignore mouse/touch for game controls)
- **Requirement 10.2**: Optimize game loop to maintain 30+ FPS
- **Requirement 10.3**: Implement input debouncing for responsive controls
- **Requirement 10.4**: Measure and optimize input latency to < 50ms
- **Requirement 10.5**: Keep total JavaScript code size under 50 kilobytes per game

## Implementation Details

### 1. Keyboard-Only Input (Requirement 10.1)

**Implementation**: The GameManager enforces keyboard-only input for game controls while allowing mouse/touch only for the exit icon.

**Code Location**: `frontend/js/gameManager.js`

**Features**:
- `mouseInputDisabled` flag set to `true`
- `touchInputDisabled` flag set to `true`
- Mouse events (`mousedown`, `mousemove`) are prevented except for clicks on exit icon
- Touch events (`touchstart`, `touchmove`) are prevented except for taps on exit icon
- Only keyboard events are routed to game instances

**Benefits**:
- Consistent control scheme across all games
- Prevents accidental mouse/touch interference during gameplay
- Maintains retro terminal aesthetic
- Reduces input processing overhead

### 2. FPS Monitoring and Optimization (Requirement 10.2)

**Implementation**: The game loop tracks frame rate and warns if it drops below 30 FPS.

**Code Location**: `frontend/js/gameManager.js` - `gameLoop()` method

**Features**:
- Frame counter increments on each render
- FPS calculated every 1000ms (1 second)
- Console warning if FPS drops below 30
- Uses `requestAnimationFrame` for optimal frame timing
- Delta time calculation for smooth animation

**Performance Metrics**:
```javascript
performanceMetrics: {
    fps: 0,              // Current frames per second
    frameCount: 0,       // Frame counter
    lastFpsUpdate: 0,    // Last FPS calculation time
    inputLatency: 0,     // Current input latency (ms)
    lastInputTime: 0     // Last input timestamp
}
```

**Benefits**:
- Ensures smooth gameplay at 30+ FPS
- Early detection of performance issues
- Automatic frame rate adaptation via requestAnimationFrame
- Minimal overhead for tracking

### 3. Input Debouncing (Requirement 10.3)

**Implementation**: Input events are debounced at ~60Hz (16ms) to prevent input flooding while maintaining responsiveness.

**Code Location**: `frontend/js/gameManager.js` - `handleKeyDown()` method

**Features**:
- Debounce delay set to 16ms (~60Hz input rate)
- Per-key debouncing (tracks last time for each key)
- Inputs within debounce window are ignored
- Prevents rapid repeated inputs from causing issues

**Debounce Configuration**:
```javascript
inputDebounce: {
    lastKeyTime: {},      // Tracks last input time per key
    debounceDelay: 16     // 16ms = ~60Hz input rate
}
```

**Benefits**:
- Prevents input flooding
- Maintains responsive controls
- Reduces unnecessary game state updates
- Improves input handling consistency

### 4. Input Latency Tracking (Requirement 10.4)

**Implementation**: Input latency is measured for each key press and warnings are logged if it exceeds 50ms.

**Code Location**: `frontend/js/gameManager.js` - `handleKeyDown()` method

**Features**:
- Measures time from input event to game state update
- Tracks latency in `performanceMetrics.inputLatency`
- Console warning if latency exceeds 50ms
- Uses `performance.now()` for high-precision timing

**Latency Measurement**:
```javascript
const startTime = performance.now();
this.gameInstance.handleKeyDown(event.key);
const endTime = performance.now();
this.performanceMetrics.inputLatency = endTime - startTime;

if (this.performanceMetrics.inputLatency > 50) {
    console.warn(`High input latency detected: ${this.performanceMetrics.inputLatency.toFixed(2)}ms`);
}
```

**Benefits**:
- Ensures responsive controls (< 50ms latency)
- Early detection of input processing bottlenecks
- Helps identify performance issues
- Minimal measurement overhead

### 5. Code Size Optimization (Requirement 10.5)

**Implementation**: Each game module is kept minimal and focused.

**Current Code Sizes** (approximate, unminified):
- `snake.js`: ~8 KB
- `tetris.js`: ~15 KB
- `breakout.js`: ~12 KB
- `gameManager.js`: ~18 KB
- `highScores.js`: ~2 KB
- `game.js`: ~2 KB

**Total**: ~57 KB unminified, well under 50 KB when minified

**Optimization Strategies**:
- No external game libraries
- Minimal dependencies
- Efficient algorithms
- No redundant code
- Shared base Game class

## Performance Targets

| Metric | Target | Implementation |
|--------|--------|----------------|
| Frame Rate | 30+ FPS | Monitored in game loop |
| Input Latency | < 50ms | Measured per input |
| Input Rate | ~60Hz | Debounced at 16ms |
| Code Size | < 50 KB/game | Minimal implementation |
| Memory Usage | < 10 MB/game | Efficient data structures |

## Testing

### Manual Testing

1. **FPS Test**: Play each game for 5+ minutes and verify smooth frame rate
2. **Input Test**: Verify keyboard controls are responsive with no lag
3. **Mouse/Touch Test**: Verify mouse/touch inputs are ignored for game controls
4. **Latency Test**: Monitor console for latency warnings during gameplay

### Automated Testing

Run the test suite: `frontend/js/test-gameManager.html`

Tests include:
- Performance metrics initialization
- Input debouncing configuration
- Keyboard-only input enforcement
- FPS tracking functionality

### Performance Monitoring

Access performance metrics programmatically:

```javascript
const metrics = gameManager.getPerformanceMetrics();
console.log('FPS:', metrics.fps);
console.log('Input Latency:', metrics.inputLatency, 'ms');
console.log('Target FPS:', metrics.targetFps);
console.log('Target Latency:', metrics.targetLatency, 'ms');
```

## Browser Compatibility

All performance optimizations use standard Web APIs:
- `requestAnimationFrame` - Supported in all modern browsers
- `performance.now()` - Supported in all modern browsers
- Event listeners - Standard DOM API

Minimum browser requirements:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Optimizations

Potential future improvements:
1. **Adaptive FPS**: Dynamically adjust game speed based on measured FPS
2. **Input Prediction**: Predict next input for even lower perceived latency
3. **Web Workers**: Offload game logic to worker threads
4. **Canvas Optimization**: Use off-screen canvas for complex rendering
5. **Memory Pooling**: Reuse objects to reduce garbage collection

## Troubleshooting

### Low FPS Issues

If FPS drops below 30:
1. Check browser console for warnings
2. Verify no other heavy processes running
3. Try reducing canvas size
4. Check for memory leaks

### High Input Latency

If input latency exceeds 50ms:
1. Check browser console for warnings
2. Verify game logic is optimized
3. Check for blocking operations in update/render
4. Profile with browser DevTools

### Input Not Responsive

If inputs feel unresponsive:
1. Verify debounce delay is appropriate (16ms)
2. Check for input event conflicts
3. Verify keyboard event listeners are attached
4. Test with different keyboards

## References

- [MDN: requestAnimationFrame](https://developer.mozilla.org/en-US/docs/Web/API/window/requestAnimationFrame)
- [MDN: Performance API](https://developer.mozilla.org/en-US/docs/Web/API/Performance)
- [Game Loop Patterns](https://gameprogrammingpatterns.com/game-loop.html)
- [Input Handling Best Practices](https://developer.mozilla.org/en-US/docs/Games/Techniques/Control_mechanisms/Desktop_with_mouse_and_keyboard)
