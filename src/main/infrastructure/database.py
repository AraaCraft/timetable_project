"""
Couche Infrastructure : Gestion de la persistance et connexion à la base de données.

Architecture (Pattern Factory & Dependency Injection) :
Ce fichier isole toute la configuration de la base de données. 
Le reste de l'application n'a pas besoin de savoir si on utilise SQLite, PostgreSQL ou MySQL. Tout est géré ici via les variables d'environnement.
"""
import os
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# 1. Séparation de la configuration et du code (Méthodologie "12-Factor App")
load_dotenv()

# 2. Récupération de l'URL de connexion. 
# La valeur par défaut 'sqlite:///database.db' permet de faire tourner 
# l'application en local (développement) même si le fichier .env est absent, 
# tout en permettant de basculer sur une vraie BDD en production via la variable.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# 3. Gestion de la concurrence (Thread Safety)
# Justification technique critique : FastAPI gère les requêtes de manière 
# asynchrone avec de multiples "threads". 
# Par défaut, SQLite interdit qu'une connexion ouverte dans un thread soit 
# utilisée dans un autre, ce qui fait planter FastAPI. 
# On désactive cette sécurité uniquement pour SQLite.
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

# 4. Création du moteur (Engine)
# Le moteur est créé UNE SEULE FOIS au démarrage. Il gère le "pool" de connexions.
# echo=True permet d'afficher les vraies requêtes SQL générées dans la console 
# pour faciliter le débogage (à désactiver en production pure).
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


def init_db():
    """
    Crée les tables physiques dans la base de données.
    Cette fonction se base sur les modèles importés dans 'models/__init__.py'.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Générateur de session pour l'Injection de Dépendance (Dependency Injection).
    
    Justification : Utilisé avec 'Depends()' dans les routes FastAPI.
    Le mot-clé 'yield' permet de fournir une session à la route, puis de 
    reprendre l'exécution APRÈS que la requête HTTP soit terminée afin 
    de fermer proprement la connexion, évitant ainsi les fuites de mémoire 
    ou le verrouillage de la base (Database Locked).
    """
    with Session(engine) as session:
        yield session