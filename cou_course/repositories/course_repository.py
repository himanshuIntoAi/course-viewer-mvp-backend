from typing import Optional, List
from sqlmodel import Session, select
from cou_course.models.course import Course
from cou_mentor.models.mentor import Mentor
import logging
from cou_course.models.coursecategory import CourseCategory
from cou_course.models.coursesubcategory import CourseSubcategory
from cou_course.models.coursetype import CourseType

class CourseRepository:
    @staticmethod
    def create_course(session: Session, course: Course) -> Course:
        session.add(course)
        session.commit()
        session.refresh(course)
        return course

    @staticmethod
    def get_course_by_id(session: Session, course_id: int) -> Optional[Course]:
        statement = (
            select(Course)
            .join(Mentor, Course.mentor_id == Mentor.user_id)
            .where(Course.id == course_id)
        )
        return session.exec(statement).first()

    @staticmethod
    def get_all_courses(session: Session , skip: int , limit: int) -> List[Course]:
        statement = (
            select(Course)
            .join(Mentor, Course.mentor_id == Mentor.user_id)
            .offset(skip)
            .limit(limit)
        )
        return session.exec(statement).all()

    @staticmethod
    def update_course(session: Session, course_id: int, updates: dict) -> Optional[Course]:
        course = session.get(Course, course_id)
        if course:
            for key, value in updates.items():
                setattr(course, key, value)
            session.commit()
            session.refresh(course)
        return course

    @staticmethod
    def delete_course(session: Session, course_id: int) -> bool:
        course = session.get(Course, course_id)
        if course:
            session.delete(course)
            session.commit()
            return True
        return False
    
    @staticmethod
    def get_courses_by_mentor(session: Session, mentor_id: int):
        statement = (
            select(Course)
            .join(Mentor, Course.mentor_id == Mentor.user_id)
            .where(Course.mentor_id == mentor_id)
        )
        return session.exec(statement).all()
    
    @staticmethod
    def get_filters(session: Session):
        """
        Get all possible filter options for courses including:
        - IT/Non-IT categories
        - Coding/Non-Coding categories
        - Course categories
        - Course levels
        - Price options
        - Average completion time ranges
        """
        # Get all categories
        categories = session.exec(select(CourseCategory).where(CourseCategory.active == True)).all()
        
        # Get all subcategories
        subcategories = session.exec(select(CourseSubcategory).where(CourseSubcategory.active == True)).all()
        
        # Get all course types
        course_types = session.exec(select(CourseType).where(CourseType.active == True)).all()

        # Predefined filters based on the UI requirements
        it_non_it = ["IT", "Non IT"]
        coding_non_coding = ["Coding", "Non-Coding"]
        
        # Price options
        price_options = [
            {"id": "free", "label": "Free", "value": 0},
            {"id": "paid", "label": "Paid", "value": None}
        ]
        
        # Completion time ranges
        completion_time_ranges = [
            {"id": "less_than_5", "label": "Less than 5 hours", "min": 0, "max": 5},
            {"id": "5_10", "label": "5-10 hours", "min": 5, "max": 10},
            {"id": "11_15", "label": "11-15 hours", "min": 11, "max": 15},
            {"id": "16_22", "label": "16-22 hours", "min": 16, "max": 22}
        ]
        
        # Course levels
        levels = [
            {"id": "beginner", "label": "Beginner"},
            {"id": "intermediate", "label": "Intermediate"},
            {"id": "advanced", "label": "Advanced"}
        ]
        
        return {
            "it_non_it": [{"id": x.lower().replace(" ", "_"), "label": x} for x in it_non_it],
            "coding_non_coding": [{"id": x.lower().replace(" ", "_"), "label": x} for x in coding_non_coding],
            "criteria": {
                "categories": [{"id": cat.id, "label": cat.name} for cat in categories],
                "levels": levels
            },
            "preferences": {
                "price": price_options,
                "completion_time": completion_time_ranges
            }
        }
    
    @staticmethod
    def filter_courses(
        session: Session,
        category_id: Optional[int] = None,
        subcategory_id: Optional[int] = None,
        course_type_id: Optional[int] = None,
        sells_type_id: Optional[int] = None,
        language_id: Optional[int] = None,
        mentor_id: Optional[int] = None,
        is_flagship: Optional[bool] = None,
        active: Optional[bool] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_ratings: Optional[float] = None,
        max_ratings: Optional[float] = None,
        it_non_it: Optional[bool] = None,
        coding_non_coding: Optional[bool] = None,
        level: Optional[str] = None,
        price_type: Optional[str] = None,
        completion_time: Optional[str] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Course]:
        """
        Enhanced filter courses based on all available filter options.
        """
        query = select(Course)

        # Basic filters
        if category_id is not None:
            query = query.where(Course.category_id == category_id)
        if subcategory_id is not None:
            query = query.where(Course.subcategory_id == subcategory_id)
        if course_type_id is not None:
            query = query.where(Course.course_type_id == course_type_id)
        if sells_type_id is not None:
            query = query.where(Course.sells_type_id == sells_type_id)
        if language_id is not None:
            query = query.where(Course.language_id == language_id)
        if mentor_id is not None:
            query = query.where(Course.mentor_id == mentor_id)
        if is_flagship is not None:
            query = query.where(Course.is_flagship == is_flagship)
        if active is not None:
            query = query.where(Course.active == active)

        # IT/Non-IT filter - now using the IT boolean field directly
        if it_non_it:
            query = query.where(Course.IT == it_non_it)

        # Coding/Non-Coding filter - now using the Coding_Required boolean field directly
        if coding_non_coding:
            query = query.where(Course.Coding_Required == coding_non_coding)

        # Level filter - now using the Course_level field directly
        if level:
            print(level)
            query = query.where(Course.Course_level == level.lower())

        # Price type filter
        if price_type == "free":
            query = query.where(Course.price == 0)
        elif price_type == "paid":
            query = query.where(Course.price > 0)

        # Price range filter
        if min_price is not None:
            query = query.where(Course.price >= min_price)
        if max_price is not None:
            query = query.where(Course.price <= max_price)

        # Completion time filter - now using Avg_Completion_Time field directly
        if completion_time:
            time_ranges = {
                "less_than_5": (0, 5),
                "5_10": (5, 10),
                "11_15": (11, 15),
                "16_22": (16, 22)
            }
            if completion_time in time_ranges:
                min_time, max_time = time_ranges[completion_time]
                query = query.where(Course.Avg_Completion_Time >= min_time)
                query = query.where(Course.Avg_Completion_Time <= max_time)

        # Rating filters
        if min_ratings is not None:
            query = query.where(Course.ratings >= min_ratings)
        if max_ratings is not None:
            query = query.where(Course.ratings <= max_ratings)

        results = session.exec(query.offset(skip).limit(limit))
        return results.all()