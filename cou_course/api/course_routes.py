from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from cou_course.models.course import Course
from cou_course.schemas.course_schema import CourseCreate, CourseRead, CourseUpdate
from cou_course.repositories.course_repository import CourseRepository
from common.database import get_session
from typing import Optional, List
from fastapi import Query
import logging
from cou_course.schemas.course_filters_schema import CourseFilters, CourseFilterRequest

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

@router.post("/", response_model=CourseRead)
def create_course(course: CourseCreate, session: Session = Depends(get_session)):
    course_model = Course(**course.dict())
    return CourseRepository.create_course(session, course_model)

@router.post("/filter", response_model=List[CourseRead])
def filter_courses(
    filters: CourseFilterRequest,
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    """
    Filter courses based on multiple criteria:
    - IT/Non-IT category
    - Coding/Non-Coding category
    - Course category
    - Course level
    - Price type (free/paid)
    - Price range
    - Completion time range
    """
    return CourseRepository.filter_courses(
        session=session,
        category_id=filters.category_id,
        it_non_it=filters.it_non_it,
        coding_non_coding=filters.coding_non_coding,
        level=filters.level,
        price_type=filters.price_type,
        min_price=filters.min_price,
        max_price=filters.max_price,
        completion_time=filters.completion_time,
        active=True,  # Only show active courses
        skip=skip,
        limit=limit
    )

@router.get("/filters", response_model=CourseFilters)
def get_filters(session: Session = Depends(get_session)):
    return CourseRepository.get_filters(session)

@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, session: Session = Depends(get_session)):
    course = CourseRepository.get_course_by_id(session, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/", response_model=List[CourseRead])
def get_all_courses(session: Session = Depends(get_session), skip: int = 0, limit: int = 10):
    return CourseRepository.get_all_courses(session , skip , limit)

@router.put("/{course_id}", response_model=CourseRead)  
def update_course(course_id: int, course_update: CourseUpdate, session: Session = Depends(get_session)):
    updates = course_update.dict(exclude_unset=True)
    updated_course = CourseRepository.update_course(session, course_id, updates)
    if not updated_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return updated_course

@router.delete("/{course_id}", response_model=dict)
def delete_course(course_id: int, session: Session = Depends(get_session)):
    if not CourseRepository.delete_course(session, course_id):
        raise HTTPException(status_code=404, detail="Course not found")
    return {"message": "Course deleted successfully"}


