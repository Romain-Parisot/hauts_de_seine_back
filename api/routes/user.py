# api/routes/user.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import UserPrivate, UserCreate
from api.auth import CurrentUser
from core.security import create_access_token, verify_password
from crud.crud_user import get_user_by_email, create_user
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Durée d'expiration du token en minutes

@router.post("/")
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """Crée un nouvel utilisateur et retourne un token JWT"""
    # Vérifie si l'utilisateur existe déjà avec le même email
    user_exist = get_user_by_email(db, user.email)
    print(f"il existe : {user_exist}")
    if user_exist is not None:
      raise HTTPException(status_code=400, detail="L'utilisateur avec cet email existe déjà dans le système.")
    # Crée un nouvel utilisateur
    db_user = create_user(db, user)
    
    # Génére un token d'accès pour l'utilisateur nouvellement créé
    access_token = create_access_token(subject=db_user.id)
    
    # Retourne le token et le type (bearer)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Connexion pour obtenir un token JWT en utilisant le nom d'utilisateur et le mot de passe"""
    # Recherche l'utilisateur par email
    user = get_user_by_email(db, form_data.username)
    
    # Vérifie que l'utilisateur existe et que le mot de passe est correct
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nom d'utilisateur ou mot de passe incorrect")
    
    # Crée un token d'accès avec une expiration définie
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(subject=user.id, expires_delta=access_token_expires)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserPrivate)
def read_current_user(current_user: CurrentUser):
    """Retourne les informations de l'utilisateur connecté"""
    return current_user
