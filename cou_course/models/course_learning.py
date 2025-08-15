from pydantic import BaseModel
from typing import List

class VideoInfo(BaseModel):
    name : str
    url : str
    content_type : str
    size : int

class VideoListResponse(BaseModel):
    videos : List[VideoInfo]