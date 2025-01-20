from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from common.database import get_session
from cou_course.models.coursecategory import CourseCategory
from ..repositories.coursecategory_repository import CourseCategoryRepository
from ..schemas.coursecategory_schema import (
    CourseCategoryCreate,
    CourseCategoryRead,
    CourseCategoryUpdate,
)

router = APIRouter(prefix="/coursecategories", tags=["Course Categories"])

@router.get("/", response_model=list[CourseCategoryRead])
def read_all_coursecategories(session: Session = Depends(get_session)):
    return CourseCategoryRepository.get_all(session)

@router.get("/{category_id}", response_model=CourseCategoryRead)
def read_coursecategory(category_id: int, session: Session = Depends(get_session)):
    category = CourseCategoryRepository.get_by_id(session, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course Category not found"
        )
    return category

@router.post("/", response_model=CourseCategoryRead, status_code=status.HTTP_201_CREATED)
def create_coursecategory(
    category_data: CourseCategoryCreate, session: Session = Depends(get_session)
):
    category = CourseCategory(**category_data.dict())
    return CourseCategoryRepository.create(session, category)

@router.put("/{category_id}", response_model=CourseCategoryRead)
def update_coursecategory(
    category_id: int, updates: CourseCategoryUpdate, session: Session = Depends(get_session)
):
    category = CourseCategoryRepository.get_by_id(session, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course Category not found"
        )
    return CourseCategoryRepository.update(session, category, updates.dict(exclude_unset=True))

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coursecategory(category_id: int, session: Session = Depends(get_session)):
    category = CourseCategoryRepository.delete(session, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Course Category not found"
        )
