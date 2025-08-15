from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class MindmapBase(BaseModel):
    course_id: int
    topic_id: int
    mindmap_mermaid: Optional[str] = None
    mindmap_json: Dict[str, Any] = Field(..., description="JSONB field for mindmap data")
    is_completed: Optional[bool] = False
    active: Optional[bool] = True

class MindmapCreate(MindmapBase):
    created_by: int

class MindmapUpdate(BaseModel):
    mindmap_mermaid: Optional[str] = None
    mindmap_json: Optional[Dict[str, Any]] = None
    is_completed: Optional[bool] = None
    active: Optional[bool] = None
    updated_by: Optional[int] = None

class MindmapRead(MindmapBase):
    id: int
    created_at: datetime
    created_by: int
    updated_at: datetime
    updated_by: Optional[int] = None

    class Config:
        orm_mode = True 