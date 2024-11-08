from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import User, UserPrivate, UserCreate

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
  try:
      db_user = User(**user.dict())
      db.add(db_user)
      db.commit()
      db.refresh(db_user)
      return db_user
  except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))
