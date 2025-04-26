from typing import List, Optional
from pydantic import BaseModel

class MeetingSummary(BaseModel):
    meeting_topic: str
    key_speakers: List[str]  
    key_decisions: List[str]  
    action_items: List[str]   
    discussion_highlights: List[str]
