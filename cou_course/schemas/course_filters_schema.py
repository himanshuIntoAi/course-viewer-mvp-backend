from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class FilterOption(BaseModel):
    id: str
    label: str

class PriceOption(FilterOption):
    value: Optional[float]

class CompletionTimeRange(FilterOption):
    min: int
    max: int

class CourseFilters(BaseModel):
    it_non_it: List[FilterOption]
    coding_non_coding: List[FilterOption]
    criteria: dict
    preferences: dict

    class Config:
        orm_mode = True

class CourseFilterRequest(BaseModel):
    it_non_it: Optional[bool] = None
    coding_non_coding: Optional[bool] = None
    category_id: Optional[int] = None
    level: Optional[Literal["beginner", "intermediate", "advanced"]] = None
    price_type: Optional[Literal["free", "paid"]] = None
    completion_time: Optional[Literal["less_than_5", "5_10", "11_15", "16_22"]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

    class Config:
        schema_extra = {
            "example": {
                "it_non_it": "it",
                "coding_non_coding": "coding",
                "category_id": 1,
                "level": "beginner",
                "price_type": "free",
                "completion_time": "5_10",
                "min_price": 10,
                "max_price": 1000
            }
        } 