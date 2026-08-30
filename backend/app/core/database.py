from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

Base=declarative_base()

engine=create_async_engine(url=settings.DB_CONNECTION,echo=False,future=True)
LocalSession=async_sessionmaker(bind=engine,class_=AsyncSession,expire_on_commit=False,autoflush=False,autocommit=False)

async def get_db():
   async with LocalSession() as session:
        try:
            yield session
        finally:
            await session.close()