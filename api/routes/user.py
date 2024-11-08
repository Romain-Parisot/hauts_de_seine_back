from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import User, UserPrivate, UserCreate
from sqlmodel import select
from core.security import get_password_hash

router = APIRouter()

@router.post("/", response_model=UserPrivate)
def create_new_user(user:UserCreate , db: Session = Depends(get_db)):
  """ Crée un nouvel utilisateur

  keyword arguments:
    user: UserCreate -- [description] (default: {Depends(get_db)})
    db: Session -- [description] (default: {Depends(get_db)})

  returns:
    [type] -- [description]s
"""
  user_exist = db.exec(select(User).where(User.email == user.email)).first()
  if user_exist:
    raise HTTPException(
        status_code=400,
        detail="The user with this email already exists in the system.",
    )
  user.password = get_password_hash(user.password)
  try:
      db_user = User(**user.dict())
      db.add(db_user)
      db.commit()
      db.refresh(db_user)
      return db_user
  except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))
