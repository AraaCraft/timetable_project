"""
Modèle de domaine représentant un Intervenant (Enseignant).

Architecture (DTO) : 
Tout comme pour le modèle 'Cours', nous utilisons ici Pydantic pur (BaseModel) 
pour définir un Data Transfer Object. L'objectif de cette classe est 
strictement de valider la "payload" (le corps de la requête HTTP entrante) 
avant tout traitement métier.
"""
from typing import Optional
from pydantic import BaseModel, Field

class Intervenant(BaseModel):
    # L'ID est généré par la base de données. Il doit donc être optionnel 
    # lors de la réception d'une requête POST de création d'un intervenant.
    id: Optional[int] = Field(default=None, description="ID généré par la BDD")
    
    # Règle de validation des données :
    # Le type 'str' natif de Python accepte les chaînes vides ("").
    # L'utilisation de Field(..., min_length=1) force FastAPI à rejeter 
    # automatiquement les requêtes contenant un nom ou un prénom vide, 
    # garantissant ainsi l'intégrité des données dans la base.
    nom: str = Field(..., min_length=1, description="Nom de famille")
    prenom: str = Field(..., min_length=1, description="Prénom")