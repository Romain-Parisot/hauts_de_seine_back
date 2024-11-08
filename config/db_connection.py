import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine, Session, Field

#Chargement des variables d'environnement
load_dotenv()

#variable de connexion à la base de données
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

#URL de connexion à la base de données
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

#Création de la connexion à la base de données
engine = create_engine(DATABASE_URL, echo=True)

#Création de la base de données
def create_db():
    SQLModel.metadata.create_all(engine)

#Test de connexion à la base de données
def test_connection():
    try:
        create_db()
        print("Connexion réussie à la base de données.")
    except Exception as e:
        print("Erreur de connexion à la base de données :", e)

test_connection()
