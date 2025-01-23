from sqlmodel import create_engine, Session, SQLModel
from common.config import settings
from cou_admin.models.currency import Currency
from cou_admin.models.country import Country
from cou_user.models.user import User
from cou_user.models.role import Role
from cou_user.models.login_type import LoginType

engine = create_engine(settings.DATABASE_URL, pool_size=20, max_overflow=15)

SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

