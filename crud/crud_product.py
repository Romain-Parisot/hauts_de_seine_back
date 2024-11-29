import uuid
from sqlmodel import Session

from models.models import Product


def get_product_by_id(db: Session, product_id: uuid.UUID) -> Product:
    """
    Recherche un produit par son ID.
    """
    return db.get(Product, product_id)