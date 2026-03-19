"""
Modèle de domaine représentant une Salle de cours.

Architecture (Évolutivité) :
Ce modèle DTO valide les requêtes liées aux salles. Son isolation permet  d'envisager facilement des évolutions futures sans casser l'API, comme  l'ajout d'une notion de capacité maximale (ex: capacite: int) ou  d'équipements spécifiques (ex: a_projecteur: bool).
"""
from typing import Optional
from pydantic import BaseModel, Field

class Salle(BaseModel):
    id: Optional[int] = Field(default=None)
    
    # Règle métier : 1 caractère minimum, car une salle peut techniquement 
    # s'appeler "A" ou "B" dans certains établissements, contrairement aux promos.
    nom: str = Field(..., min_length=1, description="Nom de la salle (ex: Salle 1)")