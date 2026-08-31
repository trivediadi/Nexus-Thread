from fastapi import HTTPException,status,Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from app.models.user import UserModel
from app.core.database import get_db
from app.core.security import decode_access_token

oauth2_schema=OAuth2PasswordBearer(tokenUrl="/login")

async def is_authenticate(token:str=Depends(oauth2_schema),db:AsyncSession=Depends(get_db))->UserModel:
   credential_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credendials",headers={"WWW-Authenticate":"Bearer"})
   data=decode_access_token(token)
   if not data:
      raise credential_exception
   user_id=data.get("sub") or data.get("_id")
   if not user_id:
      raise credential_exception
   result=await db.execute(select(UserModel).where(UserModel.id==int(user_id)))
   user=result.scalar_one_or_none()
   if not user:
      raise credential_exception
   if not user.is_active:
      raise HTTPException(
         status_code=status.HTTP_400_BAD_REQUEST,detail="Inactive User"
      )
   return user
