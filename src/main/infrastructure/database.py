import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# 1. On charge les variables cachées dans le fichier .env
load_dotenv()

# 2. On récupère l'URL (avec SQLite en valeur par défaut au cas où le .env manque)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# 3. Petite subtilité pour SQLite et FastAPI (pour éviter les erreurs de threads)
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# 4. On crée le moteur une seule fois pour toute l'application
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session