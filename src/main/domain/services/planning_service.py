"""
Couche de Service Métier (Service Layer) pour la gestion du planning.

Architecture : 
Toute l'intelligence de l'application (vérification des conflits, annulations) 
est isolée ici. FastAPI (dans api.py) ne fait que faire transiter les requêtes vers ce service. 
Avantages : 
1. Réutilisabilité : On pourrait utiliser ce service avec une interface CLI ou un autre framework.
2. Testabilité : On peut tester cette logique métier avec Pytest sans jamais lancer l'API.
"""

from sqlmodel import Session, select, or_
from src.main.domain.models.creneau import Creneau
from src.main.infrastructure.database import engine


class PlanningService:
    def verifier_conflits(self, session: Session, nouveau: Creneau):
        """
        Vérifie si un nouveau créneau entre en collision avec le planning existant.
        
        Justification technique (Optimisation BDD) :
        Au lieu de récupérer TOUS les créneaux de la base en Python pour les filtrer, 
        on délègue le travail au moteur SQL via la clause 'where'. On ne rapatrie 
        que les cours de la même salle OU de la même promo.
        """
        # 1. On cherche les cours de la même salle OU de la même promo...
        # 2. ET on ignore ceux qui sont annulés !
        # Le '# noqa: E712' est obligatoire ici car SQLAlchemy exige d'utiliser '== False' 
        # pour générer la requête SQL 'IS FALSE', ce qui contredit la norme standard de Python.
        statement = select(Creneau).where(
            or_(
                Creneau.id_salle == nouveau.id_salle,
                Creneau.id_promotion == nouveau.id_promotion,
            ),
            Creneau.est_annule == False  # noqa: E712
        )
        existants = session.exec(statement).all()

        for existant in existants:
            # Algorithme mathématique de détection de chevauchement (Overlap).
            # Règle universelle : Deux intervalles A et B se croisent SI ET SEULEMENT SI
            # (Début A < Fin B) ET (Fin A > Début B).
            if (
                nouveau.horodatage_debut < existant.horodatage_fin
                and nouveau.horodatage_fin > existant.horodatage_debut
            ):
                # On identifie précisément la cause du conflit pour renvoyer une erreur claire.
                if existant.id_salle == nouveau.id_salle:
                    raise ValueError(f"La salle '{nouveau.nom_salle}' est déjà occupée sur ce créneau.")
                if existant.id_promotion == nouveau.id_promotion:
                    raise ValueError(f"La promotion {nouveau.id_promotion} a déjà un cours sur ce créneau.")

    def ajouter_creneau(self, creneau: Creneau) -> Creneau:
        """
        Orchestre l'ajout sécurisé d'un créneau en base de données.
        L'utilisation du bloc 'with Session(engine)' garantit que la connexion
        à la base de données sera toujours proprement fermée, même en cas d'erreur.
        """
        with Session(engine) as session:
            # On passe la session à la méthode de vérification pour rester dans la même transaction
            self.verifier_conflits(session, creneau)
            session.add(creneau)
            session.commit()
            session.refresh(creneau)
            return creneau

    def annuler_creneau(self, id_creneau: int) -> Creneau:
        """
        Annule un cours existant.
        
        Choix architectural (Soft Delete vs Hard Delete) :
        Plutôt que d'utiliser 'session.delete(cours)' pour effacer définitivement
        la ligne (Hard Delete), nous basculons le booléen 'est_annule' à True (Soft Delete).
        Justification : Dans un système d'information universitaire, il faut garder
        la trace (audit) des annulations pour les statistiques, la paie des profs, 
        ou la justification des absences.
        """
        with Session(engine) as session:
            # 1. On va chercher le cours directement grâce à son ID
            cours = session.get(Creneau, id_creneau)

            # 2. Vérifications de base (Gestion des erreurs fail-fast)
            if not cours:
                raise ValueError(f"Impossible d'annuler : le cours avec l'ID {id_creneau} n'existe pas.")
            if cours.est_annule:
                raise ValueError("Ce cours est déjà annulé.")

            # 3. On applique la modification (Soft delete)
            cours.est_annule = True

            # 4. On sauvegarde en base de données
            session.add(cours)
            session.commit()
            session.refresh(cours)

            return cours

# Implémentation du pattern Singleton.
# On exporte une instance unique du service. Cela évite de réinstancier 
# la classe à chaque requête HTTP, optimisant ainsi la mémoire de notre API.
service_planning = PlanningService()