from typing import Optional, List
from sqlmodel import Session, select
from cou_course.models.course import Course

class CourseRepository:
    @staticmethod
    def create_course(session: Session, course: Course) -> Course:
        session.add(course)
        session.commit()
        session.refresh(course)
        return course

    @staticmethod
    def get_course_by_id(session: Session, course_id: int) -> Optional[Course]:
        return session.get(Course, course_id)

     
    @staticmethod
    def get_all_courses(session: Session) -> List[Course]:
        statement = select(Course)
        return session.exec(statement).all()

    @staticmethod
    def update_course(session: Session, course_id: int, updates: dict) -> Optional[Course]:
        course = session.get(Course, course_id)
        if course:
            for key, value in updates.items():
                setattr(course, key, value)
            session.commit()
            session.refresh(course)
        return course

    @staticmethod
    def delete_course(session: Session, course_id: int) -> bool:
        course = session.get(Course, course_id)
        if course:
            session.delete(course)
            session.commit()
            return True
        return False
    
    @staticmethod
    def get_courses_by_mentor(session: Session, mentor_id: int):
        return session.exec(select(Course).where(Course.mentor_id == mentor_id)).all()
