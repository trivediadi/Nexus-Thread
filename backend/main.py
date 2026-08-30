from fastapi import FastAPI
from app.core.database import Base,engine

Base.metadata.create_all(engine)


app=FastAPI(title="Nexus Thread")