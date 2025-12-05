"""
WebSocket manager for Obsidian BBS.

This module provides WebSocket connection management, message routing, and broadcasting.

Supported Message Types:
- chat_message: Regular chat messages
- system: System notifications
- error: Error messages
- user_list: Active user list updates
- room_list: Room list updates
- room_change: Room change notifications
- help: Help command responses
- support_activation: Support bot activation and greeting (Requirements 2.1, 2.3, 2.4, 12.1, 12.3)
- support_response: Support bot empathetic responses (Requirements 4.1, 4.2, 4.3, 4.4, 12.1, 12.2)
- crisis_hotlines: Crisis hotline information (Requirements 6.4, 6.5, 7.1, 7.2, 7.3, 7.4, 12.1, 12.2, 12.4)

For detailed Support Bot message type specifications, see backend/websocket/SUPPORT_MESSAGE_TYPES.md
"""

from datetime import datetime
from typing import Dict, List, Optional
from fastapi import WebSocket
from backend.database import User
import json


class ActiveUser:
    """
    Represents an active user connection.
    
    Attributes:
        websocket: WebSocket connection for this user
        user: User object from database
        current_room: Name of the room the user is currently in
        connected_at: Timestamp when user connected
    """
    
    def __init__(self, websocket: WebSocket, user: User, current_room: str = "Lobby"):
        """
        Initialize an active user connection.
        
        Args:
            websocket: WebSocket connection
            user: User object
            current_room: Initial room (default: Lobby)
        """
        self.websocket = websocket
        self.user = user
        self.current_room = current_room
        self.connected_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<ActiveUser(username='{self.user.username}', room='{self.current_room}')>"


class WebSocketManager:
    """
    WebSocket manager handling connections, disconnections, and message broadcasting.
    
    This manager provides:
    - Connection and disconnection handling
    - Message sending to specific users
    - Broadcasting to rooms or all users
    - Active connection tracking
    
    Attributes:
        active_connections: Dict mapping WebSocket to ActiveUser
        user_websockets: Dict mapping username to WebSocket
    """
    
    def __init__(self):
        """
        Initialize the WebSocket manager with empty connection tracking.
        """
        self.active_connections: Dict[WebSocket, ActiveUser] = {}
        self.user_websockets: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user: User, initial_room: str = "Lobby") -> None:
        """
        Handle a new WebSocket connection.
        
        This method:
        1. Accepts the WebSocket connection
        2. Creates an ActiveUser object
        3. Adds to connection tracking dictionaries
        
        Args:
            websocket: WebSocket connection to accept
            user: User object for the connecting user
            initial_room: Room to place user in (default: Lobby)
        
        Requirements: 5.1, 6.1
        """
        # Accept the WebSocket connection
        await websocket.accept()
        
        # Create ActiveUser object
        active_user = ActiveUser(websocket, user, initial_room)
        
        # Track connection
        self.active_connections[websocket] = active_user
        self.user_websockets[user.username] = websocket
    
    async def disconnect(self, websocket: WebSocket) -> Optional[ActiveUser]:
        """
        Handle a WebSocket disconnection and clean up resources.
        
        This method:
        1. Removes connection from tracking dictionaries
        2. Returns the ActiveUser that was disconnected
        
        Args:
            websocket: WebSocket connection that disconnected
            
        Returns:
            ActiveUser object that was disconnected, or None if not found
        
        Requirements: 6.2
        """
        # Get the active user
        active_user = self.active_connections.get(websocket)
        
        if active_user:
            # Remove from tracking dictionaries
            del self.active_connections[websocket]
            
            # Remove from user_websockets if it matches
            if self.user_websockets.get(active_user.user.username) == websocket:
                del self.user_websockets[active_user.user.username]
        
        return active_user
    
    async def send_to_user(self, websocket: WebSocket, message: dict) -> None:
        """
        Send a message to a specific user via their WebSocket connection.
        
        Args:
            websocket: WebSocket connection to send to
            message: Message dictionary to send (will be JSON encoded)
        
        Requirements: 5.1
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            # Connection might be closed, log but don't raise
            print(f"Error sending message to user: {e}")
    
    async def send_to_username(self, username: str, message: dict) -> bool:
        """
        Send a message to a specific user by username.
        
        Args:
            username: Username to send message to
            message: Message dictionary to send (will be JSON encoded)
            
        Returns:
            True if message was sent, False if user not connected
        """
        websocket = self.user_websockets.get(username)
        if websocket:
            await self.send_to_user(websocket, message)
            return True
        return False
    
    async def broadcast_to_room(self, room: str, message: dict, exclude_websocket: Optional[WebSocket] = None) -> None:
        """
        Broadcast a message to all users in a specific room.
        
        Args:
            room: Room name to broadcast to
            message: Message dictionary to send (will be JSON encoded)
            exclude_websocket: Optional WebSocket to exclude from broadcast (e.g., sender)
        
        Requirements: 5.2, 6.3
        """
        # Find all users in the specified room
        for websocket, active_user in self.active_connections.items():
            # Skip if this is the excluded websocket
            if exclude_websocket and websocket == exclude_websocket:
                continue
            
            # Send if user is in the target room
            if active_user.current_room == room:
                await self.send_to_user(websocket, message)
    
    async def broadcast_to_all(self, message: dict, exclude_websocket: Optional[WebSocket] = None) -> None:
        """
        Broadcast a message to all connected users.
        
        Args:
            message: Message dictionary to send (will be JSON encoded)
            exclude_websocket: Optional WebSocket to exclude from broadcast
        
        Requirements: 6.3
        """
        for websocket in list(self.active_connections.keys()):
            # Skip if this is the excluded websocket
            if exclude_websocket and websocket == exclude_websocket:
                continue
            
            await self.send_to_user(websocket, message)
    
    def get_active_users(self) -> List[dict]:
        """
        Get a list of all active users with their current rooms.
        
        Returns:
            List of dicts with username and room information
        
        Requirements: 6.4
        """
        return [
            {
                "username": active_user.user.username,
                "room": active_user.current_room
            }
            for active_user in self.active_connections.values()
        ]
    
    def get_users_in_room(self, room: str) -> List[str]:
        """
        Get a list of usernames currently in a specific room.
        
        Args:
            room: Room name to query
            
        Returns:
            List of usernames in the room
        """
        return [
            active_user.user.username
            for active_user in self.active_connections.values()
            if active_user.current_room == room
        ]
    
    def get_user_room(self, username: str) -> Optional[str]:
        """
        Get the current room of a specific user.
        
        Args:
            username: Username to query
            
        Returns:
            Room name if user is connected, None otherwise
        """
        websocket = self.user_websockets.get(username)
        if websocket:
            active_user = self.active_connections.get(websocket)
            if active_user:
                return active_user.current_room
        return None
    
    def update_user_room(self, websocket: WebSocket, new_room: str) -> bool:
        """
        Update the current room for a user.
        
        Args:
            websocket: WebSocket connection of the user
            new_room: New room name
            
        Returns:
            True if successful, False if user not found
        
        Requirements: 6.5
        """
        active_user = self.active_connections.get(websocket)
        if active_user:
            active_user.current_room = new_room
            return True
        return False
    
    def is_user_connected(self, username: str) -> bool:
        """
        Check if a user is currently connected.
        
        Args:
            username: Username to check
            
        Returns:
            True if user is connected, False otherwise
        """
        return username in self.user_websockets
    
    def get_connection_count(self) -> int:
        """
        Get the total number of active connections.
        
        Returns:
            Number of active connections
        """
        return len(self.active_connections)
