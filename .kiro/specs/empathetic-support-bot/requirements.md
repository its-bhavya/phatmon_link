# Requirements Document

## Introduction

This document specifies the requirements for the Empathetic Support Bot, a compassionate AI system that detects users experiencing negative emotions and connects them with an intelligent, empathetic bot in a dedicated support room. The system analyzes message sentiment to identify users who may benefit from emotional support, then creates a private conversation with context-aware guidance. For crisis situations involving self-harm or abuse, the system provides appropriate Indian hotline numbers without attempting therapeutic intervention.

## Glossary

- **Support Bot**: An empathetic AI assistant that provides compassionate, non-judgmental conversation and practical advice within appropriate boundaries
- **Negative Sentiment Detection**: Analysis of user messages to identify expressions of sadness, anger, frustration, anxiety, or other distressing emotions
- **Support Room**: A private room created specifically for the user to interact with the Support Bot
- **User Context**: Information about the user's recent activity, interests, and conversation history used to personalize support
- **Crisis Keywords**: Specific terms indicating self-harm, abuse, or other emergency situations requiring professional intervention
- **Hotline Information**: Contact numbers for professional crisis services in India
- **SysOp Brain**: The primary AI routing system that handles normal message routing and room management
- **BBS**: Bulletin Board System, the chat application being enhanced

## Requirements

### Requirement 1

**User Story:** As a user experiencing negative emotions, I want the system to recognize my distress, so that I can receive appropriate support.

#### Acceptance Criteria

1. WHEN a user sends a message containing high-intensity negative sentiment THEN the system SHALL flag the message for support intervention
2. WHEN the system detects sadness indicators THEN the system SHALL classify the sentiment as requiring support
3. WHEN the system detects anger indicators THEN the system SHALL classify the sentiment as requiring support
4. WHEN the system detects frustration indicators THEN the system SHALL classify the sentiment as requiring support
5. WHEN the system detects anxiety indicators THEN the system SHALL classify the sentiment as requiring support

### Requirement 2

**User Story:** As a user flagged for support, I want to be connected to an empathetic bot in a private room, so that I can receive personalized support without public exposure.

#### Acceptance Criteria

1. WHEN a user is flagged for support THEN the system SHALL create a dedicated support room for that user
2. WHEN a support room is created THEN the system SHALL name the room uniquely to prevent conflicts
3. WHEN a support room is created THEN the system SHALL automatically join the user to the support room
4. WHEN a user joins a support room THEN the system SHALL send an initial greeting message from the Support Bot
5. WHEN a support room is created THEN the system SHALL mark the room as private to the user

### Requirement 3

**User Story:** As a user in a support room, I want the Support Bot to have context about me, so that the conversation feels personalized and relevant.

#### Acceptance Criteria

1. WHEN the Support Bot generates a response THEN the system SHALL provide the bot with the user's recent message history
2. WHEN the Support Bot generates a response THEN the system SHALL provide the bot with the user's interests from their profile
3. WHEN the Support Bot generates a response THEN the system SHALL provide the bot with the user's recent room activity
4. WHEN the Support Bot generates a response THEN the system SHALL provide the bot with the original message that triggered support
5. WHEN the Support Bot accesses user context THEN the system SHALL ensure read-only access to user data

### Requirement 4

**User Story:** As a user seeking support, I want the Support Bot to be curious and empathetic, so that I feel heard and understood.

#### Acceptance Criteria

1. WHEN the Support Bot generates a response THEN the response SHALL demonstrate curiosity about the user's situation
2. WHEN the Support Bot generates a response THEN the response SHALL express empathy for the user's emotional state
3. WHEN the Support Bot generates a response THEN the response SHALL use warm and non-judgmental language
4. WHEN the Support Bot generates a response THEN the response SHALL ask open-ended questions to encourage sharing
5. WHEN the Support Bot generates a response THEN the response SHALL validate the user's feelings without dismissing them

### Requirement 5

**User Story:** As a user seeking support, I want the Support Bot to provide practical advice within appropriate boundaries, so that I receive helpful guidance without inappropriate therapeutic intervention.

#### Acceptance Criteria

1. WHEN the Support Bot provides advice THEN the advice SHALL be practical and actionable
2. WHEN the Support Bot provides advice THEN the advice SHALL stay within the limitations of an AI assistant
3. WHEN the Support Bot provides advice THEN the system SHALL NOT attempt to emulate a licensed therapist
4. WHEN the Support Bot provides advice THEN the system SHALL NOT diagnose mental health conditions
5. WHEN the Support Bot provides advice THEN the system SHALL suggest general coping strategies appropriate for AI guidance

### Requirement 6

**User Story:** As a user in crisis, I want the system to recognize emergency situations and provide appropriate resources, so that I can access professional help immediately.

#### Acceptance Criteria

1. WHEN a message contains self-harm keywords THEN the system SHALL classify the situation as a crisis
2. WHEN a message contains abuse keywords THEN the system SHALL classify the situation as a crisis
3. WHEN a message contains suicide keywords THEN the system SHALL classify the situation as a crisis
4. WHEN a crisis is detected THEN the system SHALL NOT engage in conversational support
5. WHEN a crisis is detected THEN the system SHALL provide relevant Indian hotline numbers immediately

### Requirement 7

**User Story:** As a user in crisis, I want to receive appropriate hotline information for my specific situation, so that I can contact professional services.

#### Acceptance Criteria

1. WHEN a self-harm crisis is detected THEN the system SHALL provide the National Suicide Prevention Hotline number for India
2. WHEN an abuse crisis is detected THEN the system SHALL provide relevant abuse helpline numbers for India
3. WHEN a crisis response is sent THEN the system SHALL include a brief message encouraging the user to reach out to professionals
4. WHEN a crisis response is sent THEN the system SHALL format hotline information clearly with service name and number
5. WHEN a crisis response is sent THEN the system SHALL NOT provide any advice beyond hotline information

### Requirement 8

**User Story:** As a system administrator, I want user interactions with the Support Bot to be logged, so that I can monitor system effectiveness and identify issues.

#### Acceptance Criteria

1. WHEN a user is flagged for support THEN the system SHALL log the detection event with timestamp and sentiment score
2. WHEN a support room is created THEN the system SHALL log the room creation with user ID and trigger message
3. WHEN a crisis is detected THEN the system SHALL log the crisis type and response provided
4. WHEN the Support Bot generates a response THEN the system SHALL log the interaction for monitoring
5. WHEN logging support interactions THEN the system SHALL protect user privacy by anonymizing sensitive content

### Requirement 9

**User Story:** As a developer, I want the Support Bot to use Gemini AI for response generation, so that conversations are natural and contextually appropriate.

#### Acceptance Criteria

1. WHEN the Support Bot generates a response THEN the system SHALL use Gemini 2.5 Flash API for content generation
2. WHEN the system calls Gemini API THEN the system SHALL include user context in the prompt
3. WHEN the system calls Gemini API THEN the system SHALL include empathetic conversation guidelines in the prompt
4. WHEN the system calls Gemini API THEN the system SHALL handle API errors gracefully with fallback responses
5. WHEN the system configures Gemini API THEN the system SHALL load credentials securely from environment configuration

### Requirement 10

**User Story:** As a user, I want the Support Bot to respect my autonomy, so that I can leave the support room whenever I choose.

#### Acceptance Criteria

1. WHEN a user is in a support room THEN the user SHALL be able to leave the room using standard commands
2. WHEN a user leaves a support room THEN the system SHALL return the user to their previous room
3. WHEN a user leaves a support room THEN the system SHALL preserve the support room for potential return
4. WHEN a user returns to a support room THEN the system SHALL maintain conversation history
5. WHEN a user is connected to support THEN the system SHALL NOT force continued interaction

### Requirement 11

**User Story:** As a system integrator, I want the Support Bot to integrate seamlessly with existing message flow, so that support functionality operates without disrupting core BBS functionality.

#### Acceptance Criteria

1. WHEN a message enters the system THEN the SysOp Brain SHALL perform initial routing before support evaluation
2. WHEN support evaluation completes THEN the system SHALL evaluate whether support intervention is needed
3. WHEN support is not needed THEN the system SHALL continue normal SysOp Brain operation without interruption
4. WHEN support intervention completes THEN the system SHALL return message flow control to the SysOp Brain
5. WHEN the system processes messages THEN the integration SHALL maintain compatibility with existing websocket communication

### Requirement 12

**User Story:** As a user, I want the Support Bot to have a distinct identity, so that I understand I'm interacting with a support-focused assistant.

#### Acceptance Criteria

1. WHEN the Support Bot sends a message THEN the message SHALL be prefixed with "[SUPPORT]" tag
2. WHEN the Support Bot sends a message THEN the message SHALL use a distinct visual style from normal messages
3. WHEN a user enters a support room THEN the system SHALL display a welcome message explaining the Support Bot's purpose
4. WHEN a user enters a support room THEN the system SHALL clarify that the bot is not a replacement for professional help
5. WHEN the Support Bot introduces itself THEN the system SHALL set appropriate expectations for the conversation
