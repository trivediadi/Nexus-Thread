from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import Base,engine

@asynccontextmanager
async def lifespan(app:FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    await engine.dispose()
app=FastAPI(title="Nexus Thread",lifespan=lifespan)


