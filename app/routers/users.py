from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.deps import get_db
from app.redis import redis_client
import json

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    created_user = crud.create_user(db, user)

    if redis_client:
        redis_client.delete("users")

    return created_user

@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    if redis_client:
        cached = redis_client.get(f"user:{user_id}")
        if cached:
            return json.loads(cached)

    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if redis_client:
        redis_client.set(
            f"user:{user_id}",
            json.dumps(
                schemas.UserResponse.model_validate(user).model_dump()
            )
        )

    return user

@router.get("/", response_model=list[schemas.UserResponse])
def read_users(db: Session = Depends(get_db)):
    if redis_client:
        cached = redis_client.get("users")
        if cached:
            return json.loads(cached)

    users = crud.get_users(db)

    if redis_client:
        redis_client.set(
            "users",
            json.dumps([
                schemas.UserResponse.model_validate(u).model_dump()
                for u in users
            ])
        )

    return users

@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if redis_client:
        redis_client.delete("users")
        redis_client.delete(f"user:{user_id}")

    return {"message": "User deleted successfully"}
