import os
import uuid
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from db.database import get_db
from models.models import Product
from crud.crud_user import get_user_by_id
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
from math import cos, sin, radians

router = APIRouter()

@router.post("/generate_pdf/")
def generate_pdf(mairie_id: uuid.UUID, association_id: uuid.UUID, product_reference: str, db: Session = Depends(get_db)):
    mairie_user = get_user_by_id(db, mairie_id)
    association_user = get_user_by_id(db, association_id)
    product = db.query(Product).filter(Product.reference == product_reference).first()

    if not mairie_user:
        raise HTTPException(status_code=404, detail="Mairie non trouvée.")
    if not association_user:
        raise HTTPException(status_code=404, detail="Association non trouvée.")
    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")

    pdf_path = f"./uploads/pdf/{product.reference}.pdf"
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Header: centered title
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(300, 750, "Certificat de Formatage d'Ordinateur")

    # Sub-header
    c.setFont("Helvetica", 12)
    c.drawCentredString(300, 730, f"Délivré par la Mairie de {mairie_user.nom}")

    # Body content
    c.setFont("Helvetica", 11)
    text_lines = [
        f"Référence du produit : {product.reference}",
        f"Association bénéficiaire : {association_user.nom} {association_user.prenom}",
        "",
        "Ce document atteste que l'ordinateur mentionné ci-dessus a été entièrement formaté. ",
        "Toutes les données personnelles ont été supprimées conformément aux normes en vigueur, ",
        "",
        "Le processus de formatage inclut les étapes suivantes :",
        "- Analyse initiale pour vérifier l'état du disque et identifier toutes les partitions existantes.",
        "- Suppression complète des partitions et des données associées.",
        "- Réinstallation d'un système d'exploitation propre et exempt de toute donnée résiduelle.",
        "- Configuration minimale pour permettre un usage immédiat par les nouveaux bénéficiaires.",
        "",
        "L'objectif de cette opération est double :",
        "1. Assurer la confidentialité des données de l'ancien propriétaire.",
        "2. Préparer l'appareil pour qu'il soit pleinement opérationnel pour de nouveaux usages.",
        "",
        "Nous tenons à vous remercier chaleureusement pour votre générosité. Grâce à votre contribution,",
        "vous participez activement à une démarche solidaire et responsable, en réduisant les déchets électroniques ",
        "et en favorisant l'accès au numérique pour tous.",
        "",
        "Ce certificat est signé par la mairie et garantit que toutes les procédures ont été suivies.",
    ]

    y = 670
    for line in text_lines:
        c.drawString(60, y, line)
        y -= 20

    # Signature section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y - 30, f"Signé par la Mairie de {mairie_user.nom}")

    c.setLineWidth(1)
    c.setStrokeColor(colors.darkblue)
    c.line(100, y - 40, 300, y - 40)

    # Footer: Date and circular text
    c.setFont("Helvetica", 10)
    c.drawString(100, 50, f"Date : {datetime.now().strftime('%d-%m-%Y')}")
    c.drawRightString(500, 50, "Page 1/1")

    # Circular logo or text
    texte_cercle = "Liberté, égalité, fraternité,"
    radius = 65
    angle_step = 360 / len(texte_cercle.replace(" ", ""))
    current_angle = 0

    for char in texte_cercle.replace(" ", ""):
        x = 450 + radius * cos(radians(current_angle))
        y = 150 + radius * sin(radians(current_angle))
        c.saveState()
        c.translate(x, y)
        c.rotate(current_angle + 90)
        c.setFont("Helvetica", 8)
        c.drawString(-3, 0, char)
        c.restoreState()
        current_angle += angle_step

    text_maire_de = "Maire de"
    text_nom_mairie = f"{mairie_user.nom}"
    text_maire_de_width = c.stringWidth(text_maire_de, "Helvetica-Bold", 10)
    text_nom_mairie_width = c.stringWidth(text_nom_mairie, "Helvetica-Bold", 10)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(450 - text_maire_de_width / 2, 140, text_maire_de)
    c.drawString(450 - text_nom_mairie_width / 2, 125, text_nom_mairie)

    c.save()

    with open(pdf_path, "wb") as f:
        f.write(buffer.getvalue())

    return {"message": "PDF généré avec succès", "file_path": pdf_path}


@router.get("/get_pdf/{product_reference}")
def get_pdf(product_reference: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.reference == product_reference).first()

    if not product:
        raise HTTPException(status_code=404, detail="Produit non trouvé.")
    
    pdf_path = f"./uploads/pdf/{product_reference}.pdf"

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF non trouvé.")

    return FileResponse(pdf_path)
