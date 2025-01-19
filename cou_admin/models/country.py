# cou_admin/models/country.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Country(SQLModel, table=True):
    __tablename__ = "country"
    __table_args__ = {"schema": "cou_admin"} 
  
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[int]
    updated_by: Optional[int]
    active: bool = Field(default=True)