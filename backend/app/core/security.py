import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from typing import Any
from datetime import timedelta,datetime,timezone
from app.core.config import settings

password_hash = PasswordHash.recommended()

def verify_password(plain_password, hashed_password)->bool:
    return password_hash.verify(plain_password, hashed_password)

def get_password_hash(password)->str:
    return password_hash.hash(password)

def create_access_token(data:dict[str,Any],expire_delta:timedelta|None=None)->str:
    to_encode=data.copy()
    if expire_delta:
        expire=datetime.now(timezone.utc)+expire_delta
    else:
        expire=datetime.now(timezone.utc)+ timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
def decode_access_token(token:str)->dict[str,Any]|None:
    try:
        return jwt.decode(token,settings.SECRET_KEY,algorithms=settings.ALGORITHM)
    except InvalidTokenError:
        return None
    