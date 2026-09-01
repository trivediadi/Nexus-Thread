from pydantic import BaseModel,ConfigDict
from app.schemas.user import UserResponseSchema
from datetime import datetime

class PostCreateSchema(BaseModel):
    title:str
    content:str


class PostResponseSchema(BaseModel):
    id:int
    title:str
    content:str
    score:int
    user_id:int
    author:UserResponseSchema
    created_at:datetime
    updated_at:datetime
    model_config=ConfigDict(from_attributes=True)