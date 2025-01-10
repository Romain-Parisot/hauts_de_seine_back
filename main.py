from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.database import  create_db
from api.main import api_router

# Création de la base de données
create_db()

# Création de l'application FastAPI
app = FastAPI()

#Allow all CORS for staging
#todo: make all cors available only in staging
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routes de l'API
app.include_router(api_router, prefix="/api/v1")
