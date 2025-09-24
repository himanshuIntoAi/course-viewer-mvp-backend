from typing import Optional, List
from datetime import datetime, date, time
from pydantic import BaseModel
from enum import Enum

class DurationUnit(str, Enum):
    DAYS = "Days"
    HOURS = "Hours"
    WEEKS = "Weeks"
    MONTHS = "Months"

class RecurrenceType(str, Enum):
    WEEKLY = "Weekly"
    DAILY = "Daily"
    MONTHLY = "Monthly"
    YEARLY = "Yearly"


class InstructorInfo(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    profession: Optional[str] = None


class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[int]
    subcategory_id: Optional[int]
    course_type_id: Optional[int]
    sells_type_id: Optional[int]
    mentor_id: Optional[int]
    language_id: Optional[int]
    is_flagship: Optional[bool] = False
    active: Optional[bool] = True
    price: Optional[float] = 0
    ratings: Optional[float] = 0.0
    IT: Optional[bool] = False
    Coding_Required: Optional[bool] = False
    Avg_Completion_Time: Optional[int] = None
    Course_level: Optional[str] = None
    
class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    pass

class CourseRead(CourseBase):
    id: int
    created_at: datetime
    updated_at: datetime
    instructor: Optional[InstructorInfo] = None

    class Config:
        from_attributes = True


class SubcategorySummary(BaseModel):
    id: int
    name: str

class CourseDetailsRead(BaseModel):
    """Comprehensive course details schema matching the database table structure"""
    id: int
    title: str
    what_will_you_learn: Optional[str] = None
    category_id: Optional[int] = None
    subcategory_id: Optional[int] = None
    course_type_id: Optional[int] = None
    sells_type_id: Optional[int] = None
    mentor_id: Optional[int] = None
    language_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    is_flagship: Optional[bool] = False
    active: Optional[bool] = True
    price: Optional[float] = 0
    ratings: Optional[int] = None
    slug: Optional[str] = None
    discount: Optional[float] = None
    introduction_video_link: Optional[str] = None
    prerequisites: Optional[str] = None
    description: Optional[str] = None
    skill_level: Optional[str] = None
    max_students: Optional[float] = None
    thumbnail: Optional[str] = None
    time: Optional[float] = None
    is_live: Optional[bool] = None
    IT: Optional[bool] = None
    Coding_Required: Optional[bool] = None
    Avg_Completion_TIme: Optional[int] = None
    Course_level: Optional[str] = None
    audience: Optional[str] = None
    duration_hours: Optional[float] = None
    course_bundle: Optional[str] = None
    course_1: Optional[str] = None
    course_duration: Optional[int] = None
    duration_unit: Optional[DurationUnit] = DurationUnit.DAYS
    recurrence: Optional[RecurrenceType] = RecurrenceType.WEEKLY
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    intro_video_source: Optional[str] = None
    intro_video_url: Optional[str] = None
    intro_video_filename: Optional[str] = None
    tags: Optional[List[str]] = None
    learning_outcomes: Optional[str] = None
    targeted_audience: Optional[List[str]] = None
    material_included: Optional[str] = None
    requirements_text: Optional[str] = None
    expiration_setting: Optional[str] = "Expiration"
    expiration_date: Optional[date] = None
    expiration_time: Optional[time] = None
    student_interaction_with_tutor: Optional[bool] = False
    co_peer_interaction: Optional[bool] = False
    student_upload_file_access: Optional[bool] = False
    skip_topics: Optional[bool] = False
    skip_lessons: Optional[bool] = False
    mandatory_attendance: Optional[bool] = False
    installments_availability: Optional[bool] = False
    refund_upon_cancellation: Optional[bool] = False
    course_switch: Optional[bool] = False
    timeline_extension: Optional[bool] = False
    publish_date: Optional[date] = None
    publish_time: Optional[time] = None
    enrollment_expiration: Optional[int] = 0
    is_public_course: Optional[bool] = True
    has_qa: Optional[bool] = True
    regular_price: Optional[float] = None
    sale_price: Optional[float] = None
    pricing_type: str = "PAID"
    instructor_type: Optional[str] = None
    publish_type: str = "Public"
    
    # Additional fields for enhanced response
    instructor: Optional[InstructorInfo] = None

    class Config:
        from_attributes = True
