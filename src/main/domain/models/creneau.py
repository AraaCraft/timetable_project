"""
Modèle de domaine et Entité de base de données pour un Créneau.

Utilisation de SQLModel avec 'table=True'.
Cela nous permet d'utiliser cette classe à la fois comme :
1. Schéma de validation de l'API (héritage Pydantic) pour les requêtes entrantes.
2. Modèle de persistance (héritage SQLAlchemy) pour la création de la table SQLite.
--> Une seule source de vérité et aucune duplication de code.
"""

from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import model_validator
from datetime import datetime, timedelta, time
import datetime as dt

class Creneau(SQLModel, table=True):
    # L'ID est généré par la BDD. Il est optionnel à la création (POST).
    id: Optional[int] = Field(default=None, primary_key=True)

    intitule_cours: str  
    nom_salle: str  

    # Règle de modélisation : Un cours en autonomie n'a pas forcément d'enseignant, 
    # le champ doit donc autoriser les valeurs nulles (Optional).
    nom_enseignant: Optional[str] = None

    # Clés de liaison (Foreign Keys logiques) vers les autres entités
    id_promotion: int
    id_salle: int

    horodatage_debut: datetime
    horodatage_fin: datetime
    
    # Valeurs par défaut sécurisées : Un cours n'est ni autonome ni annulé par défaut.
    est_autonome: bool = False
    est_annule: bool = False

    @model_validator(mode="after")
    def valider_regles_metier(self) -> "Creneau":
        """
        Validation métier globale.
        
        L'utilisation d'un validateur de modèle Pydantic (mode="after")
        permet de centraliser toutes les règles métier intrinsèques au créneau.
        L'avantage du mode 'after' est qu'il s'exécute une fois que tous les champs 
        individuels sont validés, permettant de faire des comparaisons entre eux 
        (ex: date de fin par rapport à la date de début).
        Ces règles sont évaluées avant même d'interroger la base de données (Fail-fast).
        """

        # --- FIX POUR SQLMODEL / SQLITE ---
        # SQLite ne possède pas de type 'DATETIME' natif 
        # (il stocke les dates sous forme de chaînes ISO 8601). Lors de la récupération 
        # depuis la base, il arrive que SQLModel ne parse pas automatiquement la chaîne.
        # Ce bloc garantit la robustesse du typage dynamique.
        if isinstance(self.horodatage_debut, str):
            self.horodatage_debut = dt.datetime.fromisoformat(self.horodatage_debut)
        if isinstance(self.horodatage_fin, str):
            self.horodatage_fin = dt.datetime.fromisoformat(self.horodatage_fin)
        # ----------------------------------

        # 1. Cohérence temporelle fondamentale
        if self.horodatage_fin <= self.horodatage_debut:
            raise ValueError("L'heure de fin doit être strictement après l'heure de début.")

        # 2. Règle métier : Atomicité journalière du créneau
        if self.horodatage_debut.date() != self.horodatage_fin.date():
            raise ValueError("Un créneau ne peut pas s'étaler sur plusieurs jours.")

        # 3. Règle métier : Bornes de durée (pédagogie)
        duree = self.horodatage_fin - self.horodatage_debut
        if duree < timedelta(minutes=30) or duree > timedelta(hours=4):
            raise ValueError("La durée du cours doit être comprise entre 30 minutes et 4 heures.")

        # 4. Règle métier : Plages horaires de l'établissement
        heure_debut = self.horodatage_debut.time()
        heure_fin = self.horodatage_fin.time()
        limite_matin = time(8, 15)
        limite_soir = time(17, 15)

        if heure_debut < limite_matin or heure_fin > limite_soir:
            raise ValueError("Le cours doit se dérouler dans la plage horaire autorisée (08h15 - 17h15).")

        # 5. Règle métier : Jours ouvrés (0 = Lundi, 4 = Vendredi)
        if self.horodatage_debut.weekday() > 4:
            raise ValueError("Les cours ne peuvent avoir lieu que du Lundi au Vendredi.")

        # 6. Règle métier : Responsabilité pédagogique
        # Validation conditionnelle croisée entre deux champs.
        if not self.est_autonome and not self.nom_enseignant:
            raise ValueError("Un nom d'enseignant est obligatoire si le cours n'est pas en autonomie.")

        # 7. Règle métier : Contrainte d'équipement (Exemple du Fablab)
        if "fablab" in self.intitule_cours.lower() and "fablab" not in self.nom_salle.lower():
            raise ValueError("Un cours nécessitant le Fablab doit impérativement se dérouler dans la salle Fablab.")

        return self