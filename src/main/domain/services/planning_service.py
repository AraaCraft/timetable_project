from sqlmodel import Session, select, or_
from typing import List
from src.main.infrastructure.database import engine
from src.main.domain.models import Creneau

class PlanningService:
    def verifier_disponibilite(self, session: Session, nouveau: Creneau) -> None:
        """
        Vérifie si la salle OU la promo est déjà occupée.
        """
        # On cherche les créneaux qui concernent SOIT la même promo, SOIT la même salle
        statement = select(Creneau).where(
            or_(
                Creneau.id_promotion == nouveau.id_promotion,
                Creneau.id_salle == nouveau.id_salle
            )
        )
        existants = session.exec(statement).all()
        
        for existant in existants:
            # Vérification du chevauchement d'horaires
            if (nouveau.horodatage_debut < existant.horodatage_fin and 
                nouveau.horodatage_fin > existant.horodatage_debut):
                
                if existant.id_promotion == nouveau.id_promotion:
                    raise ValueError(f"La promotion {nouveau.id_promotion} a déjà un cours à ce moment.")
                if existant.id_salle == nouveau.id_salle:
                    raise ValueError(f"La salle '{existant.nom_salle}' est déjà occupée.")

    def ajouter_creneau(self, creneau: Creneau) -> Creneau:
        with Session(engine) as session:
            self.verifier_disponibilite(session, creneau)
            session.add(creneau)
            session.commit()
            session.refresh(creneau)
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