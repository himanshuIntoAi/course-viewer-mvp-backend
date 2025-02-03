from sqlmodel import Session, select
from typing import List, Optional
from cou_mentor.models.mentor import Mentor

class MentorRepository:
    @staticmethod
    def get_mentor_by_id(session: Session, mentor_id: int) -> Optional[Mentor]:
        """
        Retrieve a mentor by their ID.
        """
        return session.get(Mentor, mentor_id)

    @staticmethod
    def get_all_mentors(session: Session) -> List[Mentor]:
        """
        Retrieve all mentors.
        """
        return session.exec(select(Mentor)).all()

    @staticmethod
    def create_mentor(session: Session, mentor_data: dict) -> Mentor:
        """
        Create a new mentor.
        """
        mentor = Mentor(**mentor_data)
        session.add(mentor)
        session.commit()
        session.refresh(mentor)
        return mentor

    @staticmethod
    def update_mentor(session: Session, mentor_id: int, mentor_data: dict) -> Optional[Mentor]:
        """
        Update an existing mentor.
        """
        mentor = session.get(Mentor, mentor_id)
        if mentor:
            for key, value in mentor_data.items():
                setattr(mentor, key, value)
            session.commit()
            session.refresh(mentor)
        return mentor

    @staticmethod
    def delete_mentor(session: Session, mentor_id: int) -> bool:
        """
        Delete a mentor by their ID.
        """
        mentor = session.get(Mentor, mentor_id)
        if mentor:
            session.delete(mentor)
            session.commit()
            return True
        return False

    @staticmethod
    def get_mentors_by_expertise(session: Session, expertise: str) -> List[Mentor]:
        """
        Retrieve mentors by their expertise.
        """
        return session.exec(select(Mentor).where(Mentor.expertise == expertise)).all()

    @staticmethod
    def get_mentors_by_rating(session: Session, min_rating: float) -> List[Mentor]:
        """
        Retrieve mentors with a rating greater than or equal to the specified value.
        """
        return session.exec(select(Mentor).where(Mentor.rating >= min_rating)).all()

    @staticmethod
    def get_available_mentors(session: Session) -> List[Mentor]:
        """
        Retrieve all available mentors.
        """
        return session.exec(select(Mentor).where(Mentor.is_available == True)).all()
    
    @staticmethod
    def get_all_mentors(session: Session) -> List[Mentor]:
        """
        Retrieve all mentors.
        """
        return session.exec(select(Mentor)).all()