import qrcode
from io import BytesIO
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import Product
from crud.crud_product import get_product_by_id
import uuid

router = APIRouter()

@router.get("/{product_id}/generate-qr-code")
async def generate_qr_code(product_id: uuid.UUID, db: Session = Depends(get_db)):
    """Génère un QR code pour un produit."""
    product = get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    product_url = f"http://localhost:8000/products/{product_id}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(product_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return StreamingResponse(buffer, media_type="image/png")
