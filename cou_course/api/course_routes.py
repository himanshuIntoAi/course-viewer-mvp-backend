from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from cou_course.models.course import Course
from cou_course.schemas.course_schema import CourseCreate, CourseRead, CourseUpdate
from cou_course.repositories.course_repository import CourseRepository
from common.database import get_session

router = APIRouter()

router = APIRouter(
    prefix="/courses",
    tags=["Courses"]
)

@router.post("/", response_model=CourseRead)
def create_course(course: CourseCreate, session: Session = Depends(get_session)):
    course_model = Course(**course.dict())
    return CourseRepository.create_course(session, course_model)

@router.get("/{course_id}", response_model=CourseRead)
def get_course(course_id: int, session: Session = Depends(get_session)):
    course = CourseRepository.get_course_by_id(session, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.get("/", response_model=List[CourseRead])
def get_all_courses(session: Session = Depends(get_session)):
    return CourseRepository.get_all_courses(session)

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
