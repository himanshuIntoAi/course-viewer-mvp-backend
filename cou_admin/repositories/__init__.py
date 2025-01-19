from sqlmodel import Session, select

def __init__(self, session: Session):
        self.session = session