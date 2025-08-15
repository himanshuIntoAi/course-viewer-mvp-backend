from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from cou_course.models.memory_game_pair import MemoryGamePair
from cou_course.schemas.memory_game_pair_schema import MemoryGamePairCreate, MemoryGamePairRead, MemoryGamePairUpdate
from cou_course.repositories.memory_game_pair_repository import MemoryGamePairRepository
from common.database import get_session
from typing import Optional
import logging

router = APIRouter(
    prefix="/memory-game-pairs",
    tags=["Memory Game Pairs"]
)

@router.post("/", response_model=MemoryGamePairRead)
def create_memory_game_pair(
    memory_game_pair: MemoryGamePairCreate, 
    session: Session = Depends(get_session)
):
    """Create a new memory game pair"""
    return MemoryGamePairRepository.create_memory_game_pair(session, memory_game_pair)

@router.get("/{memory_game_pair_id}", response_model=MemoryGamePairRead)
def get_memory_game_pair(
    memory_game_pair_id: int, 
    session: Session = Depends(get_session)
):
    """Get a memory game pair by ID"""
    memory_game_pair = MemoryGamePairRepository.get_memory_game_pair_by_id(session, memory_game_pair_id)
    if not memory_game_pair:
        raise HTTPException(status_code=404, detail="Memory game pair not found")
    return memory_game_pair

@router.get("/", response_model=List[MemoryGamePairRead])
def get_all_memory_game_pairs(
    session: Session = Depends(get_session), 
    skip: int = 0, 
    limit: int = 100
):
    """Get all memory game pairs with pagination"""
    return MemoryGamePairRepository.get_all_memory_game_pairs(session, skip, limit)

@router.get("/game/{memory_game_id}", response_model=List[MemoryGamePairRead])
def get_memory_game_pairs_by_game(
    memory_game_id: int, 
    session: Session = Depends(get_session)
):
    """Get all memory game pairs for a specific memory game"""
    return MemoryGamePairRepository.get_memory_game_pairs_by_game(session, memory_game_id)

@router.get("/search/{term}", response_model=List[MemoryGamePairRead])
def search_memory_game_pairs_by_term(
    term: str, 
    session: Session = Depends(get_session)
):
    """Search memory game pairs by term"""
    return MemoryGamePairRepository.get_memory_game_pairs_by_term(session, term)

@router.put("/{memory_game_pair_id}", response_model=MemoryGamePairRead)
def update_memory_game_pair(
    memory_game_pair_id: int, 
    memory_game_pair_update: MemoryGamePairUpdate, 
    session: Session = Depends(get_session)
):
    """Update a memory game pair"""
    updated_memory_game_pair = MemoryGamePairRepository.update_memory_game_pair(
        session, memory_game_pair_id, memory_game_pair_update
    )
    if not updated_memory_game_pair:
        raise HTTPException(status_code=404, detail="Memory game pair not found")
    return updated_memory_game_pair

@router.delete("/{memory_game_pair_id}", response_model=dict)
def delete_memory_game_pair(
    memory_game_pair_id: int, 
    session: Session = Depends(get_session)
):
    """Delete a memory game pair (soft delete)"""
    if not MemoryGamePairRepository.delete_memory_game_pair(session, memory_game_pair_id):
        raise HTTPException(status_code=404, detail="Memory game pair not found")
    return {"message": "Memory game pair deleted successfully"} 