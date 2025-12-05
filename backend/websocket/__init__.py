"""
WebSocket module for Obsidian BBS.

This module provides WebSocket connection management and message broadcasting.
"""

from backend.websocket.manager import WebSocketManager, ActiveUser

__all__ = ["WebSocketManager", "ActiveUser"]
