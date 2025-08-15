from sqlmodel import Session, select
from cou_course.models.memory_game_pair import MemoryGamePair
from cou_course.schemas.memory_game_pair_schema import MemoryGamePairCreate, MemoryGamePairUpdate
from typing import List, Optional

class MemoryGamePairRepository:
    @staticmethod
    def create_memory_game_pair(session: Session, memory_game_pair: MemoryGamePairCreate) -> MemoryGamePair:
        db_memory_game_pair = MemoryGamePair(**memory_game_pair.dict())
        session.add(db_memory_game_pair)
        session.commit()
        session.refresh(db_memory_game_pair)
        return db_memory_game_pair

    @staticmethod
    def get_memory_game_pair_by_id(session: Session, memory_game_pair_id: int) -> Optional[MemoryGamePair]:
        return session.get(MemoryGamePair, memory_game_pair_id)

    @staticmethod
    def get_memory_game_pairs_by_game(session: Session, memory_game_id: int) -> List[MemoryGamePair]:
        statement = select(MemoryGamePair).where(
            MemoryGamePair.memory_game_id == memory_game_id, 
            MemoryGamePair.active == True
        ).order_by(MemoryGamePair.pair_order)
        return list(session.exec(statement))

    @staticmethod
    def get_all_memory_game_pairs(session: Session, skip: int = 0, limit: int = 100) -> List[MemoryGamePair]:
        statement = select(MemoryGamePair).where(MemoryGamePair.active == True).offset(skip).limit(limit)
        return list(session.exec(statement))

    @staticmethod
    def update_memory_game_pair(session: Session, memory_game_pair_id: int, memory_game_pair_update: MemoryGamePairUpdate) -> Optional[MemoryGamePair]:
        db_memory_game_pair = session.get(MemoryGamePair, memory_game_pair_id)
        if not db_memory_game_pair:
            return None
        
        update_data = memory_game_pair_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_memory_game_pair, field, value)
        
        session.add(db_memory_game_pair)
        session.commit()
        session.refresh(db_memory_game_pair)
        return db_memory_game_pair

    @staticmethod
    def delete_memory_game_pair(session: Session, memory_game_pair_id: int) -> bool:
        db_memory_game_pair = session.get(MemoryGamePair, memory_game_pair_id)
        if not db_memory_game_pair:
            return False
        
        db_memory_game_pair.active = False
        session.add(db_memory_game_pair)
        session.commit()
        return True

    @staticmethod
    def get_memory_game_pairs_by_term(session: Session, term: str) -> List[MemoryGamePair]:
        statement = select(MemoryGamePair).where(
            MemoryGamePair.term.ilike(f"%{term}%"), 
            MemoryGamePair.active == True
        )
        return list(session.exec(statement)) 