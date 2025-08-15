from sqlmodel import Session, select
from cou_course.models.lesson import Lesson
from cou_course.schemas.lesson_schema import LessonCreate, LessonUpdate
from typing import List, Optional

class LessonRepository:
    @staticmethod
    def create_lesson(session: Session, lesson: LessonCreate) -> Lesson:
        db_lesson = Lesson(**lesson.dict())
        session.add(db_lesson)
        session.commit()
        session.refresh(db_lesson)
        return db_lesson

    @staticmethod
    def get_lesson_by_id(session: Session, lesson_id: int) -> Optional[Lesson]:
        return session.get(Lesson, lesson_id)

    @staticmethod
    def get_lessons_by_course(session: Session, course_id: int) -> List[Lesson]:
        statement = select(Lesson).where(Lesson.course_id == course_id, Lesson.active == True)
        return list(session.exec(statement))

    @staticmethod
    def update_lesson(session: Session, lesson_id: int, lesson_update: LessonUpdate) -> Optional[Lesson]:
        db_lesson = session.get(Lesson, lesson_id)
        if not db_lesson:
            return None
        
        update_data = lesson_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_lesson, field, value)
        
        session.add(db_lesson)
        session.commit()
        session.refresh(db_lesson)
        return db_lesson

    @staticmethod
    def delete_lesson(session: Session, lesson_id: int) -> bool:
        db_lesson = session.get(Lesson, lesson_id)
        if not db_lesson:
            return False
        
        db_lesson.active = False
        session.add(db_lesson)
        session.commit()
        return True 