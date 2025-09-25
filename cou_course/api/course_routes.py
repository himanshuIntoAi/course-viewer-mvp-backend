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

@router.get("/categories/{category_id}", response_model=List[CourseRead])
def get_courses_by_category_id(category_id: int, session: Session = Depends(get_session), skip: int = 0, limit: int = 10):
    """
    Get all courses that belong to the specified category.
    
    Args:
        category_id: The ID of the category to filter by
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        List of courses in the specified category
    """
    return CourseRepository.get_courses_by_category_id(session, category_id, skip, limit)

@router.get("/", response_model=List[CourseRead])
def get_all_courses(session: Session = Depends(get_session), skip: int = 0, limit: int = 10):
    return CourseRepository.get_all_courses(session , skip , limit)

@router.get("/search", response_model=List[CourseRead])
def search_courses(q: str = Query(..., min_length=1), session: Session = Depends(get_session), skip: int = 0, limit: int = 10):
    """
    Enhanced search endpoint that handles both text search and ID-based course fetching.
    
    - If query is numeric: Returns the specific course by ID
    - If query is text: Performs title-based search with pagination
    
    Args:
        q: Search query (can be course ID as number or text search term)
        skip: Number of records to skip for pagination (only applies to text search)
        limit: Maximum number of records to return (only applies to text search)
        
    Returns:
        List of courses matching the search criteria
    """
    # Check if the query is numeric (course ID)
    if q.strip().isdigit():
        course_id = int(q.strip())
        course = CourseRepository.get_course_by_id(session, course_id)
        if course:
            return [course]
        else:
            return []  # Course not found
    else:
        # Perform text-based search
        return CourseRepository.search_courses_by_title(session, q, skip, limit)

@router.get("/count")
def get_course_count(session: Session = Depends(get_session)):
    """
    Debug endpoint to get the total count of courses in the database.
    This helps identify if the issue is with data retrieval or pagination.
    """
    result = CourseRepository.get_course_count(session)
    result["message"] = f"Total courses: {result['total_courses']}, With mentors: {result['courses_with_mentors']}, Without mentors: {result['courses_without_mentors']}"
    return result

 

 


