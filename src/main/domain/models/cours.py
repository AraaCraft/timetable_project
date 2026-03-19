"""
Modèle de domaine représentant un Cours.

Utilisation de Pydantic (BaseModel) pour garantir la validation stricte 
des données entrantes et sortantes de l'API. Cela nous permet de rejeter 
automatiquement (erreur 422 Unprocessable Entity) les requêtes mal formées 
avant même qu'elles n'atteignent notre logique métier.
"""
from typing import Optional
from pydantic import BaseModel, Field

class Cours(BaseModel):
    # L'ID est optionnel (None par défaut) car lors de la création d'un 
    # nouveau cours via l'API (requête POST), l'ID n'existe pas encore. 
    # Il sera généré et auto-incrémenté plus tard par la base de données.
    id: Optional[int] = Field(default=None, description="Identifiant unique du cours")
    
    # Le '...' (Ellipsis) indique que ce champ est strictement obligatoire à la création.
    # Règle métier : On impose un 'min_length=2' pour éviter la création de cours
    # avec un libellé vide ou d'une seule lettre (ex: "A"), garantissant la qualité des données.
    libelle: str = Field(
        ..., 
        min_length=2, 
        description="Intitulé du cours (ex: Programmation Web)"
    )