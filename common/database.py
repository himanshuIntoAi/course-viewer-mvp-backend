from sqlmodel import create_engine, Session, SQLModel
from common.config import settings
from cou_admin.models.currency import Currency
from cou_admin.models.country import Country
from cou_user.models.user import User
from cou_user.models.role import Role
from cou_user.models.logintype import LoginType

# Create engine with explicit schema creation
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=15,
    pool_pre_ping=True,   # validate connections before use
    pool_recycle=1800,    # recycle after 30 minutes to avoid stale connections
    pool_timeout=30,      # wait up to 30s for a pooled connection
    connect_args={        # enable TCP keepalives at driver level (psycopg2)
        "keepalives": 1,
        "keepalives_idle": 30,      # seconds of inactivity before keepalive probes
        "keepalives_interval": 10,  # seconds between keepalive probes
        "keepalives_count": 3       # number of failed probes before dropping
    }
)

# Create all tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
