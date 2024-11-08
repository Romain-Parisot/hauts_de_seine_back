from sqlmodel import SQLModel, Field
from typing import Optional
from models.role import Role

class UserBase(SQLModel):
    nom: str
    prenom: str
    email: str = Field(index=True, unique=True)
    telephone: str
    role: Role
    
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: str

class UserCreate(UserBase):
    password: str

class UserId():
    id: int
    
class UserPrivate(UserBase):
    id: int
    