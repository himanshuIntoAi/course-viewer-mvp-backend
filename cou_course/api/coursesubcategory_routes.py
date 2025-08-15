from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from common.database import get_session
from cou_course.repositories.coursesubcategory_repository import coursesubcategory_repository
from cou_course.schemas.coursesubcategory_schema import CourseSubcategoryCreate, CourseSubcategoryUpdate, CourseSubcategoryInDB

router = APIRouter(
    prefix="/coursesubcategories",
    tags=["Course Subcategories"]
)

@router.post("/", response_model=CourseSubcategoryInDB, summary="Create a new course subcategory")
def create_coursesubcategory(
    *,
    db: Session = Depends(get_session),
    coursesubcategory_in: CourseSubcategoryCreate,
) -> CourseSubcategoryInDB:
    return coursesubcategory_repository.create(db=db, obj_in=coursesubcategory_in)

@router.get("/", response_model=List[CourseSubcategoryInDB], summary="Get all course subcategories")
def read_coursesubcategories(
    db: Session = Depends(get_session),
) -> List[CourseSubcategoryInDB]:
    return coursesubcategory_repository.get_all(db=db)

@router.get("/{coursesubcategory_id}", response_model=CourseSubcategoryInDB, summary="Get a course subcategory by ID")
def read_coursesubcategory(
    *,
    db: Session = Depends(get_session),
    coursesubcategory_id: int,
) -> CourseSubcategoryInDB:
    coursesubcategory = coursesubcategory_repository.get(db=db, id=coursesubcategory_id)
    if not coursesubcategory:
        raise HTTPException(status_code=404, detail="Course subcategory not found")
    return coursesubcategory

@router.put("/{coursesubcategory_id}", response_model=CourseSubcategoryInDB, summary="Update a course subcategory")
def update_coursesubcategory(
    *,
    db: Session = Depends(get_session),
    coursesubcategory_id: int,
    coursesubcategory_in: CourseSubcategoryUpdate,
) -> CourseSubcategoryInDB:
    coursesubcategory = coursesubcategory_repository.get(db=db, id=coursesubcategory_id)
    if not coursesubcategory:
        raise HTTPException(status_code=404, detail="Course subcategory not found")
    return coursesubcategory_repository.update(db=db, db_obj=coursesubcategory, obj_in=coursesubcategory_in)

@router.delete("/{coursesubcategory_id}", response_model=CourseSubcategoryInDB, summary="Delete a course subcategory")
def delete_coursesubcategory(
    *,
    db: Session = Depends(get_session),
    coursesubcategory_id: int,
) -> CourseSubcategoryInDB:
    coursesubcategory = coursesubcategory_repository.delete(db=db, id=coursesubcategory_id)
    if not coursesubcategory:
        raise HTTPException(status_code=404, detail="Course subcategory not found")
    return coursesubcategory 