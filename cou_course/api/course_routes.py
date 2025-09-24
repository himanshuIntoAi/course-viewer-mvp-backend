from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List
from cou_course.schemas.course_schema import CourseRead, SubcategorySummary
from cou_course.repositories.course_repository import CourseRepository
from common.database import get_session
from typing import Optional, List
from fastapi import Query
import logging

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

 

@router.get("/subcategories", response_model=List[SubcategorySummary])
def get_unique_subcategories(session: Session = Depends(get_session)):
    """
    Get unique course subcategory names used by all courses.
    Returns distinct subcategory names for catalog filtering.
    """
    return CourseRepository.get_unique_subcategories(session)

@router.get("/subcategories/{subcategory_id}", response_model=List[CourseRead])
def get_courses_by_subcategory_id(subcategory_id: int, session: Session = Depends(get_session), skip: int = 0, limit: int = 10):
    return CourseRepository.get_courses_by_subcategory_id(session, subcategory_id, skip, limit)

@router.get("/", response_model=List[CourseRead])
def get_all_courses(session: Session = Depends(get_session), skip: int = 0, limit: int = 10):
    return CourseRepository.get_all_courses(session , skip , limit)

@router.get("/search", response_model=List[CourseRead])
def search_courses(q: str = Query(..., min_length=1), session: Session = Depends(get_session), skip: int = 0, limit: int = 10):
    return CourseRepository.search_courses_by_title(session, q, skip, limit)

 

 


