import pytest
from datetime import datetime
from src.main.domain.models import Creneau

# ==========================================
# DONNÉES DE BASE (Fixtures / Helpers)
# ==========================================

def base_creneau_data() -> dict:
    """Retourne un dictionnaire de données valides pour un créneau (Un Lundi de 10h à 12h)."""
    return {
        "id_cours": 1,
        "id_intervenant": 1,
        "id_salle": 1,
        "id_promotion": 1,
        # Lundi 2 Mars 2026
        "horodatage_debut": datetime(2026, 3, 2, 10, 0),
        "horodatage_fin": datetime(2026, 3, 2, 12, 0)
    }

# ==========================================
# LES TESTS UNITAIRES
# ==========================================

def test_creneau_valide():
    """Test qu'un créneau normal est accepté sans erreur."""
    data = base_creneau_data()
    creneau = Creneau(**data)
    assert creneau.id_cours == 1
    assert creneau.horodatage_debut == data["horodatage_debut"]

def test_heure_fin_avant_heure_debut():
    """Test la cohérence chronologique basique."""
    data = base_creneau_data()
    # On inverse les heures (12h -> 10h)
    data["horodatage_debut"] = datetime(2026, 3, 2, 12, 0)
    data["horodatage_fin"] = datetime(2026, 3, 2, 10, 0)
    
    with pytest.raises(ValueError, match="L'heure de fin doit être strictement après l'heure de début"):
        Creneau(**data)

def test_creneau_sur_plusieurs_jours():
    """Test qu'un cours ne peut pas s'étaler sur deux jours différents."""
    data = base_creneau_data()
    data["horodatage_fin"] = datetime(2026, 3, 3, 10, 0) # Le lendemain
    
    with pytest.raises(ValueError, match="Un créneau ne peut pas s'étaler sur plusieurs jours"):
        Creneau(**data)

def test_duree_trop_courte():
    """Test la limite minimum de 30 minutes."""
    data = base_creneau_data()
    data["horodatage_fin"] = datetime(2026, 3, 2, 10, 15) # Dure 15 minutes
    
    with pytest.raises(ValueError, match="comprise entre 30 minutes et 4 heures"):
        Creneau(**data)

def test_duree_trop_longue():
    """Test la limite maximum de 4 heures."""
    data = base_creneau_data()
    data["horodatage_fin"] = datetime(2026, 3, 2, 15, 0) # Dure 5 heures
    
    with pytest.raises(ValueError, match="comprise entre 30 minutes et 4 heures"):
        Creneau(**data)

def test_horaires_en_dehors_plage():
    """Test la plage horaire stricte (08h15 - 17h15)."""
    data = base_creneau_data()
    data["horodatage_debut"] = datetime(2026, 3, 2, 8, 0) # Commence à 8h00 (trop tôt)
    data["horodatage_fin"] = datetime(2026, 3, 2, 10, 0)
    
    with pytest.raises(ValueError, match="plage horaire autorisée"):
        Creneau(**data)

def test_cours_le_week_end():
    """Test que les cours le Samedi ou Dimanche sont interdits."""
    data = base_creneau_data()
    # Samedi 7 Mars 2026
    data["horodatage_debut"] = datetime(2026, 3, 7, 10, 0)
    data["horodatage_fin"] = datetime(2026, 3, 7, 12, 0)
    
    with pytest.raises(ValueError, match="du Lundi au Vendredi"):
        Creneau(**data)