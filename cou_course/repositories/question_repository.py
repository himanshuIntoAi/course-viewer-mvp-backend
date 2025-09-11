from sqlmodel import Session, select, text
from cou_course.models.question import Question, QuestionType
from cou_course.schemas.question_schema import QuestionCreate, QuestionUpdate
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

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
        # Use raw SQL approach to handle question_type to type conversion
        logger.info(f"Fetching question {question_id} using raw SQL approach")
        result = session.execute(text("""
            SELECT id, quiz_id, question_text, type AS question_type, points, answers, 
                   question_order, created_at, created_by, updated_at, updated_by, active
            FROM cou_course.question 
            WHERE id = :question_id AND active = true
        """), {"question_id": question_id})
        
        row = result.fetchone()
        if not row:
            return None
        
        from datetime import datetime, timezone
        
        # Question type mapping
        question_type_mapping = {
            "True/False": QuestionType.TRUE_FALSE,
            "true/false": QuestionType.TRUE_FALSE,
            "TRUE_FALSE": QuestionType.TRUE_FALSE,
            "Multiple Choice": QuestionType.MULTIPLE,
            "multiple_choice": QuestionType.MULTIPLE,
            "MULTIPLE": QuestionType.MULTIPLE,
            "Single Choice": QuestionType.SINGLE,
            "single_choice": QuestionType.SINGLE,
            "SINGLE": QuestionType.SINGLE,
            "Fill in the Blank": QuestionType.FILL_BLANK,
            "fill_blank": QuestionType.FILL_BLANK,
            "FILL_BLANK": QuestionType.FILL_BLANK,
            "Open Ended": QuestionType.OPEN_ENDED,
            "open_ended": QuestionType.OPEN_ENDED,
            "OPEN_ENDED": QuestionType.OPEN_ENDED,
            "Matching Text": QuestionType.MATCHING_TEXT,
            "matching_text": QuestionType.MATCHING_TEXT,
            "MATCHING_TEXT": QuestionType.MATCHING_TEXT,
            "Matching Image": QuestionType.MATCHING_IMAGE,
            "matching_image": QuestionType.MATCHING_IMAGE,
            "MATCHING_IMAGE": QuestionType.MATCHING_IMAGE,
            "Sort Answer": QuestionType.SORT_ANSWER,
            "sort_answer": QuestionType.SORT_ANSWER,
            "SORT_ANSWER": QuestionType.SORT_ANSWER
        }
        
        current_time = datetime.now(timezone.utc)
        
        # Map database question_type to enum
        db_question_type = row[3] or "SINGLE"
        mapped_question_type = question_type_mapping.get(db_question_type, QuestionType.SINGLE)
        
        question_data = {
            "id": row[0],
            "quiz_id": row[1],
            "question_text": row[2] or "Sample Question",
            "type": mapped_question_type,
            "points": row[4] or 1,
            "answers": row[5],
            "question_order": row[6],
            "created_at": row[7] or current_time,
            "created_by": row[8] or 1,
            "updated_at": row[9] or current_time,
            "updated_by": row[10],
            "active": bool(row[11]) if row[11] is not None else True
        }
        
        try:
            question_obj = Question(**question_data)
            logger.info(f"Successfully created question object: {question_obj.id}")
            return question_obj
        except Exception as validation_error:
            logger.error(f"Validation error for question data: {validation_error}")
            return None

    @staticmethod
    def get_questions_by_quiz(session: Session, quiz_id: int) -> List[Question]:
        # Use raw SQL approach to handle question_type to type conversion
        logger.info(f"Fetching questions for quiz {quiz_id} using raw SQL approach")
        result = session.execute(text("""
            SELECT id, quiz_id, question_text, type AS question_type, points, answers, 
                   question_order, created_at, created_by, updated_at, updated_by, active
            FROM cou_course.question 
            WHERE quiz_id = :quiz_id AND active = true
        """), {"quiz_id": quiz_id})
        
        questions = []
        from datetime import datetime, timezone
        
        # Question type mapping
        question_type_mapping = {
            "True/False": QuestionType.TRUE_FALSE,
            "true/false": QuestionType.TRUE_FALSE,
            "TRUE_FALSE": QuestionType.TRUE_FALSE,
            "Multiple Choice": QuestionType.MULTIPLE,
            "multiple_choice": QuestionType.MULTIPLE,
            "MULTIPLE": QuestionType.MULTIPLE,
            "Single Choice": QuestionType.SINGLE,
            "single_choice": QuestionType.SINGLE,
            "SINGLE": QuestionType.SINGLE,
            "Fill in the Blank": QuestionType.FILL_BLANK,
            "fill_blank": QuestionType.FILL_BLANK,
            "FILL_BLANK": QuestionType.FILL_BLANK,
            "Open Ended": QuestionType.OPEN_ENDED,
            "open_ended": QuestionType.OPEN_ENDED,
            "OPEN_ENDED": QuestionType.OPEN_ENDED,
            "Matching Text": QuestionType.MATCHING_TEXT,
            "matching_text": QuestionType.MATCHING_TEXT,
            "MATCHING_TEXT": QuestionType.MATCHING_TEXT,
            "Matching Image": QuestionType.MATCHING_IMAGE,
            "matching_image": QuestionType.MATCHING_IMAGE,
            "MATCHING_IMAGE": QuestionType.MATCHING_IMAGE,
            "Sort Answer": QuestionType.SORT_ANSWER,
            "sort_answer": QuestionType.SORT_ANSWER,
            "SORT_ANSWER": QuestionType.SORT_ANSWER
        }
        
        for row in result.fetchall():
            current_time = datetime.now(timezone.utc)
            
            # Map database question_type to enum
            db_question_type = row[3] or "SINGLE"
            mapped_question_type = question_type_mapping.get(db_question_type, QuestionType.SINGLE)
            
            question_data = {
                "id": row[0],
                "quiz_id": row[1],
                "question_text": row[2] or "Sample Question",
                "type": mapped_question_type,
                "points": row[4] or 1,
                "answers": row[5],
                "question_order": row[6],
                "created_at": row[7] or current_time,
                "created_by": row[8] or 1,
                "updated_at": row[9] or current_time,
                "updated_by": row[10],
                "active": bool(row[11]) if row[11] is not None else True
            }
            
            try:
                question_obj = Question(**question_data)
                questions.append(question_obj)
                logger.info(f"Successfully created question object: {question_obj.id}")
            except Exception as validation_error:
                logger.error(f"Validation error for question data: {validation_error}")
                continue
        
        return questions

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