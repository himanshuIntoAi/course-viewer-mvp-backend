from sqlmodel import Session, select
from cou_course.models.question import Question
from cou_course.schemas.question_schema import QuestionCreate, QuestionUpdate
from typing import List, Optional

class QuestionRepository:
    @staticmethod
    def create_question(session: Session, question: QuestionCreate) -> Question:
        db_question = Question(**question.dict())
        session.add(db_question)
        session.commit()
        session.refresh(db_question)
        return db_question

    @staticmethod
    def get_question_by_id(session: Session, question_id: int) -> Optional[Question]:
        return session.get(Question, question_id)

    @staticmethod
    def get_questions_by_quiz(session: Session, quiz_id: int) -> List[Question]:
        statement = select(Question).where(Question.quiz_id == quiz_id, Question.active == True)
        return list(session.exec(statement))

    @staticmethod
    def update_question(session: Session, question_id: int, question_update: QuestionUpdate) -> Optional[Question]:
        db_question = session.get(Question, question_id)
        if not db_question:
            return None
        
        update_data = question_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_question, field, value)
        
        session.add(db_question)
        session.commit()
        session.refresh(db_question)
        return db_question

    @staticmethod
    def delete_question(session: Session, question_id: int) -> bool:
        db_question = session.get(Question, question_id)
        if not db_question:
            return False
        
        db_question.active = False
        session.add(db_question)
        session.commit()
        return True 