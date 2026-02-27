# src/main/api.py
from fastapi import FastAPI, HTTPException
from typing import List
from src.main.domain.models import Creneau, Planning

app = FastAPI(
    title="Timetable API",
    description="API de gestion d'emploi du temps (Projet)",
    version="0.1.0"
)

# --- Base de données en mémoire temporaire ---
db_creneaux: List[Creneau] = []
compteur_id_creneau = 1

# --- Routes (Endpoints) ---

@app.post("/planning/programmer", response_model=Creneau, tags=["Gestion"])
def programmer_cours(nouveau_creneau: Creneau):
    """
    Ajoute un nouveau cours. Pydantic valide automatiquement les horaires
    """
    global compteur_id_creneau
    
    # Simulation de la base de données
    nouveau_creneau.id = compteur_id_creneau
    compteur_id_creneau += 1
    
    db_creneaux.append(nouveau_creneau)
    return nouveau_creneau


@app.get("/planning/consultation/{id_promo}/{semaine}", response_model=Planning, tags=["Consultation"])
def consulter_planning_promo(id_promo: int, semaine: int):
    """
    Génère et renvoie le planning complet d'une promotion pour une semaine donnée.
    """
    # On filtre les créneaux pour ne garder que ceux de la bonne promo
    creneaux_promo = [c for c in db_creneaux if c.id_promotion == id_promo]
    
    planning_resultat = Planning(
        id_promotion=id_promo,
        semaine=semaine,
        creneaux=creneaux_promo
    )
    
    return planning_resultat