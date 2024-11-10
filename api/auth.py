from datetime import timedelta
from typing import Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import User
from core.config import settings
import jwt
from fastapi.security import OAuth2PasswordBearer
from core.security import decode_access_token


# Schéma OAuth2 pour gérer le token d'authentification
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/token")


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    """
    Récupère l'utilisateur actuel à partir du token JWT.
    
    Cette fonction décode le JWT, extrait l'ID utilisateur et vérifie si l'utilisateur existe et est actif.
    Si le token est invalide ou expiré, elle lève une exception HTTP 403.
    """
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token invalide",
            )
        # Recherche l'utilisateur dans la base de données avec l'ID extrait du token
        user = db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        return user
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token invalide ou expiré",
        )


# Alias pour l'utilisateur courant afin de l'utiliser facilement dans les dépendances FastAPI
CurrentUser = Annotated[User, Depends(get_current_user)]
