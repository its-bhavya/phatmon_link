# Implementation Plan: Vecna Adversarial AI Module

## Task List

- [x] 1. Set up database schema and models for user profiles and Vecna tracking





  - Create database migration for new tables (user_profiles, command_history, board_tracking, vecna_activations)
  - Add indexes for performance optimization
  - _Requirements: 7.1, 7.2, 7.3_

- [ ]* 1.1 Write property test for profile tracking
  - **Property 23: Room visit tracking**
  - **Validates: Requirements 7.1**

- [ ]* 1.2 Write property test for command tracking
  - **Property 24: Command tracking**
  - **Validates: Requirements 7.2**

- [ ]* 1.3 Write property test for board creation tracking
  - **Property 25: Board creation tracking**
  - **Validates: Requirements 7.3**

- [x] 2. Implement User Profile Service





  - Create UserProfile data model with interests, frequent rooms, recent rooms, command history, and behavioral patterns
  - Implement UserProfileService with methods for profile creation, retrieval, and updates
  - Implement room visit recording, command tracking, and board creation tracking
  - Implement baseline activity calculation and deviation metrics
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ]* 2.1 Write property test for deviation calculation
  - **Property 26: Deviation calculation**
  - **Validates: Requirements 7.4**

- [ ]* 2.2 Write property test for read-only profile access
  - **Property 27: Read-only profile access**
  - **Validates: Requirements 7.5**

- [x] 3. Implement Gemini AI Service





  - Create GeminiService class with Gemini 2.5 Flash API integration
  - Implement methods for SysOp Brain suggestions, Vecna hostile responses, and Psychic Grip narratives
  - Implement adversarial prompt generation for Vecna
  - Add error handling and fallback mechanisms
  - Load API credentials from environment configuration
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 3.1 Write property test for Gemini API integration
  - **Property 28: Gemini API integration**
  - **Validates: Requirements 8.1, 8.2, 8.3**

- [ ]* 3.2 Write property test for API error handling
  - **Property 29: API error handling**
  - **Validates: Requirements 8.4**

- [ ]* 3.3 Write property test for secure credential storage
  - **Property 30: Secure credential storage**
  - **Validates: Requirements 8.5**

- [x] 4. Implement Sentiment Analysis Service





  - Create SentimentAnalyzer class with sentiment detection logic
  - Implement keyword-based negative sentiment detection
  - Implement intensity calculation and threshold checking
  - Return SentimentResult with polarity, intensity, and trigger status
  - _Requirements: 2.1, 3.1_

- [ ]* 4.1 Write property test for emotional trigger activation
  - **Property 6: Emotional trigger activation**
  - **Validates: Requirements 2.1**

- [x] 5. Implement Pattern Detection Service





  - Create PatternDetector class with spam, command repetition, and anomaly detection
  - Implement spam detection with configurable threshold and time window
  - Implement command repetition detection
  - Implement unusual activity detection using baseline deviation
  - _Requirements: 2.2, 2.3, 2.4_

- [ ]* 5.1 Write property test for spam pattern detection
  - **Property 7: Spam pattern detection**
  - **Validates: Requirements 2.2**

- [ ]* 5.2 Write property test for command repetition detection
  - **Property 8: Command repetition detection**
  - **Validates: Requirements 2.3**

- [ ]* 5.3 Write property test for anomaly detection
  - **Property 9: Anomaly detection**
  - **Validates: Requirements 2.4**

- [x] 6. Implement text corruption algorithm





  - Create text corruption function with character substitution map
  - Implement corruption level control (percentage of characters to corrupt)
  - Ensure partial readability (minimum 50% readable characters)
  - Handle edge cases (empty strings, special characters, punctuation)
  - _Requirements: 3.2, 3.5_

- [ ]* 6.1 Write property test for text corruption application
  - **Property 11: Text corruption application**
  - **Validates: Requirements 3.2**

- [ ]* 6.2 Write property test for partial readability preservation
  - **Property 13: Partial readability preservation**
  - **Validates: Requirements 3.5**

- [x] 7. Implement Vecna Module core functionality





  - Create VecnaModule class with trigger evaluation logic
  - Implement evaluate_triggers method that checks emotional and system triggers
  - Implement execute_emotional_trigger method with text corruption and hostile response generation
  - Implement execute_psychic_grip method with freeze duration and narrative generation
  - Integrate with SentimentAnalyzer, PatternDetector, and GeminiService
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3, 3.4, 4.1, 4.3, 4.4_

- [ ]* 7.1 Write property test for Vecna control override
  - **Property 10: Vecna control override**
  - **Validates: Requirements 2.5, 3.1**

- [ ]* 7.2 Write property test for hostile response generation
  - **Property 12: Hostile response generation**
  - **Validates: Requirements 3.3**

- [ ]* 7.3 Write property test for thread freeze duration
  - **Property 14: Thread freeze duration**
  - **Validates: Requirements 4.1**

- [ ]* 7.4 Write property test for profile data in narrative
  - **Property 16: Profile data in narrative**
  - **Validates: Requirements 4.3**

- [ ] 8. Implement SysOp Brain Service
  - Create SysOpBrain class with normal routing logic
  - Implement process_message method for message routing and board creation
  - Implement suggest_rooms method using user profile analysis
  - Implement create_dynamic_board method for topic-based board creation
  - Integrate with GeminiService and RoomService
  - _Requirements: 1.1, 1.2, 1.4, 1.5_

- [ ]* 8.1 Write property test for SysOp Brain baseline routing
  - **Property 1: SysOp Brain baseline routing**
  - **Validates: Requirements 1.1**

- [ ]* 8.2 Write property test for user profile data access
  - **Property 2: User profile data access**
  - **Validates: Requirements 1.2**

- [ ]* 8.3 Write property test for room suggestion generation
  - **Property 4: Room suggestion generation**
  - **Validates: Requirements 1.4**

- [ ]* 8.4 Write property test for board persistence
  - **Property 5: Board persistence**
  - **Validates: Requirements 1.5**

- [ ] 9. Integrate Vecna and SysOp Brain into message processing pipeline
  - Modify WebSocket message handler in backend/main.py to include Vecna evaluation
  - Implement message flow: SysOp Brain → Vecna Check → Conditional Activation → Return to SysOp
  - Add Vecna trigger evaluation after SysOp Brain routing
  - Handle Vecna responses (emotional trigger and Psychic Grip)
  - Ensure control returns to SysOp Brain after Vecna activation
  - _Requirements: 1.3, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 9.1 Write property test for control resumption after Vecna
  - **Property 3: Control resumption after Vecna**
  - **Validates: Requirements 1.3, 6.4**

- [ ]* 9.2 Write property test for processing order
  - **Property 20: Processing order**
  - **Validates: Requirements 6.1, 6.2**

- [ ]* 9.3 Write property test for normal path continuation
  - **Property 21: Normal path continuation**
  - **Validates: Requirements 6.3**

- [ ]* 9.4 Write property test for WebSocket compatibility
  - **Property 22: WebSocket compatibility**
  - **Validates: Requirements 6.5**

- [ ] 10. Implement Psychic Grip release mechanism
  - Add timer mechanism for Psychic Grip duration (5-8 seconds)
  - Implement grip release that sends system message and re-enables input
  - Ensure proper cleanup after grip release
  - _Requirements: 4.5_

- [ ]* 10.1 Write property test for grip release message
  - **Property 17: Grip release message**
  - **Validates: Requirements 4.5, 9.2**

- [ ] 11. Add Vecna message types to WebSocket protocol
  - Define vecna_emotional message type with corrupted content
  - Define vecna_psychic_grip message type with duration and effects
  - Define vecna_release message type for grip release
  - Update WebSocket message routing to handle new types
  - _Requirements: 3.3, 4.1, 4.5, 9.1_

- [ ]* 11.1 Write property test for Vecna message prefix
  - **Property 31: Vecna message prefix**
  - **Validates: Requirements 9.1**

- [ ] 12. Checkpoint - Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 13. Implement frontend Vecna Effects Manager
  - Create VecnaEffects class in frontend/js/vecnaEffects.js
  - Implement applyTextCorruption method for displaying corrupted text
  - Implement startPsychicGrip method with visual effects (flicker, inverted colors, scanlines, static)
  - Implement endPsychicGrip method for cleanup and restoration
  - Add CSS classes and animations for Vecna effects
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ]* 13.1 Write property test for visual effects application
  - **Property 18: Visual effects application**
  - **Validates: Requirements 5.1, 5.2**

- [ ]* 13.2 Write property test for visual effects cleanup
  - **Property 19: Visual effects cleanup**
  - **Validates: Requirements 5.6, 9.5**

- [ ] 14. Implement frontend Vecna Handler
  - Create VecnaHandler class in frontend/js/vecnaHandler.js
  - Implement handleEmotionalTrigger method for corrupted message display
  - Implement handlePsychicGrip method for freeze and narrative display
  - Implement handleGripRelease method for cleanup
  - Implement displayVecnaMessage with [VECNA] prefix and special styling
  - Add character-by-character animation for Psychic Grip messages
  - _Requirements: 3.3, 4.2, 4.5, 9.1, 9.3, 9.4_

- [ ]* 14.1 Write property test for corrupted text styling
  - **Property 32: Corrupted text styling**
  - **Validates: Requirements 9.3**

- [ ]* 14.2 Write property test for character animation
  - **Property 33: Character animation**
  - **Validates: Requirements 9.4**

- [ ] 15. Integrate Vecna Handler into main.js
  - Import VecnaHandler and VecnaEffects in main.js
  - Initialize VecnaHandler with chatDisplay, commandBar, and vecnaEffects
  - Add message routing for vecna_emotional, vecna_psychic_grip, and vecna_release types
  - Implement input disabling during Psychic Grip
  - _Requirements: 4.2, 5.1, 5.2, 5.6_

- [ ]* 15.1 Write property test for input disabling during Psychic Grip
  - **Property 15: Input disabling during Psychic Grip**
  - **Validates: Requirements 4.2**

- [ ] 16. Add Vecna CSS styling to terminal.css
  - Add .vecna-corrupted class with red glow and glitch animation
  - Add .vecna-psychic-grip class with screen flicker animation
  - Add .vecna-inverted class with color inversion
  - Add .vecna-scanlines class with scanline ripple effect
  - Add .vecna-static class for ASCII static storm overlay
  - Add @keyframes for glitch, screen-flicker, and scanline-move animations
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 9.3_

- [ ] 17. Add environment configuration for Vecna
  - Add GEMINI_API_KEY to .env.example
  - Add Vecna configuration variables (thresholds, limits, cooldowns)
  - Update backend/config.py to load Vecna configuration
  - Add validation for required Vecna settings
  - _Requirements: 8.5_

- [ ] 18. Implement Vecna abuse prevention
  - Add rate limiting for Vecna activations (max 5 per hour per user)
  - Implement cooldown period between activations (60 seconds)
  - Add activation logging to vecna_activations table
  - Implement admin controls to disable Vecna globally
  - _Requirements: Security considerations_

- [ ] 19. Add monitoring and logging for Vecna
  - Log all Vecna activations with trigger type, reason, and intensity
  - Log Gemini API calls and errors
  - Add metrics for activation rates per user
  - Implement alerts for unusual activation patterns
  - _Requirements: Deployment considerations_

- [ ] 20. Final Checkpoint - Integration testing and user acceptance
  - Test full emotional trigger flow (high-negative message → corrupted response → control return)
  - Test full Psychic Grip flow (spam detection → freeze → narrative → release)
  - Test profile tracking across multiple user actions
  - Test Gemini API integration with real API calls
  - Test visual effects on frontend
  - Verify backward compatibility with existing features
  - Ensure all tests pass, ask the user if questions arise.
