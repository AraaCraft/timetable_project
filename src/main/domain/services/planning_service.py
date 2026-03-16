from sqlmodel import Session, select, or_
from src.main.domain.models.creneau import Creneau
from src.main.infrastructure.database import engine

class PlanningService:
    def verifier_conflits(self, session: Session, nouveau: Creneau):
        # 1. On cherche les cours de la même salle OU de la même promo...
        # 2. ET on ignore ceux qui sont annulés !
        statement = select(Creneau).where(
            or_(
                Creneau.id_salle == nouveau.id_salle,
                Creneau.id_promotion == nouveau.id_promotion
            ),
            Creneau.est_annule == False 
        )
        existants = session.exec(statement).all()

        for existant in existants:
            # Vérification du chevauchement d'horaires
            if (nouveau.horodatage_debut < existant.horodatage_fin and 
                nouveau.horodatage_fin > existant.horodatage_debut):
                
                if existant.id_salle == nouveau.id_salle:
                    raise ValueError(f"La salle '{nouveau.nom_salle}' est déjà occupée sur ce créneau.")
                if existant.id_promotion == nouveau.id_promotion:
                    raise ValueError(f"La promotion {nouveau.id_promotion} a déjà un cours sur ce créneau.")

    def ajouter_creneau(self, creneau: Creneau) -> Creneau:
        with Session(engine) as session:
            self.verifier_conflits(session, creneau)
            session.add(creneau)
            session.commit()
            session.refresh(creneau)
            return creneau

    def annuler_creneau(self, id_creneau: int) -> Creneau:
        with Session(engine) as session:
            # 1. On va chercher le cours directement grâce à son ID
            cours = session.get(Creneau, id_creneau)
            
            # 2. Vérifications de base
            if not cours:
                raise ValueError(f"Impossible d'annuler : le cours avec l'ID {id_creneau} n'existe pas.")
            if cours.est_annule:
                raise ValueError("Ce cours est déjà annulé.")
                
            # 3. On applique la modification (soft delete)
            cours.est_annule = True
            
            # 4. On sauvegarde en base de données
            session.add(cours)
            session.commit()
            session.refresh(cours)
            
            return cours

# Instance unique
service_planning = PlanningService()