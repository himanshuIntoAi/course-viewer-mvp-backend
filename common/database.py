from sqlmodel import create_engine, Session
from common.config import settings

engine = create_engine(settings.DATABASE_URL, pool_size=20, max_overflow=15)

def get_session():
    with Session(engine) as session:
        yield session
