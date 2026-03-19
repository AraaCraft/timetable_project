"""
Couche de Présentation / Routage (API).

Choix architectural (Clean Architecture) :
Ce fichier ne contient AUCUNE logique métier. Son seul rôle est d'agir comme 
un "contrôleur" : il reçoit les requêtes HTTP, vérifie les autorisations, 
délègue le travail complexe au 'PlanningService', et traduit les résultats 
(ou les erreurs) en réponses HTTP standardisées (JSON, Code 200, Code 400).
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader

from src.main.domain.models import Creneau, Planning
from src.main.domain.services.planning_service import service_planning
from src.main.infrastructure.database import init_db

# --- CONFIGURATION DES LOGS ---
# Mise en place d'une stratégie de traçabilité robuste.
# Le 'RotatingFileHandler' empêche le fichier de logs de saturer le disque dur 
# du serveur en limitant sa taille à 5 Mo et en archivant les 3 derniers.
log_handler = RotatingFileHandler(
    "app.log", 
    maxBytes=5 * 1024 * 1024,  # 5 Mo en octets
    backupCount=3,             # Garde app.log.1, app.log.2, app.log.3
    encoding="utf-8"
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        log_handler,
        logging.StreamHandler()  # Garde l'affichage console pour le debug
    ]
)
logger = logging.getLogger("timetable-api")
# -----------------------------------------------

app = FastAPI(title="Timetable API - Session 2")

# --- CONFIGURATION DE LA SÉCURITÉ ---
CLE_SECRETE = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verifier_autorisation(cle_fournie: str = Security(api_key_header)):
    """
    Middleware d'authentification par Injection de Dépendance.
    Vérifie la présence et la validité de la clé dans l'en-tête HTTP.
    """
    if cle_fournie != CLE_SECRETE:
        # Sécurité : On masque la clé dans les logs pour éviter les fuites de données
        logger.warning(f"Tentative d'accès refusée avec la clé : {cle_fournie[:3]}***") 
        raise HTTPException(
            status_code=403, detail="Accès refusé : Clé d'API invalide."
        )
    return cle_fournie

@app.on_event("startup")
def on_startup():
    """Événement déclenché automatiquement au démarrage du serveur."""
    logger.info("Démarrage de l'API et initialisation de la base de données") 
    init_db()

# --- ROUTES DE L'API ---

@app.post(
    "/planning/programmer",
    response_model=Creneau,
    tags=["Gestion"],
    dependencies=[Depends(verifier_autorisation)],
)
def programmer_cours(nouveau_creneau: Creneau):
    """Route de création d'un créneau. Protégée par la clé d'API."""
    try:
        # On délègue toute la logique au Service Layer
        resultat = service_planning.ajouter_creneau(nouveau_creneau)
        logger.info(f"Nouveau cours programmé : ID {resultat.id} pour la promo {nouveau_creneau.id_promotion}")
        return resultat
    except ValueError as e:
        # Traduction des erreurs métier (Python) en erreurs HTTP (Web)
        logger.error(f"Erreur de programmation : {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.patch(
    "/planning/{id_creneau}/annuler",
    tags=["Gestion"],
    dependencies=[Depends(verifier_autorisation)],
)
def annuler_cours(id_creneau: int):
    """
    Route d'annulation (Soft Delete).
    Modifie partiellement la ressource (est_annule=True) 
    au lieu de la supprimer physiquement (DELETE).
    """
    try:
        cours_annule = service_planning.annuler_creneau(id_creneau)
        logger.info(f"Cours annulé avec succès : ID {id_creneau}") 
        return {"message": "Le cours a été annulé avec succès", "cours": cours_annule}
    except ValueError as e:
        logger.warning(f"Échec de l'annulation pour l'ID {id_creneau} : {str(e)}") 
        raise HTTPException(status_code=400, detail=str(e))

@app.get(
    "/planning/consultation/{id_promo}/{semaine}",
    response_model=Planning,
    tags=["Consultation"],
)
def consulter_planning_promo(id_promo: int, semaine: int):
    """
    Route publique (pas de clé d'API requise).
    Retourne l'agrégation des créneaux formatée dans le modèle 'Planning'.
    """
    creneaux = service_planning.recuperer_planning_semaine(id_promo)
    return Planning(id_promotion=id_promo, semaine=semaine, creneaux=creneaux)