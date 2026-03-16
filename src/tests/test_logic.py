import pytest
from datetime import datetime
from src.main.domain.models.creneau import Creneau
from src.main.domain.services.planning_service import PlanningService

# ==========================================
# DONNÉES DE BASE (Helpers)
# ==========================================

def base_creneau_data() -> dict:
    """Retourne un dictionnaire de données valides par défaut."""
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
    data = base_creneau_data()
    creneau = Creneau(**data)
    assert creneau.intitule_cours == "Mathématiques"

def test_heure_fin_avant_heure_debut():
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
# LES TESTS MÉTIER (Service)
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
    """Test le blocage des doublons sur une date dédiée (Mardi 24 Mars)."""
    service = PlanningService() 
    data = base_creneau_data()
    # On change la date pour éviter les conflits avec les tests précédents
    data["horodatage_debut"] = datetime(2026, 3, 24, 10, 0)
    data["horodatage_fin"] = datetime(2026, 3, 24, 12, 0)
    
    # Premier ajout : OK
    service.ajouter_creneau(Creneau(**data))
    
    # Deuxième ajout au même moment : Doit lever une ValueError
    with pytest.raises(ValueError, match="déjà occupée|a déjà un cours"):
        service.ajouter_creneau(Creneau(**data))

def test_annulation_libere_place():
    """Test qu'une annulation libère bien le créneau (Mercredi 25 Mars)."""
    service = PlanningService()
    data = base_creneau_data()
    data["horodatage_debut"] = datetime(2026, 3, 25, 14, 0)
    data["horodatage_fin"] = datetime(2026, 3, 25, 16, 0)
    
    # On ajoute puis on annule
    c1 = service.ajouter_creneau(Creneau(**data))
    service.annuler_creneau(c1.id)
    
    # On doit pouvoir rajouter un cours maintenant que c'est annulé
    try:
        service.ajouter_creneau(Creneau(**data))
    except ValueError as e:
        pytest.fail(f"Le créneau aurait dû être libéré après annulation : {e}")