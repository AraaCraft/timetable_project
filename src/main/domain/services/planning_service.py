from sqlmodel import Session, select
from typing import List
from src.main.infrastructure.database import engine
from src.main.domain.models import Creneau

class PlanningService:
    def verifier_collision_promo(self, session: Session, nouveau: Creneau) -> bool:
        """
        Vérifie si la promotion est déjà occupée.
        On passe la 'session' en argument pour faire la requête SQL.
        """
        statement = select(Creneau).where(
            Creneau.id_promotion == nouveau.id_promotion
        )
        creneaux_existants = session.exec(statement).all()
        
        for existant in creneaux_existants:
            if (nouveau.horodatage_debut < existant.horodatage_fin and 
                nouveau.horodatage_fin > existant.horodatage_debut):
                return True
        return False

    def ajouter_creneau(self, creneau: Creneau) -> Creneau:
        # On ouvre une session de base de données
        with Session(engine) as session:
            if self.verifier_collision_promo(session, creneau):
                raise ValueError("La promotion a déjà un cours sur ce créneau horaire.")
            
            session.add(creneau) # On prépare l'ajout
            session.commit()      # On enregistre dans le fichier .db
            session.refresh(creneau) # On récupère l'ID généré par SQLite
            return creneau

    # def recuperer_planning_semaine(self, id_promo: int) -> List[Creneau]:
    #     with Session(engine) as session:
    #         statement = select(Creneau).where(Creneau.id_promotion == id_promo)
    #         return session.exec(statement).all()
    def recuperer_planning_semaine(self, id_promo: int) -> List[Creneau]:
        with Session(engine) as session:
        # On demande TOUS les créneaux de cette promo, peu importe la semaine
            statement = select(Creneau).where(Creneau.id_promotion == id_promo)
            resultats = session.exec(statement).all()
            print(f"DEBUG: Nombre de créneaux trouvés en base : {len(resultats)}")
            return resultats

# Instance unique
service_planning = PlanningService()