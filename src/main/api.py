from fastapi import FastAPI, HTTPException
from src.main.domain.models import Creneau, Planning
from src.main.domain.services.planning_service import service_planning
from src.main.infrastructure.database import init_db

app = FastAPI(title="Timetable API - Session 2")

@app.on_event("startup")
def on_startup():
    init_db()

@app.post("/planning/programmer", response_model=Creneau, tags=["Gestion"])
def programmer_cours(nouveau_creneau: Creneau):
    try:
        return service_planning.ajouter_creneau(nouveau_creneau)
    except ValueError as e:
        # On renvoie une erreur propre si le bonus collision est déclenché
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/planning/consultation/{id_promo}/{semaine}", response_model=Planning, tags=["Consultation"])
def consulter_planning_promo(id_promo: int, semaine: int):
    creneaux = service_planning.recuperer_planning_semaine(id_promo)
    return Planning(id_promotion=id_promo, semaine=semaine, creneaux=creneaux)