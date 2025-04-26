from pydantic import BaseModel, Field

class DownloadRequest(BaseModel):
    """
    Request model for downloading a file.
    """
    video_url: str = Field(..., description="URL of the file to download")