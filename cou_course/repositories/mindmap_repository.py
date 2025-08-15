from sqlmodel import Session, select
from cou_course.models.mindmap import Mindmap
from cou_course.schemas.mindmap_schema import MindmapCreate, MindmapUpdate
from typing import List, Optional

class MindmapRepository:
    @staticmethod
    def create_mindmap(session: Session, mindmap: MindmapCreate) -> Mindmap:
        db_mindmap = Mindmap(**mindmap.dict())
        session.add(db_mindmap)
        session.commit()
        session.refresh(db_mindmap)
        return db_mindmap

    @staticmethod
    def get_mindmap_by_id(session: Session, mindmap_id: int) -> Optional[Mindmap]:
        return session.get(Mindmap, mindmap_id)

    @staticmethod
    def get_mindmaps_by_course(session: Session, course_id: int) -> List[Mindmap]:
        statement = select(Mindmap).where(Mindmap.course_id == course_id, Mindmap.active == True)
        return list(session.exec(statement))

    @staticmethod
    def update_mindmap(session: Session, mindmap_id: int, mindmap_update: MindmapUpdate) -> Optional[Mindmap]:
        db_mindmap = session.get(Mindmap, mindmap_id)
        if not db_mindmap:
            return None
        
        update_data = mindmap_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_mindmap, field, value)
        
        session.add(db_mindmap)
        session.commit()
        session.refresh(db_mindmap)
        return db_mindmap

    @staticmethod
    def delete_mindmap(session: Session, mindmap_id: int) -> bool:
        db_mindmap = session.get(Mindmap, mindmap_id)
        if not db_mindmap:
            return False
        
        db_mindmap.active = False
        session.add(db_mindmap)
        session.commit()
        return True 