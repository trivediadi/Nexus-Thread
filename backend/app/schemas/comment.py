from __future__ import annotations
from pydantic import BaseModel,ConfigDict
from datetime import datetime


from app.schemas.user import UserResponseSchema

class CommentCreateSchema(BaseModel):
    content:str
    parent_id:int |None=None

class CommentUpdateSchema(BaseModel):
    content:str

class CommentResponseSchema(BaseModel):
    id:int 
    content:str   
    score:int
    user_id:int
    post_id:int
    parent_id:int | None=None
    author:UserResponseSchema 
    created_at:datetime
    updated_at:datetime
    replies:list[CommentResponseSchema]=[]
    model_config=ConfigDict(from_attributes=True)


