# cou_admin/schemas/country_schema.py
from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

# Shared base schema
class CountryBase(SQLModel):
    name: str

# Schema for creating a new country
class CountryCreate(CountryBase):
    created_by: Optional[int] = None

# Schema for updating a country
class CountryUpdate(SQLModel):
    name: Optional[str] = None
    updated_by: Optional[int] = None
    active: Optional[bool] = None

# Schema for reading country details
class CountryRead(CountryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    updated_by: Optional[int]
    active: bool

    class Config:
        orm_mode = True
