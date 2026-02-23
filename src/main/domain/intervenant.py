from typing import Optional
from pydantic import BaseModel, Field

class Intervenant(BaseModel):
    id: Optional[int] = Field(default=None, description="ID généré par la BDD")
    nom: str = Field(..., min_length=1, description="Nom de famille")
    prenom: str = Field(..., min_length=1, description="Prénom")