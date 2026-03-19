"""
Modèle d'agrégation représentant le Planning d'une semaine.

Architecture (Response Model / DTO) :
Ce modèle n'est pas persisté en base de données (ce n'est pas un SQLModel). 
Il s'agit d'un objet de transfert de données utilisé exclusivement pour formater 
la réponse de notre API lors de la consultation (/planning/consultation/...).
Il agrège les créneaux récupérés en base pour les présenter proprement au client (Front-end).
"""
from pydantic import BaseModel, Field
from typing import List
from .creneau import Creneau

class Planning(BaseModel):
    # L'Ellipsis (...) rend l'ID de promotion obligatoire pour générer un planning.
    id_promotion: int = Field(..., description="L'ID de la promotion concernée")
    
    # Règle de validation métier sur le calendrier :
    # 'ge' (Greater or Equal) et 'le' (Less or Equal) garantissent que la semaine 
    # demandée est cohérente (entre 1 et 52). Si l'utilisateur demande la semaine 99,
    # Pydantic bloque la requête avant même de chercher dans la base de données.
    semaine: int = Field(
        ..., ge=1, le=52, description="Numéro de la semaine dans l'année"
    )
    
    # Composition : Un planning contient une liste d'objets Creneau.
    # L'initialisation par défaut à une liste vide [] (default=[]) est cruciale.
    # Si une promotion n'a pas de cours une semaine donnée, l'API renverra 
    # une liste vide au lieu d'une erreur (ou d'un type 'None' qui ferait 
    # planter le front-end).
    creneaux: List[Creneau] = Field(
        default=[], description="Liste des cours de cette semaine"
    )