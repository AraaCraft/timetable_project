from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
from pydantic import field_validator, model_validator
from datetime import datetime, timedelta, time
import datetime as dt

class Creneau(SQLModel, table=True):
    # L'ID est optionnel car SQLite le génère tout seul
    id: Optional[int] = Field(default=None, primary_key=True)
    id_cours: int
    id_intervenant: int
    id_salle: int
    id_promotion: int
    horodatage_debut: datetime
    horodatage_fin: datetime

    @model_validator(mode='after')
    def valider_regles_metier(self) -> 'Creneau':
        # --- FIX POUR SQLMODEL / SQLITE ---
        # Si SQLModel nous donne du texte, on le transforme en vraie date
        if isinstance(self.horodatage_debut, str):
            self.horodatage_debut = dt.datetime.fromisoformat(self.horodatage_debut)
        if isinstance(self.horodatage_fin, str):
            self.horodatage_fin = dt.datetime.fromisoformat(self.horodatage_fin)
        # ----------------------------------

        # 1. Cohérence de base
        if self.horodatage_fin <= self.horodatage_debut:
            raise ValueError("L'heure de fin doit être strictement après l'heure de début.")

        # 2. Règle métier : Le cours doit être sur une seule journée
        if self.horodatage_debut.date() != self.horodatage_fin.date():
            raise ValueError("Un créneau ne peut pas s'étaler sur plusieurs jours.")

        # 3. Règle métier : Durée de 30 minutes à 4 heures maximum
        duree = self.horodatage_fin - self.horodatage_debut
        if duree < timedelta(minutes=30) or duree > timedelta(hours=4):
            raise ValueError("La durée du cours doit être comprise entre 30 minutes et 4 heures.")

        # 4. Règle métier : Entre 08h15 et 17h15
        heure_debut = self.horodatage_debut.time()
        heure_fin = self.horodatage_fin.time()
        
        limite_matin = time(8, 15)
        limite_soir = time(17, 15)

        if heure_debut < limite_matin or heure_fin > limite_soir:
            raise ValueError("Le cours doit se dérouler dans la plage horaire autorisée (08h15 - 17h15).")

        # 5. Règle métier : Du Lundi (0) au Vendredi (4)
        if self.horodatage_debut.weekday() > 4:
            raise ValueError("Les cours ne peuvent avoir lieu que du Lundi au Vendredi.")

        return self