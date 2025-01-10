import os
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import Product, ProductCreate, ProductResponse, ProductUpdate, Photo, PhotoCreate, ProductUpdateStatus, ProductUpdatesAssociation
from crud.crud_user import get_user_by_id
from crud.crud_product import get_product_by_id
from models.status import Status
import shutil

router = APIRouter()

@router.post("/")
async def create_new_product_with_images(
    product: ProductCreate = Depends(), 
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db)
):
    """Crée un nouveau produit avec des images associées."""

    current_date = datetime.datetime.now().strftime("%Y%m%d")
    random_part = str(uuid.uuid4()).split("-")[0]
    reference = f"PRD-{current_date}-{random_part}"
    
    user = get_user_by_id(db, product.user_id)
    mairie_user = get_user_by_id(db, product.mairie_user_id)
    if user is None or mairie_user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")

    product_data = product.dict(exclude={'photos', 'user_id', 'mairie_user_id'})
    product_db = Product(**product_data, reference=reference, user_id=user.id, mairie_user_id=mairie_user.id)

    photos = []
    try:
        db.add(product_db)
        upload_dir = "./uploads/images"
        os.makedirs(upload_dir, exist_ok=True)

        for file in files:
            if not file.content_type.startswith("image/"):
                raise HTTPException(status_code=400, detail=f"Le fichier {file.filename} n'est pas une image valide.")
            
            file_path = f"./uploads/images/{file.filename}"
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            photo = PhotoCreate(url=f"/uploads/images/{file.filename}", product_id=product_db.id)
            photos.append(Photo(**photo.dict()))

        if photos:
            db.add_all(photos)
            db.commit()
        db.commit()
        db.refresh(product_db)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création du produit : {str(e)}")

    return {"product": product_db, "images": photos}

@router.get("/")
def get_all_products(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    """Retourne tous les produits avec leurs images associées."""
    
    products = db.query(Product).offset(skip).limit(limit).all()
    
    product_responses = []
    for product in products:
        photos = db.query(Photo).filter(Photo.product_id == product.id).all()
        product_response = ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            reference=product.reference,
            images=[Photo(id=photo.id, url=photo.url) for photo in photos]
        )
        product_responses.append(product_response)
    
    return product_responses

@router.get("/{product_id}")
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retourne un produit avec ses images associées."""
    
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    product_response = ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            reference=product.reference,
            images=db.query(Photo).filter(Photo.product_id == product.id).all()
        )
    
    return product_response
  
@router.get("/user/{user_id}")
def get_product_by_user_id(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """Retourne les produits du user avec leurs images associées."""
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    products = db.query(Product).filter(Product.user_id == user.id).all()
    
    product_responses = []
    for product in products:
        photos = db.query(Photo).filter(Photo.product_id == product.id).all()
        product_response = ProductResponse(
            id=product.id,
            title=product.title,
            description=product.description,
            reference=product.reference,
            images=[Photo(id=photo.id, url=photo.url) for photo in photos]
        )
        product_responses.append(product_response)
    
    return product_responses

@router.put("/{product_id}")
async def update_product_with_images(
    product_id: uuid.UUID,
    product: ProductUpdate = Depends(),
    db: Session = Depends(get_db),
    files: list[UploadFile] = File(...)
):
    product_db = get_product_by_id(db, product_id)
    if product_db is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    for file in files:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail=f"Le fichier {file.filename} n'est pas une image valide.")
    
    if "status" in product.dict(exclude_unset=True) and product_db.status != product.status:
        raise HTTPException(status_code=401, detail="Vous ne pouvez pas modifier le status du produit.")
    
    updated_fields = False
    for key, value in product.dict(exclude_unset=True).items():
        if value is not None:
            setattr(product_db, key, value)
            updated_fields = True 

    if updated_fields:
        product_db.updated_at = datetime.datetime.now(datetime.timezone.utc)
    
    try:
        current_images = db.query(Photo).filter(Photo.product_id == product_id).all()
        current_image_urls = {photo.url for photo in current_images}
        new_image_urls = {f"/images/{file.filename}" for file in files}
        
        images_to_delete = current_image_urls - new_image_urls
        if images_to_delete:
            db.query(Photo).filter(Photo.product_id == product_id, Photo.url.in_(images_to_delete)).delete(synchronize_session="fetch")
        
        photos = []
        for file in files:
            file_url = f"/images/{file.filename}"
            if file_url in new_image_urls - current_image_urls:
                file_path = f"uploads/images/{file.filename}"
                
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, "wb") as buffer:
                    buffer.write(await file.read())
                
                photo = PhotoCreate(url=file_url, product_id=product_id)
                photos.append(Photo(**photo.dict()))
        
        db.add_all(photos)

        if updated_fields:
            db.add(product_db)
        
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la mise à jour du produit : {str(e)}"
        )

    db.refresh(product_db)
    for photo in photos:
        db.refresh(photo)
    
    updated_images = db.query(Photo).filter(Photo.product_id == product_id).all()

    return {
        "product": {
            "id": str(product_db.id),
            "title": product_db.title,
            "description": product_db.description,
            "updated_at": product_db.updated_at,
        },
        "images": [{"id": photo.id, "url": photo.url} for photo in updated_images],
    }

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

@router.put("/{product_id}/association")
async def update_product_association(product: ProductUpdatesAssociation, db: Session = Depends(get_db)):
    """Met à jour l'association d'un produit."""
    
    product_db = get_product_by_id(db, product.id)
    if product_db is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")

    asso = get_user_by_id(db, product.association_user_id)
    if asso is None:
      raise HTTPException(status_code=404, detail="Association non trouvée.")
    
    product_db.association_user_id = asso.id
    product_db.updated_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.commit()
    db.refresh(product_db)
    
    return {"product": product_db}
  
@router.delete("/{product_id}")
def delete_product(product_id: uuid.UUID, db: Session = Depends(get_db)):
    """Supprime un produit avec ses images associées."""
    
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    db.query(Photo).filter(Photo.product_id == product_id).delete()
    db.delete(product)
    db.commit()
    
    return {"message": "Produit supprimé avec succès."}
  
@router.put("/{product_id}/deposed")
def update_product_deposed_at(product_id: uuid.UUID, db: Session = Depends(get_db)):
    """Met à jour la date de déposition d'un produit."""
    
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    product.deposed_at = datetime.datetime.now(datetime.timezone.utc)
    product.updated_at = datetime.datetime.now(datetime.timezone.utc)
    
    db.commit()
    db.refresh(product)
    
    return {"product": product}