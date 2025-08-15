from sqlmodel import Session, select
from cou_course.models.topic import Topic
from cou_course.schemas.topic_schema import TopicCreate, TopicUpdate
from typing import List, Optional

class TopicRepository:
    @staticmethod
    def create_topic(session: Session, topic: TopicCreate) -> Topic:
        db_topic = Topic(**topic.dict())
        session.add(db_topic)
        session.commit()
        session.refresh(db_topic)
        return db_topic

    @staticmethod
    def get_topic_by_id(session: Session, topic_id: int) -> Optional[Topic]:
        return session.get(Topic, topic_id)

    @staticmethod
    def get_topics_by_course(session: Session, course_id: int) -> List[Topic]:
        statement = select(Topic).where(Topic.course_id == course_id, Topic.active == True)
        return list(session.exec(statement))

    @staticmethod
    def update_topic(session: Session, topic_id: int, topic_update: TopicUpdate) -> Optional[Topic]:
        db_topic = session.get(Topic, topic_id)
        if not db_topic:
            return None
        
        update_data = topic_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_topic, field, value)
        
        session.add(db_topic)
        session.commit()
        session.refresh(db_topic)
        return db_topic

    @staticmethod
    def delete_topic(session: Session, topic_id: int) -> bool:
        db_topic = session.get(Topic, topic_id)
        if not db_topic:
            return False
        
        db_topic.active = False
        session.add(db_topic)
        session.commit()
        return True 