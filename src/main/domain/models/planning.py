from pydantic import BaseModel, Field
from typing import List
from .creneau import Creneau

class Planning(BaseModel):
    id_promotion: int = Field(..., description="L'ID de la promotion concernée")
    semaine: int = Field(..., ge=1, le=52, description="Numéro de la semaine dans l'année")
    creneaux: List[Creneau] = Field(default=[], description="Liste des cours de cette semaine")