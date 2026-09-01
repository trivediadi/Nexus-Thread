from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import String,INTEGER,DateTime,ForeignKey,func,Text
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import UserModel
    from app.models.comment import CommentModel

class PostModel(Base):
    __tablename__="posts"

    id:Mapped[int]=mapped_column(INTEGER,primary_key=True)
    title:Mapped[str]=mapped_column(String(255),nullable=False)
    content:Mapped[str]=mapped_column(Text,nullable=False)

    score:Mapped[int]=mapped_column(INTEGER,default=0,nullable=False)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now(),nullable=False)
    author:Mapped["UserModel"]=relationship("UserModel",back_populates="posts")
    comments:Mapped[list["CommentModel"]]=relationship("CommentModel",back_populates="post",cascade="all, delete-orphan")

