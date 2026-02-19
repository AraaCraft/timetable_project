# Timetable Project 📅

Projet réalisé en binôme dans le cadre du cours de Programmation Web (DEUST IOSI 2ème année). 
Ce projet consiste à créer de A à Z une API de gestion de planning scolaire en appliquant les principes de la Clean Architecture.

## 🚀 Fonctionnalités (Règles Métier)
- **Gestion des plannings :** Emploi du temps par promotion sur une semaine (Lundi au Vendredi, 08h15 - 17h15).
- **Gestion des cours :** Durée variable (30 min à 4h), attribution d'enseignants, de salles et de promotions.
- **Prévention des conflits (Bonus) :** Une promotion ne peut pas avoir deux cours en même temps, et une salle ne peut accueillir qu'un cours à la fois.
- **Consultation :** Accès en lecture pour n'importe quel utilisateur sur une semaine/date donnée.
- **Sécurité :** Mise à jour restreinte aux utilisateurs autorisés.

## 🛠️ Stack Technique
- **Langage :** Python 3.10+
- **Framework API :** FastAPI
- **ORM & Base de données :** SQLModel / SQLite (avec migration prévue vers PostgreSQL)
- **Validation des données :** Pydantic
- **Qualité de code & Tests :** Pytest, Coverage, Flake8, Bandit

## 📂 Architecture du Projet (Clean Architecture)
Le code métier est strictement séparé des intégrations techniques (base de données, framework web).

```text
src/
├── main/
│   ├── api.py            # Endpoints FastAPI orientés métier
│   ├── domain/           # Cœur métier : Modèles Pydantic et logique (sans SQL)
│   └── infrastructure/   # Intégrations : Configuration BDD (SQLModel)
└── tests/                # Tests unitaires et d'intégration
