from sqlmodel import Session, select
from cou_course.models.memory_game import MemoryGame
from cou_course.schemas.memory_game_schema import MemoryGameCreate, MemoryGameUpdate
from typing import List, Optional

class MemoryGameRepository:
    @staticmethod
    def create_memory_game(session: Session, memory_game: MemoryGameCreate) -> MemoryGame:
        db_memory_game = MemoryGame(**memory_game.dict())
        session.add(db_memory_game)
        session.commit()
        session.refresh(db_memory_game)
        return db_memory_game

    @staticmethod
    def get_memory_game_by_id(session: Session, memory_game_id: int) -> Optional[MemoryGame]:
        return session.get(MemoryGame, memory_game_id)

    @staticmethod
    def get_memory_games_by_course(session: Session, course_id: int) -> List[MemoryGame]:
        statement = select(MemoryGame).where(MemoryGame.course_id == course_id, MemoryGame.active == True)
        return list(session.exec(statement))

    @staticmethod
    def update_memory_game(session: Session, memory_game_id: int, memory_game_update: MemoryGameUpdate) -> Optional[MemoryGame]:
        db_memory_game = session.get(MemoryGame, memory_game_id)
        if not db_memory_game:
            return None
        
        update_data = memory_game_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_memory_game, field, value)
        
        session.add(db_memory_game)
        session.commit()
        session.refresh(db_memory_game)
        return db_memory_game

    @staticmethod
    def delete_memory_game(session: Session, memory_game_id: int) -> bool:
        db_memory_game = session.get(MemoryGame, memory_game_id)
        if not db_memory_game:
            return False
        
        db_memory_game.active = False
        session.add(db_memory_game)
        session.commit()
        return True 