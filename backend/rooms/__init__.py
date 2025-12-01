"""
Rooms module for Phantom Link BBS.

This module provides room management functionality.
"""

from backend.rooms.models import Room
from backend.rooms.service import RoomService

__all__ = ["Room", "RoomService"]
