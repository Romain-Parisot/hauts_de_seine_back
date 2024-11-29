import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from typing import Optional
from models.role import Role
from models.status import Status
from pydantic import EmailStr
from typing import List
from sqlmodel import Relationship

class UserBase(SQLModel):
    nom: str = Field(max_length=255)
    prenom: str = Field(max_length=255)
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    telephone: str = Field(max_length=20)
    role: Role
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deleted_at: Optional[datetime] = None

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    password: str = Field(min_length=8, max_length=255)
    products: List["Product"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)
    
class UserUpdate(SQLModel):
    nom: Optional[str] = Field(None, max_length=255)
    prenom: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None, unique=True, index=True, max_length=255)
    telephone: Optional[str] = Field(None, max_length=20)
    role: Optional[Role] = None
    password: Optional[str] = Field(None, min_length=8, max_length=40)
    update_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserDelete(SQLModel):
    id: uuid.UUID
    deleted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserId(SQLModel):
    id: uuid.UUID
    
class UserPrivate(UserBase):
    id: uuid.UUID

class ProductBase(SQLModel):
    title: str = Field(max_length=255)
    description: str = Field(max_length=255)
    productIssue: str = Field(max_length=255)
    reference : str = Field(max_length=255)
    marque: str = Field(max_length=255)
    status: Status 
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    deposed_at: Optional[datetime] = None
    
class Product(ProductBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    mairie_user_id: uuid.UUID = Field(foreign_key="user.id")
    association_user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="user.id") 
    user: "User" = Relationship(back_populates="products", sa_relationship_kwargs={"foreign_keys": "Product.user_id"})
    mairie_user: "User" = Relationship(sa_relationship_kwargs={"foreign_keys": "Product.mairie_user_id"}) 
    association_user: Optional["User"] = Relationship(sa_relationship_kwargs={"foreign_keys": "Product.association_user_id"})
    photos: List["Photo"] = Relationship(back_populates="product")
    
class ProductCreate(ProductBase):
    user_id: uuid.UUID
    mairie_user_id: uuid.UUID

class ProductUpdate(SQLModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    productIssue: Optional[str] = Field(None, max_length=255)
    reference : Optional[str] = Field(None, max_length=255)
    marque: Optional[str] = Field(None, max_length=255)
    user_id: Optional[uuid.UUID] = None
    mairie_user_id: Optional[uuid.UUID] = None
    update_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    
class ProductUpdateStatus(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: Status
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductUpdatesAssociation(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    association_user_id: uuid.UUID
    update_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductId(SQLModel):
    id: uuid.UUID
    
class photoBase(SQLModel):
    url: str = Field(max_length=255)
    
class Photo(photoBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    product_id: uuid.UUID = Field(foreign_key="product.id")
    product: "Product" = Relationship(back_populates="photos")

class PhotoCreate(photoBase):
    product_id: uuid.UUID
    
class PhotoUpdate(SQLModel):
    url: Optional[str] = Field(None, max_length=255)
    productId : Optional[ProductId] = None

class PhotoId(SQLModel):
    id: uuid.UUID
    