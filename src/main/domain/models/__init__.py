"""
Point d'entrée du package 'models'.

Ce fichier centralise l'export de toutes les entités de notre domaine métier :

1. Encapsulation : Permet aux autres couches (comme l'API ou les Services) 
  d'importer les modèles depuis 'src.main.domain.models' sans avoir besoin 
   de connaître l'arborescence exacte des fichiers internes.
2. Enregistrement ORM : Garantit que tous les modèles SQLModel sont 
   chargés en mémoire afin que 'SQLModel.metadata.create_all()' puisse détecter 
   et créer toutes les tables lors du démarrage de l'application.
"""

from .intervenant import Intervenant
from .salle import Salle
from .cours import Cours
from .promotion import Promotion
from .creneau import Creneau
from .planning import Planning

# Cela évite que Flake8 ne signale ces 
# importations comme étant "inutilisées" (F401), et sécurise l'utilisation
# potentielle de 'from models import *'.
__all__ = ["Intervenant", "Salle", "Cours", "Promotion", "Creneau", "Planning"]