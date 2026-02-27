from typing import List
from src.main.domain.models import Creneau

class PlanningService:
    def __init__(self):
        # La base de données temporaire se déplace ici
        self.db_creneaux: List[Creneau] = []
        self._compteur_id = 1

    def verifier_collision_promo(self, nouveau: Creneau) -> bool:
        """
        BONUS : Vérifie si la promotion est déjà occupée sur ce créneau.
        """
        for existant in self.db_creneaux:
            if existant.id_promotion == nouveau.id_promotion:
                # Vérification du chevauchement d'horaires
                if (nouveau.horodatage_debut < existant.horodatage_fin and 
                    nouveau.horodatage_fin > existant.horodatage_debut):
                    return True # Il y a une collision !
        return False

    def ajouter_creneau(self, creneau: Creneau) -> Creneau:
        if self.verifier_collision_promo(creneau):
            raise ValueError("La promotion a déjà un cours sur ce créneau horaire.")
        
        creneau.id = self._compteur_id
        self._compteur_id += 1
        self.db_creneaux.append(creneau)
        return creneau

    def recuperer_planning_semaine(self, id_promo: int) -> List[Creneau]:
        return [c for c in self.db_creneaux if c.id_promotion == id_promo]

# On crée une instance unique (Singleton) pour toute l'appli
service_planning = PlanningService()