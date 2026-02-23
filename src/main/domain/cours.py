from typing import Optional
from pydantic import BaseModel, Field

class Cours(BaseModel):
    id: Optional[int] = Field(default=None)
    libelle: str = Field(..., min_length=2, description="Intitulé du cours (ex: Programmation Web)")