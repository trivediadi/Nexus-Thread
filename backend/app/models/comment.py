from sqlalchemy.orm import Mapped,mapped_column,relationship
from sqlalchemy import INTEGER,DateTime,ForeignKey,func,Text
from datetime import datetime
from typing import TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import UserModel
    from app.models.post import PostModel

class CommentModel(Base):
    __tablename__ ="comments"

    id:Mapped[int]=mapped_column(INTEGER,primary_key=True)
    content:Mapped[str]=mapped_column(Text,nullable=False)
    score:Mapped[int]=mapped_column(INTEGER,default=0,nullable=False)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True)
    post_id:Mapped[int]=mapped_column(ForeignKey("posts.id",ondelete="CASCADE"),nullable=False,index=True)
    parent_id:Mapped[int|None]=mapped_column(ForeignKey("comments.id",ondelete="CASCADE"),index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),onupdate=func.now(),server_default=func.now(),nullable=False)
    author:Mapped["UserModel"]=relationship("UserModel",back_populates="comments")
    post:Mapped["PostModel"]=relationship("PostModel",back_populates="comments")
    parent:Mapped["CommentModel|None"]=relationship("CommentModel",back_populates="replies",remote_side="CommentModel.id")
    replies:Mapped[list["CommentModel"]]=relationship("CommentModel",back_populates="parent",cascade="all, delete-orphan")