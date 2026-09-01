from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String,Boolean,DateTime,func,INTEGER
from datetime import datetime
from typing import List,TYPE_CHECKING


from app.core.database import Base

if TYPE_CHECKING:
    from app.models.post import PostModel

class UserModel(Base):
    __tablename__="users"

    id:Mapped[int]=mapped_column(INTEGER,primary_key=True,index=True)
    name:Mapped[str|None]=mapped_column(String(100),nullable=True)
    username:Mapped[str]=mapped_column(String(50),unique=True,index=True,nullable=False)
    email:Mapped[str]=mapped_column(String(255),unique=True,nullable=False)
    hash_password:Mapped[str]=mapped_column(String(255),nullable=False)

    is_active:Mapped[bool]=mapped_column(Boolean,default=True,nullable=False)
    is_superuser:Mapped[bool]=mapped_column(Boolean,default=False,nullable=False)

    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)
    posts:Mapped[list["PostModel"]]=relationship("PostModel",back_populates="author",cascade="all, delete-orphan")
