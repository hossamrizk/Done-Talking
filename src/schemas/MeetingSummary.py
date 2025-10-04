from pydantic import BaseModel, Field

class MeetingSummary(BaseModel):
    meeting_topic: str = Field(..., description="The topic of the meeting.")
    summary: str = Field(..., description="A summary of the meeting, including key points and decisions made.")
