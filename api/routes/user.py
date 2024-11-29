# api/routes/user.py

import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import UserPrivate, UserCreate, UserUpdate
from api.auth import CurrentUser
from core.security import create_access_token, verify_password , decode_refresh_token, create_refresh_token
from crud.crud_user import get_user_by_email, create_user, get_user_by_id
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from models.models import User

router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Durée d'expiration du token en minutes
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Durée d'expiration du refresh token en jours

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
    refresh_token = create_refresh_token(subject=user.id, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    
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
    refresh_token = create_refresh_token(subject=user.id, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/token/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Rafraîchit un access token en utilisant un refresh token valide.
    """
    try:
        # Décoder et valider le refresh token
        payload = decode_refresh_token(refresh_token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Token invalide")
        
        # Vérifier si l'utilisateur existe
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Générer un nouvel access token
        access_token = create_access_token(subject=user.id, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Refresh token invalide ou expiré")


@router.get("/me", response_model=UserPrivate)
def read_current_user(current_user: CurrentUser):
    """Retourne les informations de l'utilisateur connecté"""
    return current_user


@router.put("/me")
def update_user(current_user: CurrentUser, user_update: UserUpdate, db: Session = Depends(get_db)):
    """
    Met à jour les informations de l'utilisateur connecté.
    Les champs non fournis dans la requête ne seront pas modifiés.
    """
    user = get_user_by_id(db, current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    
    user.updated_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "Utilisateur mis à jour", "user": user}

@router.delete("/me")
def delete_user(current_user: CurrentUser, db: Session = Depends(get_db)):
    """
    Supprime l'utilisateur connecté.
    """
    user = get_user_by_id(db, current_user.id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    user.deleted_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "Utilisateur supprimé avec succès."}