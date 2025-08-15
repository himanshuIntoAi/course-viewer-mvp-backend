from sqlmodel import Session, select
from cou_course.models.quiz import Quiz
from cou_course.schemas.quiz_schema import QuizCreate, QuizUpdate
from typing import List, Optional

class QuizRepository:
    @staticmethod
    def create_quiz(session: Session, quiz: QuizCreate) -> Quiz:
        db_quiz = Quiz(**quiz.dict())
        session.add(db_quiz)
        session.commit()
        session.refresh(db_quiz)
        return db_quiz

    @staticmethod
    def get_quiz_by_id(session: Session, quiz_id: int) -> Optional[Quiz]:
        return session.get(Quiz, quiz_id)

    @staticmethod
    def get_quizzes_by_course(session: Session, course_id: int) -> List[Quiz]:
        statement = select(Quiz).where(Quiz.course_id == course_id, Quiz.active == True)
        return list(session.exec(statement))

    @staticmethod
    def update_quiz(session: Session, quiz_id: int, quiz_update: QuizUpdate) -> Optional[Quiz]:
        db_quiz = session.get(Quiz, quiz_id)
        if not db_quiz:
            return None
        
        update_data = quiz_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_quiz, field, value)
        
        session.add(db_quiz)
        session.commit()
        session.refresh(db_quiz)
        return db_quiz

    @staticmethod
    def delete_quiz(session: Session, quiz_id: int) -> bool:
        db_quiz = session.get(Quiz, quiz_id)
        if not db_quiz:
            return False
        
        db_quiz.active = False
        session.add(db_quiz)
        session.commit()
        return True 