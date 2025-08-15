from typing import List, Optional
from sqlmodel import Session, select

from cou_course.models.coursesubcategory import CourseSubcategory
from cou_course.schemas.coursesubcategory_schema import CourseSubcategoryCreate, CourseSubcategoryUpdate

class CourseSubcategoryRepository:
    def create(self, db: Session, *, obj_in: CourseSubcategoryCreate) -> CourseSubcategory:
        db_obj = CourseSubcategory(
            name=obj_in.name,
            category_id=obj_in.category_id,
            is_flagship=obj_in.is_flagship,
            active=obj_in.active,
            created_by=obj_in.created_by
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Optional[CourseSubcategory]:
        return db.exec(select(CourseSubcategory).where(CourseSubcategory.id == id)).first()

    def get_all(self, db: Session) -> List[CourseSubcategory]:
        return db.exec(select(CourseSubcategory)).all()

    def update(self, db: Session, *, db_obj: CourseSubcategory, obj_in: CourseSubcategoryUpdate) -> CourseSubcategory:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> CourseSubcategory:
        obj = db.get(CourseSubcategory, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj

coursesubcategory_repository = CourseSubcategoryRepository() 