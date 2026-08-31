from pydantic import BaseModel,EmailStr,ConfigDict
from datetime import datetime
class UserSchema(BaseModel):
    name:str | None=None
    username:str
    email:EmailStr
    password:str

class UserResponseSchema(BaseModel):
    id:int
    name:str |None=None
    username:str
    email:EmailStr
    is_active:bool
    is_superuser:bool
    created_at:datetime
    updated_at:datetime

    model_config=ConfigDict(from_attributes=True)

class LoginSchema(BaseModel):
    username:str
    password:str
class TokenSchema(BaseModel):
    access_token:str
    token_type:str="bearer"