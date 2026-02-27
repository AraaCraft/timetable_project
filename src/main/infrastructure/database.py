from sqlmodel import SQLModel, create_engine, Session
import os

# Crée le chemin vers la base de données à la racine du projet
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sqlite_url = f"sqlite:///{os.path.join(base_dir, 'database.db')}"

engine = create_engine(sqlite_url, echo=True)

def init_db():
    # Cette commande crée le fichier database.db et les tables
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session