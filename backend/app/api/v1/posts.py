from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


from app.api import deps
from app.models.user import UserModel
from app.models.post import PostModel
from app.schemas.post import PostCreateSchema,PostResponseSchema
from app.core.database import get_db

post_routes=APIRouter(prefix="/posts",tags=["Posts"])

@post_routes.post("/create",response_model=PostResponseSchema,status_code=status.HTTP_201_CREATED)
async def create(body:PostCreateSchema,db:AsyncSession=Depends(get_db),user:UserModel=Depends(deps.is_authenticate)):
    new_post=PostModel(title=body.title,content=body.content,user_id=user.id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)

    new_post.author=user
    return new_post

@post_routes.get("/{username}/submitted",response_model=list[PostResponseSchema],status_code=status.HTTP_200_OK)
async def get_user_submitted_posts(username:str,db:AsyncSession=Depends(get_db)):
    user_results=await db.execute(select(UserModel).where(UserModel.username==username))
    target_user=user_results.scalar_one_or_none()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    query=(select(PostModel).options(selectinload(PostModel.author)).where(PostModel.user_id==target_user.id).order_by(PostModel.created_at.desc()))
    result=await db.execute(query)
    posts=result.scalars().all()
    return posts

@post_routes.get("/",response_model=list[PostResponseSchema],status_code=status.HTTP_200_OK)
async def get_all_posts(db:AsyncSession=Depends(get_db),skip:int=0,limit:int=20):
    query=(
        select(PostModel).options(selectinload(PostModel.author)).order_by(PostModel.created_at.desc()).offset(skip).limit(limit)
    )
    result= await db.execute(query)
    return result.scalars().all()
