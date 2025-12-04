# Implementation Plan

- [x] 1. Remove Vecna feature completely









  - Delete all Vecna-related files and directories
  - Remove Vecna imports from main.py
  - Remove Vecna configuration from config.py and .env
  - Remove Vecna database tables
  - Remove Vecna frontend components
  - Remove Vecna documentation files
  - Remove Vecna hooks
  - Keep the auto-routing for normal messages to different rooms
  - _Requirements: All (cleanup)_

- [x] 2. Set up Support Bot infrastructure





  - Create backend/support directory structure
  - Move and rename sentiment.py from vecna to support
  - Keep gemini_service.py and user_profile.py for reuse
  - Update configuration for Support Bot settings
  - Create database tables for support logging
  - _Requirements: 8.1, 8.2, 8.3, 9.1, 9.5_

- [x] 3. Implement sentiment analysis for emotional support




  - [x] 3.1 Update SentimentAnalyzer for emotion detection


    - Modify sentiment.py to detect sadness, anger, frustration, anxiety
    - Add emotion type classification
    - Add intensity calculation for emotions
    - Remove Vecna-specific trigger logic
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [ ]* 3.2 Write property test for emotion detection
    - **Property 2: Negative emotion detection triggers support**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5**

- [x] 4. Implement crisis detection system





  - [x] 4.1 Create crisis detection service

    - Implement CrisisType enum (self-harm, suicide, abuse)
    - Add crisis keyword detection
    - Integrate crisis detection into sentiment analysis
    - _Requirements: 6.1, 6.2, 6.3_
  
  - [x] 4.2 Create crisis hotline service


    - Implement HotlineInfo class
    - Add Indian hotline numbers for each crisis type
    - Create hotline message formatting
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  
  - [ ]* 4.3 Write property test for crisis detection
    - **Property 15, 16, 17: Crisis detection**
    - **Validates: Requirements 6.1, 6.2, 6.3**
  
  - [ ]* 4.4 Write property test for crisis response
    - **Property 18: No conversational support during crisis**
    - **Validates: Requirements 6.4**

- [-] 5. Implement Support Bot module


  - [x] 5.1 Create SupportBot class



    - Implement greeting message generation
    - Implement empathetic response generation
    - Implement crisis response generation
    - Create empathetic prompt templates
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5, 9.1, 9.2, 9.3_
  
  - [ ]* 5.2 Write property test for bot responses
    - **Property 13: Bot responses include questions**
    - **Validates: Requirements 4.4**
  
  - [ ]* 5.3 Write property test for no diagnoses
    - **Property 14: No mental health diagnoses in responses**
    - **Validates: Requirements 5.4**
  
  - [ ]* 5.4 Write unit tests for Support Bot
    - Test greeting generation
    - Test response generation
    - Test crisis response
    - Test fallback responses
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 6. Implement support room management




  - [x] 6.1 Create SupportRoomService class


    - Implement support room creation with unique naming
    - Implement room lifecycle management
    - Track active support sessions
    - Implement room privacy settings
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 10.3_
  
  - [ ]* 6.2 Write property test for unique room naming
    - **Property 4: Unique support room naming**
    - **Validates: Requirements 2.2**
  
  - [ ]* 6.3 Write unit tests for room service
    - Test room creation
    - Test room naming
    - Test room lifecycle
    - _Requirements: 2.1, 2.2, 2.3, 2.5_

- [x] 7. Implement support interaction logging
















  - [x] 7.1 Create SupportInteractionLogger class


    - Implement support activation logging
    - Implement crisis detection logging
    - Implement bot interaction logging
    - Implement content anonymization
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [ ]* 7.2 Write property test for privacy protection
    - **Property 27: Privacy protection in logs**
    - **Validates: Requirements 8.5**
  
  - [ ]* 7.3 Write unit tests for logging
    - Test activation logging
    - Test crisis logging
    - Test interaction logging
    - Test anonymization
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 8. Integrate Support Bot into message flow




  - [x] 8.1 Update main.py message handling


    - Remove Vecna integration code
    - Add sentiment analysis for support detection
    - Add crisis detection check
    - Add support room creation on trigger
    - Add Support Bot response generation
    - Maintain SysOp Brain control flow
    - _Requirements: 1.1, 2.1, 2.3, 2.4, 6.4, 6.5, 11.1, 11.2, 11.3, 11.4, 11.5_
  
  - [ ]* 8.2 Write property test for message flow
    - **Property 37, 38, 39, 40: Message flow integration**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4**
  
  - [ ]* 8.3 Write integration tests for support activation
    - Test complete support activation flow
    - Test crisis detection flow
    - Test support conversation flow
    - _Requirements: 1.1, 2.1, 2.3, 2.4, 6.4, 6.5_

- [ ] 9. Implement user context provision
  - [ ] 9.1 Update Support Bot to use user context
    - Provide message history to bot
    - Provide user interests to bot
    - Provide room activity to bot
    - Provide trigger message to bot
    - Ensure read-only access
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [ ]* 9.2 Write property test for context provision
    - **Property 8, 9, 10, 11: Bot receives context**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
  
  - [ ]* 9.3 Write property test for read-only access
    - **Property 12: Read-only user data access**
    - **Validates: Requirements 3.5**

- [ ] 10. Implement room leave and return functionality
  - [ ] 10.1 Add support room leave handling
    - Allow users to leave support rooms
    - Return users to previous room
    - Preserve support room
    - Maintain conversation history
    - _Requirements: 10.1, 10.2, 10.3, 10.4_
  
  - [ ]* 10.2 Write property test for room leave
    - **Property 33, 34, 35, 36: Room leave and return**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4**
  
  - [ ]* 10.3 Write integration test for leave and return flow
    - Test complete leave and return flow
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

- [ ] 11. Implement frontend support handler
  - [ ] 11.1 Create SupportHandler class
    - Handle support_activation messages
    - Handle support_response messages
    - Handle crisis_hotlines messages
    - Display messages with [SUPPORT] prefix
    - Apply support-specific styling
    - _Requirements: 12.1, 12.2, 12.3, 12.4_
  
  - [ ]* 11.2 Write property test for message prefix
    - **Property 42: Support message prefix**
    - **Validates: Requirements 12.1**

- [ ] 12. Add support bot CSS styling
  - Create warm, empathetic color scheme
  - Style [SUPPORT] messages distinctly
  - Style crisis hotline information prominently
  - Ensure readability and accessibility
  - _Requirements: 12.2_

- [ ] 13. Implement error handling
  - [ ] 13.1 Add Gemini API error handling
    - Implement fallback responses
    - Log errors appropriately
    - Continue support session with templates
    - _Requirements: 9.4_
  
  - [ ]* 13.2 Write property test for API error handling
    - **Property 31: Graceful API error handling**
    - **Validates: Requirements 9.4**
  
  - [ ] 13.3 Add database error handling
    - Handle logging failures gracefully
    - Continue operation without blocking
    - _Requirements: 8.1, 8.2, 8.3, 8.4_
  
  - [ ] 13.4 Add sentiment analysis error handling
    - Return neutral sentiment on failure
    - Log errors
    - Continue normal processing
    - _Requirements: 1.1_

- [ ] 14. Update WebSocket message types
  - Add support_activation message type
  - Add support_response message type
  - Add crisis_hotlines message type
  - Update WebSocket manager documentation
  - _Requirements: 11.5_

- [ ] 15. Create support bot documentation
  - Document Support Bot purpose and boundaries
  - Document crisis detection and hotlines
  - Document privacy protections
  - Create user guide for support feature
  - _Requirements: All (documentation)_

- [ ] 16. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 17. Final integration testing
  - [ ]* 17.1 Test complete support activation flow
    - User sends negative message
    - Support room created
    - User joined to room
    - Greeting sent
    - _Requirements: 1.1, 2.1, 2.3, 2.4_
  
  - [ ]* 17.2 Test complete crisis detection flow
    - User sends crisis message
    - Crisis detected
    - Hotlines provided
    - No conversational support
    - Crisis logged
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 8.3_
  
  - [ ]* 17.3 Test complete support conversation flow
    - User in support room
    - User sends message
    - Bot generates response with context
    - Response includes question
    - Interaction logged
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 4.4, 8.4_
  
  - [ ]* 17.4 Test WebSocket compatibility
    - Verify existing message types work
    - Verify new message types work
    - _Requirements: 11.5_
