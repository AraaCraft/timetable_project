## Consignes projet

### Organisation

- Travail de groupes.
- Travail de chaque étudiant identifiable (vous devriez vous appuyer sur `git`)
- A la fin de chaque session de travail, les étudiants envoient un compte rendu succint : travail réalisé, travail qui sera ensuite réalisé, difficultés rencontrées/questions (3-4 max).

### Règles métier

1. Organisation du planning

    - Chaque promotion a son propre emploi du temps.
    - Le planning est organisé sur *une seule semaine* (du Lundi au Vendredi).
    - Les cours sont programmés entre 08h15 et 17h15.

2. Créneaux horaires

    - Un cours a une durée variable (de 30 minutes à 4 heures maximum).
    - **BONUS** : Une promotion ne peut pas avoir deux cours au même moment.
    - **BONUS** : Une salle ne peut accueillir qu’un seul cours à la fois.

3. Gestion des cours
    
    - Chaque cours a un intitulé, un enseignant, une salle et une promotion concernée.
    - Certains cours nécessitent une salle spécifique (ex : Fablab).
    - Un cours peut être en autonomie ou dirigé par un enseignant.
    - Un cours peut être annulé ou modifié.

4. Disponibilité des salles

    - Une salle ne peut être utilisée que si elle est disponible sur le créneau demandé.

5. Consultation

    - N'importe qui doit pouvoir consulter l'emploi du temps pour une semaine donnée ou une date donnée.

6. Mise à jour du planning

    - Seul un utilisateur autorisé peut éditer le planning.

### Règles techniques

- Chaque étudiant travaillera sur son clone du projet.
- Langage de programmation : Python 3.10+.
- Code versionné sur Gitlab ou Github (ou git en local).
    - Aucun secret stocké en clair !
- Framework API : FastAPI.
- Base de données : SQLModel comme ORM python, techniquement sqlite pour commencer puis PostgreSQL.
    > Conseil : Vous pouvez réaliser le projet SANS base de données dans un 1er temps pour construire le code métier+API puis implémenter le stockage de données.
- Code source utilisé en production enregistré sous `src/main/`.
- **Tests** enregistrés sous `src/tests/`.
- L'IA générative peut vous assister, pas vous remplacer.
- Il doit être possible d'exécuter le projet en local.
- [Flake8](https://flake8.pycqa.org/en/latest/) sera utilisé pour le `lint` du code source.
- [Pytest](http://docs.pytest.org/en/stable/) ou [unittest](https://docs.python.org/3/library/unittest.html) peuvent être utilisés pour tester le code source.
- [Coverage](https://coverage.readthedocs.io/en/7.6.12/) sera utilisé pour mesurer la couverture du code par les tests.
- [Bandit](https://bandit.readthedocs.io/en/latest/) sera utilisé pour identifier des vulnérabilités communes dans le code source.

### Qualités appréciées - Bonus

- Chaque *point de terminaison API* est orienté **métier** pas **base de données**.
- Le `Swagger/OpenAPI` généré par FastAPI est bien documenté.
- Les modification du code apportées par chaque version sont compréhensibles et peuvent être suivies.
- Le code source est clair et maintenable.
- Le code métier est séparé des intégrations techniques (Exemple : la gestion de la base de données).
- Le code métier est couvert par des tests unitaires.
- Les intégrations techniques sont couvertes par des tests d'intégrations.
- Le fonctionnement global est vérifié par `Github actions` ou `Gitlab CI`.
- Des journaux, `logs`, permettent de suivre le fonctionnement de l'application et comprendre les erreurs.
- La documentation permet à un profil développeur de contribuer au projet.
- La documentation permet à un profil développeur d'instancier le projet.