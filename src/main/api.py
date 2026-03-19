import os
import logging 
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader

from src.main.domain.models import Creneau, Planning
from src.main.domain.services.planning_service import service_planning
from src.main.infrastructure.database import init_db

# --- CONFIGURATION DES LOGS ---
import logging
from logging.handlers import RotatingFileHandler

# Configuration de la rotation : 5 Mo maximum, on garde 3 archives
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
        logging.StreamHandler()  # Garde l'affichage console
    ]
)
logger = logging.getLogger("timetable-api")
# ------------------------------

app = FastAPI(title="Timetable API - Session 2")

CLE_SECRETE = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

def verifier_autorisation(cle_fournie: str = Security(api_key_header)):
    if cle_fournie != CLE_SECRETE:
        logger.warning(f"Tentative d'accès refusée avec la clé : {cle_fournie[:3]}***") 
        raise HTTPException(
            status_code=403, detail="Accès refusé : Clé d'API invalide."
        )
    return cle_fournie

@app.on_event("startup")
def on_startup():
    logger.info("Démarrage de l'API et initialisation de la base de données") 
    init_db()

@app.post(
    "/planning/programmer",
    response_model=Creneau,
    tags=["Gestion"],
    dependencies=[Depends(verifier_autorisation)],
)
def programmer_cours(nouveau_creneau: Creneau):
    try:
        resultat = service_planning.ajouter_creneau(nouveau_creneau)
        logger.info(f"Nouveau cours programmé : ID {resultat.id} pour la promo {nouveau_creneau.id_promotion}")
        return resultat
    except ValueError as e:
        logger.error(f"Erreur de programmation : {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.patch(
    "/planning/{id_creneau}/annuler",
    tags=["Gestion"],
    dependencies=[Depends(verifier_autorisation)],
)
def annuler_cours(id_creneau: int):
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
    creneaux = service_planning.recuperer_planning_semaine(id_promo)
    return Planning(id_promotion=id_promo, semaine=semaine, creneaux=creneaux)