from fastapi import FastAPI
from app.database import Base, engine
from app.routers import users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI CRUD with SQLite & Redis",
    version="1.0.0"
)

app.include_router(users.router)
