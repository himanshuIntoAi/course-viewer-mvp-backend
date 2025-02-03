from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

# Shared base schema
class CurrencyBase(SQLModel):
    name: str
    symbol: str
    country_id: Optional[int] = None

# Schema for creating a new currency
class CurrencyCreate(CurrencyBase):
    created_by: Optional[int] = None

# Schema for updating a currency
class CurrencyUpdate(SQLModel):
    name: Optional[str] = None
    symbol: Optional[str] = None
    country_id: Optional[int] = None
    updated_by: Optional[int] = None
    active: Optional[bool] = None

# Schema for reading currency details
class CurrencyRead(CurrencyBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int]
    updated_by: Optional[int]
    active: bool

    class Config:
        orm_mode = True 