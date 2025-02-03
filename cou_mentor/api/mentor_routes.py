from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from cou_mentor.repositories.mentor_repository import MentorRepository
from cou_mentor.services.mentor_service import MentorService
from cou_mentor.models.mentor import Mentor
from cou_mentor.schemas.mentor_schema import MentorCreate, MentorUpdate, MentorRead
from common.database import get_session

router = APIRouter()

router = APIRouter(
    prefix="/mentors",
    tags=["Mentors"]
)

@router.post("/", response_model=MentorRead)
def create_mentor(mentor: MentorCreate, session: Session = Depends(get_session)):
    return MentorRepository.create_mentor(session, mentor.dict())

@router.get("/{mentor_id}", response_model=MentorRead)
def get_mentor(mentor_id: int, session: Session = Depends(get_session)):
    mentor = MentorRepository.get_mentor_by_id(session, mentor_id)
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    return mentor

@router.put("/{mentor_id}", response_model=MentorRead)
def update_mentor(mentor_id: int, mentor: MentorUpdate, session: Session = Depends(get_session)):
    updated_mentor = MentorRepository.update_mentor(session, mentor_id, mentor.dict(exclude_unset=True))
    if not updated_mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    return updated_mentor

@router.delete("/{mentor_id}")
def delete_mentor(mentor_id: int, session: Session = Depends(get_session)):
    if not MentorRepository.delete_mentor(session, mentor_id):
        raise HTTPException(status_code=404, detail="Mentor not found")
    return {"message": "Mentor deleted successfully"}

@router.get("/", response_model=Union[List[Mentor], str])
def get_all_mentors(session: Session = Depends(get_session)):
    return MentorService.get_all_mentors(session)