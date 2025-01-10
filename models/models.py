import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from pydantic import EmailStr
from models.role import Role
from models.status import Status

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

    products: List["Product"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "Product.user_id"}
    )
    mairie_products: List["Product"] = Relationship(
        back_populates="mairie_user",
        sa_relationship_kwargs={"foreign_keys": "Product.mairie_user_id"}
    )
    association_products: List["Product"] = Relationship(
        back_populates="association_user",
        sa_relationship_kwargs={"foreign_keys": "Product.association_user_id"}
    )


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=255)


class UserUpdate(SQLModel):
    nom: Optional[str] = Field(None, max_length=255)
    prenom: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = Field(None, unique=True, index=True, max_length=255)
    telephone: Optional[str] = Field(None, max_length=20)
    role: Optional[Role] = None
    password: Optional[str] = Field(None, min_length=8, max_length=40)
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


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
    reference: str = Field(max_length=255)
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
    user: "User" = Relationship(
        back_populates="products",
        sa_relationship_kwargs={"foreign_keys": "Product.user_id"}
    )
    mairie_user: "User" = Relationship(
        back_populates="mairie_products",
        sa_relationship_kwargs={"foreign_keys": "Product.mairie_user_id"}
    )
    association_user: Optional["User"] = Relationship(
        back_populates="association_products",
        sa_relationship_kwargs={"foreign_keys": "Product.association_user_id"}
    )
    photos: List["Photo"] = Relationship(back_populates="product")


class ProductCreate(SQLModel):
    title: str = Field(max_length=255)
    description: str = Field(max_length=255)
    productIssue: str = Field(max_length=255)
    marque: str = Field(max_length=255)
    status: Status
    user_id: uuid.UUID
    mairie_user_id: uuid.UUID

class ProductUpdate(SQLModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None, max_length=255)
    productIssue: Optional[str] = Field(None, max_length=255)
    reference: Optional[str] = Field(None, max_length=255)
    marque: Optional[str] = Field(None, max_length=255)
    user_id: Optional[uuid.UUID] = None
    mairie_user_id: Optional[uuid.UUID] = None
    association_user_id: Optional[uuid.UUID] = None
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProductUpdateStatus(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    status: Status
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProductUpdatesAssociation(SQLModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    association_user_id: uuid.UUID
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProductId(SQLModel):
    id: uuid.UUID
    
class PhotoBase(SQLModel):
    url: str = Field(max_length=255)

class Photo(PhotoBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    product_id: uuid.UUID = Field(foreign_key="product.id")
    product: "Product" = Relationship(back_populates="photos")

class PhotoCreate(PhotoBase):
    product_id: uuid.UUID

class PhotoUpdate(SQLModel):
    url: Optional[str] = Field(None, max_length=255)
    product_id: Optional[uuid.UUID] = None

class PhotoId(SQLModel):
    id: uuid.UUID

class ProductResponse(SQLModel):
    id: uuid.UUID
    title: str
    description: str
    reference: str
    images: Optional[List[Photo]] = []
