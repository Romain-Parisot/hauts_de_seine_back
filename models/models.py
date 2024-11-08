import uuid
from sqlmodel import SQLModel, Field
from typing import Optional
from models.role import Role
from pydantic import EmailStr

class UserBase(SQLModel):
    nom: str = Field(max_length=255)
    prenom: str = Field(max_length=255)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    telephone: str = Field(max_length=20)
    role: Role

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password: str = Field(min_length=8, max_length=255)

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)
    
class UserUpdate(SQLModel):
    nom: Optional[str] = Field(None, max_length=255)
    prenom: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None, unique=True, index=True, max_length=255)
    telephone: Optional[str] = Field(None, max_length=20)
    role: Optional[Role] = None
    password: Optional[str] = Field(None, min_length=8, max_length=40)

class UserId(SQLModel):
    id: uuid.UUID
    
class UserPrivate(UserBase):
    id: uuid.UUID
