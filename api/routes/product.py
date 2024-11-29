import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import Product, ProductCreate, ProductUpdate, Photo, PhotoCreate, ProductUpdateStatus
from crud.crud_user import get_user_by_id
from crud.crud_product import get_product_by_id
from models.status import Status

router = APIRouter()

@router.post("/")
async def create_new_product_with_images(product: ProductCreate, db: Session = Depends(get_db), files: list[UploadFile] = File(...)):
    """Crée un nouveau produit avec des images associées."""
    
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    random_part = str(uuid.uuid4()).split("-")[0]
    reference = f"PRD-{current_date}-{random_part}"
    
    user = get_user_by_id(db, product.user_id)
    mairie_user = get_user_by_id(db, product.mairie_user_id)
    if user is None or mairie_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    product_db = Product(**product.dict(), reference=reference, user_id=user.id, mairie_user_id=mairie_user.id)
    
    photos = []
    for file in files:
        file_url = f"/images/{file.filename}"
        
        photo = PhotoCreate(url=file_url, product_id=product_db.id)
        photos.append(Photo(**photo.dict()))
    
    db.add(product_db)
    db.commit()
    db.refresh(product_db)
    
    db.add_all(photos)
    db.commit()
    
    for photo in photos:
        db.refresh(photo)
    
    return {"product": product_db, "images": photos}

@router.get("/")
def get_all_products(db: Session = Depends(get_db)):
    """Retourne tous les produits avec leurs images associées."""
    
    products = db.query(Product).all()
    
    for product in products:
        product.images = db.query(Photo).filter(Photo.product_id == product.id).all()
    
    return products
  
@router.get("/{product_id}")
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retourne un produit avec ses images associées."""
    
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    product.images = db.query(Photo).filter(Photo.product_id == product.id).all()
    
    return product
  
@router.get("/user/{user_id}")
def get_product_by_user_id(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retourne les produits du user avec leurs images associées."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    products = db.query(Product).filter(Product.user_id == user.id).all()
    
    for product in products:
        product.images = db.query(Photo).filter(Photo.product_id == product.id).all()
    
    return products

@router.put("/{product_id}")
async def update_product_with_images(product_id: uuid.UUID, product: ProductUpdate, db: Session = Depends(get_db), files: list[UploadFile] = File(...)):
    """Met à jour un produit avec de nouvelles images."""
    
    product_db = get_product_by_id(db, product_id)
    if product_db is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    for key, value in product.dict(exclude_unset=True).items():
        setattr(product_db, key, value)
        
    if product_db.status != product.status:
      raise HTTPException(status_code=401, detail="Vous ne pouvez pas modifier le status du produit.")
    
    product_db.updated_at = datetime.datetime.now(datetime.timezone.utc)
    current_images = db.query(Photo).filter(Photo.product_id == product_id).all()
    current_image_urls = {photo.url for photo in current_images}    
    new_image_urls = {f"/images/{file.filename}" for file in files}    
    images_to_delete = current_image_urls - new_image_urls
    if images_to_delete:
        db.query(Photo).filter(Photo.product_id == product_id, Photo.url.in_(images_to_delete)).delete(synchronize_session=False)
    
    images_to_add = new_image_urls - current_image_urls
    photos = []
    for file in files:
        file_url = f"/images/{file.filename}"
        if file_url in images_to_add:
            photo = PhotoCreate(url=file_url, product_id=product_id)
            photos.append(Photo(**photo.dict()))
    
    db.add_all(photos)
    db.commit()
    
    db.refresh(product_db)
    for photo in photos:
        db.refresh(photo)
    
    updated_images = db.query(Photo).filter(Photo.product_id == product_id).all()
    
    return {"product": product_db, "images": updated_images}

@router.put("/{product_id}/status")
async def update_product_status(product: ProductUpdateStatus, db: Session = Depends(get_db)):
    """Met à jour uniquement le status d'un produit."""
    
    product_db = get_product_by_id(db, product.id)
    if product_db is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    product_db.status = product.status
    product_db.updated_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.commit()
    db.refresh(product_db)
    
    return {"product": product_db}
