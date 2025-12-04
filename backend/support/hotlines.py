"""
Crisis Hotline Service for Support Bot.

This module provides crisis hotline information for India, including
hotline numbers for self-harm, suicide, and abuse situations.

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

from dataclasses import dataclass
from typing import List, Dict
from backend.support.sentiment import CrisisType


@dataclass
class HotlineInfo:
    """
    Information about a crisis hotline.
    
    Attributes:
        name: Name of the hotline service
        number: Phone number to call
        description: Brief description of the service
    """
    name: str
    number: str
    description: str


class CrisisHotlineService:
    """
    Service providing crisis hotline information for India.
    
    Provides appropriate hotline numbers based on crisis type detected,
    with formatting for clear display to users in crisis.
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
    """
    
    def __init__(self):
        """Initialize the crisis hotline service with Indian hotline numbers."""
        self.hotlines: Dict[CrisisType, List[HotlineInfo]] = {
            CrisisType.SELF_HARM: [
                HotlineInfo(
                    name="AASRA",
                    number="91-9820466726",
                    description="24/7 crisis helpline"
                ),
                HotlineInfo(
                    name="Vandrevala Foundation",
                    number="1860-2662-345",
                    description="Mental health support"
                ),
                HotlineInfo(
                    name="iCall",
                    number="91-22-25521111",
                    description="Psychosocial helpline"
                )
            ],
            CrisisType.SUICIDE: [
                HotlineInfo(
                    name="AASRA",
                    number="91-9820466726",
                    description="24/7 crisis helpline"
                ),
                HotlineInfo(
                    name="Sneha India",
                    number="91-44-24640050",
                    description="Suicide prevention"
                ),
                HotlineInfo(
                    name="Vandrevala Foundation",
                    number="1860-2662-345",
                    description="Mental health support"
                )
            ],
            CrisisType.ABUSE: [
                HotlineInfo(
                    name="Women's Helpline",
                    number="1091",
                    description="For women in distress"
                ),
                HotlineInfo(
                    name="Childline India",
                    number="1098",
                    description="For children in need"
                ),
                HotlineInfo(
                    name="National Commission for Women",
                    number="7827-170-170",
                    description="Women's rights and safety"
                )
            ]
        }
    
    def get_hotlines(self, crisis_type: CrisisType) -> List[HotlineInfo]:
        """
        Get hotline information for a specific crisis type.
        
        Args:
            crisis_type: Type of crisis (SELF_HARM, SUICIDE, or ABUSE)
            
        Returns:
            List of HotlineInfo objects for the crisis type
            
        Requirements: 7.1, 7.2
        """
        if crisis_type == CrisisType.NONE:
            return []
        
        return self.hotlines.get(crisis_type, [])
    
    def format_hotline_message(self, crisis_type: CrisisType) -> str:
        """
        Format hotline information into a clear, supportive message.
        
        Args:
            crisis_type: Type of crisis detected
            
        Returns:
            Formatted message with hotline information and encouragement
            
        Requirements: 7.3, 7.4, 7.5
        """
        if crisis_type == CrisisType.NONE:
            return ""
        
        hotlines = self.get_hotlines(crisis_type)
        
        if not hotlines:
            return ""
        
        # Create crisis-specific introduction
        crisis_intros = {
            CrisisType.SELF_HARM: "I'm concerned about what you've shared. Please reach out to a professional who can provide immediate help.",
            CrisisType.SUICIDE: "I'm very concerned about what you've shared. Please reach out to a professional who can provide immediate help.",
            CrisisType.ABUSE: "I'm concerned about your safety. Please reach out to a professional who can provide immediate help."
        }
        
        intro = crisis_intros.get(crisis_type, "Please reach out to a professional who can provide immediate help.")
        
        # Format hotline information
        hotline_lines = []
        for hotline in hotlines:
            hotline_lines.append(f"• {hotline.name}: {hotline.number} ({hotline.description})")
        
        # Combine into full message
        message = f"{intro}\n\n"
        message += "Here are some resources that can help:\n\n"
        message += "\n".join(hotline_lines)
        message += "\n\nYou don't have to face this alone. These professionals are trained to help and want to support you."
        
        return message
