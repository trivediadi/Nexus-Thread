from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import Base,engine
from app.api.v1.auth import user_routes
from app.api.v1.posts import post_routes
from app.api.v1.comments import comment_routes
@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    await engine.dispose()
app=FastAPI(title="Nexus Thread",lifespan=lifespan)

app.include_router(user_routes)
app.include_router(post_routes)
app.include_router(comment_routes)