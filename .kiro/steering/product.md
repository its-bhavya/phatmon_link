# Product Overview

Obsidian BBS is a modern reimagining of 1980s Bulletin Board Systems that combines retro terminal aesthetics with real-time chat capabilities and AI-powered features.

## Core Features

**Multi-Room Chat System**: Real-time WebSocket-based communication with themed rooms (Lobby, Techline, Arcade Hall). Users can navigate between rooms, see active users, and view message history.

**Instant Answer Recall**: AI-powered knowledge system active in Techline that searches historical conversations using semantic similarity and provides immediate, contextually relevant answers. Questions are classified, tagged, stored in ChromaDB, and matched against past discussions to generate summaries with source attribution.

**Empathetic Support Bot**: Automatic emotional distress detection that creates private support rooms when negative sentiment is detected. Provides compassionate AI assistance with crisis detection and Indian hotline information when needed.

**Retro Terminal UI**: Authentic CRT monitor effects including scanlines, phosphor glow, and subtle flicker for nostalgic BBS experience.

**Security & Authentication**: JWT-based authentication with bcrypt password hashing, rate limiting, and session management with automatic reconnection.

## Target Audience

Developers and tech enthusiasts who appreciate retro computing aesthetics while wanting modern real-time communication features enhanced by AI capabilities.

## Key Differentiators

- Seamless integration of AI features without disrupting normal chat flow
- Privacy-focused design (instant answers sent privately, support rooms are private)
- Graceful degradation (AI failures never prevent message delivery)
- Nostalgic UI with modern functionality
