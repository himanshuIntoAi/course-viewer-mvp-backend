from sqlmodel import Session, select
from ..models.coursecategory import CourseCategory

class CourseCategoryRepository:

    @staticmethod
    def get_all(session: Session):
        return session.exec(select(CourseCategory)).all()

    @staticmethod
    def get_by_id(session: Session, category_id: int):
        return session.get(CourseCategory, category_id)

    @staticmethod
    def create(session: Session, category: CourseCategory):
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    @staticmethod
    def update(session: Session, category: CourseCategory, updates: dict):
        for key, value in updates.items():
            setattr(category, key, value)
        session.add(category)
        session.commit()
        session.refresh(category)
        return category

    @staticmethod
    def delete(session: Session, category_id: int):
        category = session.get(CourseCategory, category_id)
        if category:
            session.delete(category)
            session.commit()
        return category
