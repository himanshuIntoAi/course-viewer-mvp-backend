from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from .loginhistory import LoginHistory

class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = {"schema": "cou_user"}

    id: Optional[int] = Field(default=None, primary_key=True)
    display_name: str = Field(max_length=100)
    image: Optional[bytes] = None
    first_name: Optional[str] = Field(default=None, max_length=500)
    last_name: Optional[str] = Field(default=None, max_length=500)
    role_id: Optional[int] = Field(default=None, foreign_key="cou_user.role.id")
    work_email: Optional[str] = Field(default=None, max_length=500)
    personal_email: Optional[str] = Field(default=None, max_length=500)
    login_type_id: Optional[int] = Field(default=None, foreign_key="cou_user.login_type.id")
    mobile: Optional[str] = Field(default=None)
    affiliate_id: Optional[int] = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: int
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_by: int
    active: bool = Field(default=True)
    premium: Optional[bool] = Field(default=False)
    facebook: Optional[str] = Field(default=None, max_length=500)
    instagram: Optional[str] = Field(default=None, max_length=500)
    linkedin: Optional[str] = Field(default=None, max_length=500)
    twitter: Optional[str] = Field(default=None, max_length=500)
    youtube: Optional[str] = Field(default=None, max_length=500)
    monitor: Optional[bool] = Field(default=False)
    remarks: Optional[str] = None
    currency_id: Optional[int] = Field(default=None, foreign_key="cou_admin.currency.id")
    country_id: Optional[int] = Field(default=None, foreign_key="cou_admin.country.id")

    is_student: Optional[bool] = Field(default=False)
    is_instructor: Optional[bool] = Field(default=False)
    key: Optional[str] = Field(default=None)  # For storing password hash

    # Add relationships
    login_history: List["LoginHistory"] = Relationship(back_populates="user", sa_relationship_kwargs={"lazy": "selectin"})




