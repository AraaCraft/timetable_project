"""
Suite de tests automatisés (Unitaires et d'Intégration) avec Pytest.

Architecture (Assurance Qualité & CI/CD) :
Ce fichier est le filet de sécurité de notre application. Il est exécuté 
automatiquement par GitHub Actions à chaque push. 
Nous avons adopté une approche orientée "Edge Cases" (cas aux limites) : 
on ne teste pas seulement si le code marche quand tout va bien, 
mais on vérifie surtout qu'il plante correctement quand les règles métier 
sont violées (Fail-Fast).
"""

import pytest
from datetime import datetime
from src.main.domain.models.creneau import Creneau
from src.main.domain.services.planning_service import PlanningService

# ==========================================
# DONNÉES DE BASE (Helpers / Fixtures)
# ==========================================

def base_creneau_data() -> dict:
    """
    Retourne un dictionnaire de données valides par défaut.
    
    Isolation des tests :
    Pourquoi une fonction et pas une simple variable globale ? 
    Parce qu'en Python, les dictionnaires sont mutables. Si on utilisait une 
    variable globale, le Test A modifierait les données du Test B (Side-effect). 
    En appelant cette fonction, chaque test reçoit un dictionnaire tout neuf, 
    garantissant l'isolation totale des tests.
    """
    return {
        "intitule_cours": "Mathématiques",
        "nom_enseignant": "M. Gauss",
        "nom_salle": "Salle 1",
        "id_salle": 1,
        "id_promotion": 1,
        "horodatage_debut": datetime(2026, 3, 23, 10, 0),
        "horodatage_fin": datetime(2026, 3, 23, 12, 0),
        "est_autonome": False,
        "est_annule": False
    }

# ==========================================
# LES TESTS UNITAIRES (Validation du Modèle)
# ==========================================

def test_creneau_valide():
    """Test du 'Happy Path' : vérifie qu'une donnée parfaite est bien acceptée."""
    data = base_creneau_data()
    creneau = Creneau(**data)
    assert creneau.intitule_cours == "Mathématiques"

def test_heure_fin_avant_heure_debut():
    """
    Test unitaire d'incohérence temporelle.
    L'utilisation de 'pytest.raises' permet d'affirmer que notre application 
    réagit bien en levant une exception ValueError avec le bon message.
    """
    data = base_creneau_data()
    data["horodatage_debut"] = datetime(2026, 3, 23, 12, 0)
    data["horodatage_fin"] = datetime(2026, 3, 23, 10, 0)
    with pytest.raises(ValueError, match="L'heure de fin doit être strictement après l'heure de début"):
        Creneau.model_validate(data)

def test_creneau_sur_plusieurs_jours():
    data = base_creneau_data()
    data["horodatage_fin"] = datetime(2026, 3, 24, 10, 0)
    with pytest.raises(ValueError, match="Un créneau ne peut pas s'étaler sur plusieurs jours"):
        Creneau.model_validate(data)

def test_duree_limites():
    data = base_creneau_data()
    data["horodatage_fin"] = datetime(2026, 3, 23, 10, 15) # 15 min (trop court)
    with pytest.raises(ValueError, match="comprise entre 30 minutes et 4 heures"):
        Creneau.model_validate(data)
        
def test_horaires_plage_autorisee():
    data = base_creneau_data()
    # On met 7h à 9h (durée 2h = OK), mais 7h est hors plage (8h-20h)
    data["horodatage_debut"] = datetime(2026, 3, 23, 7, 0) 
    data["horodatage_fin"] = datetime(2026, 3, 23, 9, 0)
    with pytest.raises(ValueError, match="plage horaire autorisée"):
        Creneau.model_validate(data)

def test_cours_le_week_end():
    data = base_creneau_data()
    data["horodatage_debut"] = datetime(2026, 3, 22, 10, 0) # Un dimanche
    data["horodatage_fin"] = datetime(2026, 3, 22, 12, 0)
    with pytest.raises(ValueError, match="du Lundi au Vendredi"):
        Creneau.model_validate(data)


# ==========================================
# LES TESTS D'INTÉGRATION (Service & BDD)
# ==========================================

def test_autonomie_requiert_enseignant():
    data = base_creneau_data()
    data["nom_enseignant"] = None
    data["est_autonome"] = False
    with pytest.raises(ValueError, match="Un nom d'enseignant est obligatoire"):
        Creneau.model_validate(data)

def test_regle_fablab():
    data = base_creneau_data()
    data["intitule_cours"] = "Atelier Fablab"
    data["nom_salle"] = "Salle 1"
    with pytest.raises(ValueError, match="doit impérativement se dérouler dans la salle Fablab"):
        Creneau.model_validate(data)

def test_collision_promotion_service():
    """
    Test d'intégration sur l'algorithme de détection de chevauchement.
    Justification : Contrairement aux tests précédents qui s'arrêtent au modèle, 
    ce test valide la logique de base de données (ajout puis tentative de doublon).
    """
    service = PlanningService() 
    data = base_creneau_data()
    data["horodatage_debut"] = datetime(2026, 3, 24, 10, 0)
    data["horodatage_fin"] = datetime(2026, 3, 24, 12, 0)
    
    # Premier ajout : OK
    service.ajouter_creneau(Creneau(**data))
    
    # Deuxième ajout au même moment : Doit lever une ValueError
    with pytest.raises(ValueError, match="déjà occupée|a déjà un cours"):
        service.ajouter_creneau(Creneau(**data))

def test_annulation_libere_place():
    """
    Test d'intégration complet du cycle de vie d'un créneau : 
    Création -> Annulation (Soft Delete) -> Libération de la salle.
    """
    service = PlanningService()
    data = base_creneau_data()
    data["horodatage_debut"] = datetime(2026, 3, 25, 14, 0)
    data["horodatage_fin"] = datetime(2026, 3, 25, 16, 0)
    
    c1 = service.ajouter_creneau(Creneau(**data))
    service.annuler_creneau(c1.id)
    
    try:
        service.ajouter_creneau(Creneau(**data))
    except ValueError as e:
        pytest.fail(f"Le créneau aurait dû être libéré après annulation : {e}")