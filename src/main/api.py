import os
from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader

from src.main.domain.models import Creneau, Planning
from src.main.domain.services.planning_service import service_planning
from src.main.infrastructure.database import init_db

app = FastAPI(title="Timetable API - Session 2")

# --- CONFIGURATION DE LA SÉCURITÉ ---
# On va chercher le mot de passe dans le .env (ou on met une valeur par défaut)
CLE_SECRETE = os.getenv("API_KEY", "azerty1234")

# On définit le nom du "badge" que l'utilisateur doit présenter dans l'en-tête HTTP
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)


def verifier_autorisation(cle_fournie: str = Security(api_key_header)):
    """Vérifie si la clé fournie par l'utilisateur correspond au mot de passe."""
    if cle_fournie != CLE_SECRETE:
        raise HTTPException(
            status_code=403, detail="Accès refusé : Clé d'API invalide."
        )
    return cle_fournie


# ------------------------------------


@app.on_event("startup")
def on_startup():
    init_db()


# --- ROUTES PROTÉGÉES (Nécessitent la clé d'API) ---


@app.post(
    "/planning/programmer",
    response_model=Creneau,
    tags=["Gestion"],
    dependencies=[Depends(verifier_autorisation)],
)
def programmer_cours(nouveau_creneau: Creneau):
    try:
        return service_planning.ajouter_creneau(nouveau_creneau)
    except ValueError as e:
        # On renvoie une erreur propre si le bonus collision est déclenché
        raise HTTPException(status_code=400, detail=str(e))


@app.patch(
    "/planning/{id_creneau}/annuler",
    tags=["Gestion"],
    dependencies=[Depends(verifier_autorisation)],
)
def annuler_cours(id_creneau: int):
    """
    Annule un cours existant en passant son statut 'est_annule' à True.
    """
    try:
        cours_annule = service_planning.annuler_creneau(id_creneau)
        return {"message": "Le cours a été annulé avec succès", "cours": cours_annule}
    except ValueError as e:
        # On intercepte les erreurs de notre service (ex: ID introuvable, déjà annulé)
        raise HTTPException(status_code=400, detail=str(e))


# --- ROUTE PUBLIQUE (Consultation libre) ---


@app.get(
    "/planning/consultation/{id_promo}/{semaine}",
    response_model=Planning,
    tags=["Consultation"],
)
def consulter_planning_promo(id_promo: int, semaine: int):
    creneaux = service_planning.recuperer_planning_semaine(id_promo)
    return Planning(id_promotion=id_promo, semaine=semaine, creneaux=creneaux)
