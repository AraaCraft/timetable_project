# Timetable Project 📅

Projet réalisé en binôme dans le cadre du cours de Programmation Web (DEUST IOSI 2ème année). 
Ce projet consiste à créer de A à Z une API de gestion de planning scolaire en appliquant les principes de la **Clean Architecture**.

## 🚀 Fonctionnalités (Règles Métier)
- **Gestion des plannings :** Emploi du temps par promotion sur une semaine (Lundi au Vendredi, 08h15 - 17h15).
- **Gestion des cours :** Durée variable (30 min à 4h), attribution d'enseignants, de salles et de promotions.
- **Prévention des conflits (Bonus) :** Une promotion ne peut pas avoir deux cours en même temps, et une salle ne peut accueillir qu'un cours à la fois.
- **Consultation :** Accès en lecture pour n'importe quel utilisateur sur une semaine/date donnée.
- **Sécurité :** Mise à jour restreinte aux utilisateurs autorisés.

## 🛠️ Stack Technique
- **Langage :** Python 3.10+
- **Framework API :** FastAPI
- **ORM & Base de données :** SQLModel / SQLite
- **Qualité & Sécurité :** Flake8 (Linting), Bandit (Sécurité), Black (Formatage)
- **Tests :** Pytest avec Coverage (Couverture actuelle : 94%)
- **CI/CD :** GitHub Actions (Tests automatisés à chaque push)

## 📂 Architecture du Projet
Le projet suit les principes de la **Clean Architecture** pour séparer la logique métier des détails techniques.

```text
timetable_project/
├── .github/
│   └── workflows/
│       └── tests.yml         # CI/CD (GitHub Actions)
├── src/
│   ├── main/
│   │   ├── api.py            # Endpoints FastAPI
│   │   ├── domain/           # Cœur métier (Logique pure)
│   │   │   ├── models/       # Modèles de données (Pydantic/SQLModel)
│   │   │   └── services/     # Logique métier et calculs
│   │   └── infrastructure/   # Persistance (Base de données)
│   └── tests/                # Tests unitaires et d'intégration
├── .flake8                   # Configuration du linter
├── requirements.txt          # Dépendances du projet
└── README.md                 # Documentation

```

## ⚙️ Installation et Lancement

1. **Cloner le projet :**
```bash
git clone [https://github.com/AraaCraft/timetable_project.git](https://github.com/AraaCraft/timetable_project.git)
cd timetable_project

```

2. **Créer un environnement virtuel :**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate

```

3. **Installer les dépendances :**
```bash
pip install -r requirements.txt

```

4. **Lancer l'API :**
```bash
uvicorn src.main.api:app --reload

```

L'interface Swagger est alors disponible sur : `http://127.0.0.1:8000/docs`

## 🧪 Tests et Qualité

Pour vérifier le bon fonctionnement et la qualité du code :

* **Lancer les tests :** `pytest`
* **Vérifier la couverture :** `pytest --cov=src`
* **Analyse de sécurité :** `bandit -r src/main`
* **Vérification du style :** `flake8 src/main`

---

*Réalisé par Margaux Brun & Camille — DEUST IOSI Perpignan (2026)*