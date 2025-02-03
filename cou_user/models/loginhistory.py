from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from .role import Role
from .logintype import LoginType

if TYPE_CHECKING:
    from .user import User

class LoginHistory(SQLModel, table=True):
    __tablename__ = "login_history"
    __table_args__ = {"schema": "cou_user"}

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="cou_user.user.id")
    login_type_id: int = Field(foreign_key="cou_user.login_type.id")
    role_id: Optional[int] = Field(default=None, foreign_key="cou_user.role.id")
    login_at: datetime = Field(default_factory=lambda: datetime.now())
    logout_at: Optional[datetime] = Field(default=None)
    login_success: bool = Field(default=True)
    ip: Optional[str] = Field(default=None, max_length=45)
    location: Optional[str] = Field(default=None, max_length=255)
    device_type: Optional[str] = Field(default=None, max_length=50)
    device_name: Optional[str] = Field(default=None, max_length=500)
    is_proxy: bool = Field(default=False)
    is_duplicate_login: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    created_by: int = Field(...)
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_by: int = Field(...)
    is_mobile: bool = Field(default=False)

    # Relationships with proper back_populates
    user: Optional["User"] = Relationship(
        back_populates="login_history",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    role: Optional["Role"] = Relationship(
        back_populates="login_history",
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    login_type: Optional["LoginType"] = Relationship(
        back_populates="login_history",
        sa_relationship_kwargs={"lazy": "selectin"}
    )