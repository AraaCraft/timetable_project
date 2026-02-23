from typing import Optional
from pydantic import BaseModel, Field

class Promotion(BaseModel):
    id: Optional[int] = Field(default=None)
    nom: str = Field(..., min_length=2, description="Nom de la promotion (ex: DEUST 2)")