from fastapi import FastAPI
from db.database import  create_db
from api.main import api_router

# Création de la base de données
create_db()

# Création de l'application FastAPI
app = FastAPI()

# Inclusion des routes de l'API
app.include_router(api_router, prefix="/api/v1")