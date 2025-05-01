from typing import List
from pydantic import BaseModel, Field

class MeetingSummary(BaseModel):
    meeting_topic: str = Field(...)
    key_speakers: List[str] = Field(...)
    key_decisions: List[str] = Field(...)
    action_items: List[str] = Field(...)
    discussion_highlights: List[str] = Field(...)
