from sqlalchemy import Integer,ForeignKey
from sqlalchemy.orm import Mapped,mapped_column

from app.core.database import Base

class PostVoteModel(Base):
    __tablename__="post_votes"

    user_id:Mapped[id]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),primary_key=True)
    post_id:Mapped[int]=mapped_column(ForeignKey("posts.id",ondelete="CASCADE"),primary_key=True)

    dir:Mapped[int]=mapped_column(Integer,nullable=False)

class CommentVoteModel(Base):
    __tablename__="comment_votes"
    user_id:Mapped[id]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),primary_key=True)
    comment_id:Mapped[int]=mapped_column(ForeignKey("comments.id",ondelete="CASCADE"),primary_key=True)

    dir:Mapped[int]=mapped_column(Integer,nullable=False)