"""
Modèle de domaine représentant une Promotion d'étudiants.

Architecture (Séparation des préoccupations) :
L'isoler dans son propre fichier 
respecte le principe de responsabilité unique (SRP). C'est un DTO (Data Transfer Object) dédié à la validation des données de promotion entrantes.
"""
from typing import Optional
from pydantic import BaseModel, Field

class Promotion(BaseModel):
    id: Optional[int] = Field(default=None)
    
    # Règle métier : On impose 2 caractères minimum pour éviter les fautes 
    # de frappe du type "A" ou "1" et forcer des noms descriptifs ("L1", "M2").
    nom: str = Field(..., min_length=2, description="Nom de la promotion (ex: DEUST 2)")