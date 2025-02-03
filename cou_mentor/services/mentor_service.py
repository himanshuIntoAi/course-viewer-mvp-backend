from typing import List, Optional, Union
from fastapi import HTTPException
from cou_mentor.repositories.mentor_repository import MentorRepository
from cou_mentor.models.mentor import Mentor

class MentorService:
    @staticmethod
    def get_mentor(session, mentor_id: int) -> Mentor:
        mentor = MentorRepository.get_mentor_by_id(session, mentor_id)
        if not mentor:
            raise HTTPException(status_code=404, detail="Mentor not found")
        return mentor

    @staticmethod
    def create_mentor(session, mentor_data: dict) -> Mentor:
        return MentorRepository.create_mentor(session, mentor_data)

    @staticmethod
    def update_mentor(session, mentor_id: int, mentor_data: dict) -> Mentor:
        mentor = MentorRepository.update_mentor(session, mentor_id, mentor_data)
        if not mentor:
            raise HTTPException(status_code=404, detail="Mentor not found")
        return mentor

    @staticmethod
    def delete_mentor(session, mentor_id: int) -> bool:
        if not MentorRepository.delete_mentor(session, mentor_id):
            raise HTTPException(status_code=404, detail="Mentor not found")
        return True

    @staticmethod
    def search_mentors(session, expertise: Optional[str] = None, min_rating: Optional[float] = None) -> List[Mentor]:
        if expertise:
            return MentorRepository.get_mentors_by_expertise(session, expertise)
        elif min_rating:
            return MentorRepository.get_mentors_by_rating(session, min_rating)
        else:
            return MentorRepository.get_all_mentors(session)
        
    @staticmethod
    def get_all_mentors(session) -> Union[List[Mentor], str]:
        mentors = MentorRepository.get_all_mentors(session)
        if not mentors:
            return "No mentors available"
        return mentors