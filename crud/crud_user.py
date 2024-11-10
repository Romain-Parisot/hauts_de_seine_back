# crud/crud_user.py

from sqlalchemy.orm import Session
from models.models import User, UserCreate
from core.security import get_password_hash
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

def get_user_by_email(db: Session, email: str) -> User:
    """
    Recherche un utilisateur par son adresse email (en ignorant la casse et les espaces).
    """
    normalized_email = email.strip().lower()  # Normalise l'email (supprime les espaces et met en minuscule)
    return db.exec(select(User).where(User.email == normalized_email)).first()


def create_user(db: Session, user_create: UserCreate) -> User:
    """
    Crée un nouvel utilisateur dans la base de données.
    """
    hashed_password = get_password_hash(user_create.password)# Hachage du mot de passe
    user_create.password = hashed_password
    user = User(**user_create.dict())# Crée un nouvel utilisateur
    print(f"User: {user}")
    
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as e:
        db.rollback()
        raise ValueError(f"L'utilisateur avec cet email existe déjà: {e}")
    
    return user
