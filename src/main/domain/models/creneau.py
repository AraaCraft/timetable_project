from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import model_validator
from datetime import datetime, timedelta, time
import datetime as dt

class Creneau(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Informations descriptives
    intitule_cours: str # Ex: "Algorithmique"
    
    # L'enseignant devient optionnel car un cours peut être en autonomie
    nom_enseignant: Optional[str] = None 
    
    nom_salle: str      # Ex: "Salle 1" ou "Fablab"
    
    # Identifiants de liaison
    id_promotion: int
    id_salle: int
    
    horodatage_debut: datetime
    horodatage_fin: datetime
    est_autonome: bool = False
    est_annule: bool = False

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

        # 6. Règle métier : Autonomie vs Cours dirigé
        # Si le cours n'est PAS autonome, alors il FAUT un enseignant
        if not self.est_autonome and not self.nom_enseignant:
            raise ValueError("Un nom d'enseignant est obligatoire si le cours n'est pas en autonomie.")

        # 7. Règle métier : Salle spécifique (Exemple du Fablab)
        # Si le mot "fablab" est dans le titre du cours, il doit être dans le Fablab
        if "fablab" in self.intitule_cours.lower() and "fablab" not in self.nom_salle.lower():
            raise ValueError("Un cours nécessitant le Fablab doit impérativement se dérouler dans la salle Fablab.")

        return self