from fastapi import APIRouter,HTTPException,Depends,status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.comment import CommentModel
from app.models.post import PostModel
from app.models.user import UserModel
from app.schemas.comment import CommentUpdateSchema,CommentCreateSchema,CommentResponseSchema
from app.core.database import get_db
from app.api import deps

comment_routes=APIRouter(prefix="/posts/{post_id}/comments",tags=["Comments"])

@comment_routes.post("",response_model=CommentResponseSchema,status_code=status.HTTP_201_CREATED)
async def create(post_id:int,body:CommentCreateSchema,db:AsyncSession=Depends(get_db),user:UserModel=Depends(deps.is_authenticate)):
    result=await db.execute(select(PostModel).where(PostModel.id==post_id))
    post=result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post Not Found")
    
    if body.parent_id:
        parent_res=await db.execute(select(CommentModel).where(CommentModel.id==body.parent_id))
        parent_comment=parent_res.scalar_one_or_none()
        if not parent_comment or parent_comment.post_id!=post_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Parent comment not found on this post")
    new_comment=CommentModel(content=body.content,post_id=post_id,user_id=user.id,parent_id=body.parent_id)
    db.add(new_comment)
    await db.commit()
    query=(select(CommentModel).options(selectinload(CommentModel.author),selectinload(CommentModel.replies)).where(CommentModel.id==new_comment.id))
    fresh_res=await db.execute(query)
    res=fresh_res.scalar_one()
    return new_comment

@comment_routes.get("",response_model=list[CommentResponseSchema],status_code=status.HTTP_200_OK)
async def get_comments(post_id:int,db:AsyncSession=Depends(get_db)):
    post_res=await db.execute(select(PostModel).where(PostModel.id==post_id))
    post=post_res.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post Not found")
    
    query=(select(CommentModel).options(selectinload(CommentModel.author)).where(CommentModel.post_id==post_id).order_by(CommentModel.created_at.asc()))
    result=await db.execute(query)
    all_comments=result.scalars().all()

    comment_schemas = [
        CommentResponseSchema(
            id=c.id,
            content=c.content,
            score=c.score,
            user_id=c.user_id,
            post_id=c.post_id,
            parent_id=c.parent_id,
            author=c.author, 
            created_at=c.created_at,
            updated_at=c.updated_at,
            replies=[] 
        )
        for c in all_comments
    ]

    comment_map={c.id:c for c in comment_schemas}
    root_comments=[]

    for comment in comment_schemas:
        if comment.parent_id is None:
            root_comments.append(comment)
        else:
            parent = comment_map.get(comment.parent_id)
            if parent is not None:
                parent.replies.append(comment)
    return root_comments

@comment_routes.patch("/{comment_id}",response_model=CommentResponseSchema,status_code=status.HTTP_200_OK)
async def update_comment(post_id:int,comment_id:int,body:CommentUpdateSchema,db:AsyncSession=Depends(get_db),user:UserModel=Depends(deps.is_authenticate)):
    query=(select(CommentModel).options(selectinload(CommentModel.author)).where(CommentModel.id==comment_id ,CommentModel.post_id==post_id))
    result=await db.execute(query)
    comment=result.scalar_one_or_none() 
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comment not found on this post")
    if comment.user_id!=user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not authorized")
    comment.content=body.content
   
    await db.commit()
    await db.refresh(comment,attribute_names=["content","updated_at"])
    return CommentResponseSchema(
        id=comment.id,
        content=comment.content,
        score=comment.score,
        user_id=comment.user_id,
        post_id=comment.post_id,
        parent_id=comment.parent_id,
        author=comment.author, 
        created_at=comment.created_at,
        updated_at=comment.updated_at,
        replies=[] 
    )

@comment_routes.delete("/{comment_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(post_id:int,comment_id:int,db:AsyncSession=Depends(get_db),user:UserModel=Depends(deps.is_authenticate)):
    query=(select(CommentModel).where(CommentModel.id==comment_id ,CommentModel.post_id==post_id))
    result=await db.execute(query)
    comment=result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comment not found on this post")
    if comment.user_id!=user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not authorized")
    await db.delete(comment)
    await db.commit()
    return None