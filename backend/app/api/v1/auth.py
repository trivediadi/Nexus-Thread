#routing and controller
from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime,timezone
from sqlalchemy import select

from app.core.config import settings
from app.schemas.user import UserSchema,LoginSchema,UserResponseSchema,TokenSchema
from app.api import deps
from app.core.database import get_db
from app.models.user import UserModel
from app.core.security import verify_password,get_password_hash,create_access_token
user_routes=APIRouter(prefix="/user")

@user_routes.post("/register",response_model=UserResponseSchema,status_code=status.HTTP_201_CREATED)
async def register(body:UserSchema,db:AsyncSession=Depends(get_db)):
    is_user=await db.execute(select(UserModel).where(UserModel.username==body.username))
    if is_user.scalar_one_or_none():
        raise HTTPException(status_code=400,detail="User already exist...")
    is_email=await db.execute(select(UserModel).where(UserModel.email==body.email))
    if is_email.scalar_one_or_none():
        raise HTTPException(status_code=400,detail="Mail already exist...")
    hash_pwd=get_password_hash(body.password)
    new_user=UserModel(
        name=body.name,
        username=body.username,
        hash_password=hash_pwd,
        email=body.email
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@user_routes.post("/login",response_model=TokenSchema,status_code=status.HTTP_200_OK)
async def login(body:LoginSchema,db:AsyncSession=Depends(get_db)):
    result=await db.execute(select(UserModel).where(UserModel.username==body.username))
    user=result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Username is not correct")
    if not verify_password(body.password,user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Password is not correct")
    token=create_access_token(data={"sub":str(user.id)})
    return {"access_token":token,
            "token_type":"bearer"}



@user_routes.get("/is_auth",response_model=UserResponseSchema,status_code=status.HTTP_200_OK)
async def is_auth(current_user:UserModel=Depends(deps.is_authenticate)):
    return current_user
    


    

