from fastapi import APIRouter,Depends,status,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,or_
from sqlalchemy.orm import selectinload
from typing import Literal

from app.api import deps
from app.models.user import UserModel
from app.models.post import PostModel
from app.schemas.post import PostCreateSchema,PostResponseSchema
from app.models.vote import PostVoteModel
from app.schemas.vote import VoteCreateSchema
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
async def get_all_posts(db:AsyncSession=Depends(get_db),skip:int=0,limit:int=20,sort_by:Literal["new","top","hot"]="new",search:str|None= None,user_id:int|None=None):
    query=(
        select(PostModel).options(selectinload(PostModel.author))
    )
    if user_id is not None:
        query=query.where(PostModel.user_id==user_id)
    if search:
        query=query.where(or_(PostModel.title.ilike(f"{search}%"),PostModel.content.ilike(f"{search}%")))
    if sort_by == "top":
        # Highest score of all time
        query = query.order_by(PostModel.score.desc())    
    elif sort_by == "hot":
        # Basic Hot algorithm: High score, but newer posts break ties
        query = query.order_by(PostModel.score.desc(), PostModel.created_at.desc())
    else:
        query = query.order_by(PostModel.created_at.desc())
    query=query.offset(skip).limit(limit)
    result= await db.execute(query)
    return result.scalars().all()

@post_routes.patch("/{post_id}",response_model=PostResponseSchema,status_code=status.HTTP_200_OK)
async def update_post(post_id:int,body:PostCreateSchema,db:AsyncSession=Depends(get_db),user:UserModel=Depends(deps.is_authenticate)):
    query=select(PostModel).options(selectinload(PostModel.author)).where(PostModel.id==post_id)
    result=await db.execute(query)
    post=result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not Found")
    if post.user_id!=user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to edit this post")
    post.title=body.title
    post.content=body.content
    await db.commit()
    await db.refresh(post)
    return post

@post_routes.delete("/{post_id}",status_code=status.HTTP_200_OK)
async def delete_post(post_id:int,db:AsyncSession=Depends(get_db),user:UserModel=Depends(deps.is_authenticate)):
    query=select(PostModel).where(PostModel.id==post_id)
    result=await db.execute(query)
    post=result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")
    if post.user_id!=user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to delete")
    await db.delete(post)
    await db.commit()
    return None


@post_routes.post("/{post_id}/vote",status_code=status.HTTP_200_OK)
async def vote_post(post_id:int,body:VoteCreateSchema,db:AsyncSession=Depends(get_db),user:UserModel=Depends(deps.is_authenticate)):
    post_query=select(PostModel).where(PostModel.id==post_id)
    post=(await db.execute(post_query)).scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found")
    vote_query=select(PostVoteModel).where(
        PostVoteModel.post_id==post_id,
        PostVoteModel.user_id==user.id
    )
    found_vote=(await db.execute(vote_query)).scalar_one_or_none()
    if body.dir==1 or body.dir==-1:
        if not found_vote:
            new_vote=PostVoteModel(user_id=user.id,post_id=post_id,dir=body.dir)
            db.add(new_vote)
            post.score+=body.dir
            message="Vote added"
        else:
            if found_vote.dir==body.dir:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="You have already voted in this direction")
            post.score+=(body.dir-found_vote.dir)
            found_vote.dir=body.dir
            message="Vote updated"
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Vote does not exist")
        post.score-= found_vote.dir
        await db.delete(found_vote)
        message="Vote removed"
    await db.commit()
    return{
        "message":message,"new_score":post.score
    }

