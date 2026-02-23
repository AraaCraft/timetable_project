from typing import Optional
from pydantic import BaseModel, Field

class Salle(BaseModel):
    id: Optional[int] = Field(default=None)
    nom: str = Field(..., min_length=1, description="Nom de la salle (ex: Salle 1)")