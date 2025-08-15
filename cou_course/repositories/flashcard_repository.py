from sqlmodel import Session, select
from cou_course.models.flashcard import Flashcard
from cou_course.schemas.flashcard_schema import FlashcardCreate, FlashcardUpdate
from typing import List, Optional

class FlashcardRepository:
    @staticmethod
    def create_flashcard(session: Session, flashcard: FlashcardCreate) -> Flashcard:
        db_flashcard = Flashcard(**flashcard.dict())
        session.add(db_flashcard)
        session.commit()
        session.refresh(db_flashcard)
        return db_flashcard

    @staticmethod
    def get_flashcard_by_id(session: Session, flashcard_id: int) -> Optional[Flashcard]:
        return session.get(Flashcard, flashcard_id)

    @staticmethod
    def get_flashcards_by_course(session: Session, course_id: int) -> List[Flashcard]:
        statement = select(Flashcard).where(Flashcard.course_id == course_id, Flashcard.active == True)
        return list(session.exec(statement))

    @staticmethod
    def update_flashcard(session: Session, flashcard_id: int, flashcard_update: FlashcardUpdate) -> Optional[Flashcard]:
        db_flashcard = session.get(Flashcard, flashcard_id)
        if not db_flashcard:
            return None
        
        update_data = flashcard_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_flashcard, field, value)
        
        session.add(db_flashcard)
        session.commit()
        session.refresh(db_flashcard)
        return db_flashcard

    @staticmethod
    def delete_flashcard(session: Session, flashcard_id: int) -> bool:
        db_flashcard = session.get(Flashcard, flashcard_id)
        if not db_flashcard:
            return False
        
        db_flashcard.active = False
        session.add(db_flashcard)
        session.commit()
        return True 