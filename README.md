# Workforce Data Service

Prototype de service dorsal développé pour l’exercice pratique du Bureau de la directrice parlementaire du budget (BDPB).

Le service importe plusieurs jeux de données sur l’effectif fédéral, les valide, les normalise, les stocke dans PostgreSQL et les expose au moyen d’une API REST.

## Fonctionnalités

- importation de tous les jeux de données fournis dans `data/data.xlsx`;
- validation et nettoyage des données avant le chargement;
- stockage structuré dans PostgreSQL;
- importation idempotente sans création de doublons;
- API REST pour consulter les ministères;
- calcul des ETP par trimestre;
- filtres par année et type de poste;
- tests automatisés.

## Technologies

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- psycopg
- pandas
- openpyxl
- pytest

## Structure du projet

```text
workforce-data-service/
├── app/
├── data/
│   └── data.xlsx
├── docs/
│   ├── data-import.md
│   ├── database-and-api.md
│   ├── security.md
│   └── design-questions.md
├── sql/
│   └── schema.sql
├── tests/
├── .env.example
├── main.py
├── README.md
└── requirements.txt
```

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/jojoakoun/workforce-data-service.git
cd workforce-data-service
```

### 2. Créer l’environnement Python

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### 3. Créer la base PostgreSQL

```bash
createdb workforce_data
```

### 4. Configurer l’environnement

Copier le fichier d’exemple :

```bash
cp .env.example .env
```

Configurer ensuite `DATABASE_URL` dans `.env`.

Exemple :

```text
DATABASE_URL=postgresql://<user>@localhost:5432/workforce_data
```

Le fichier `.env` ne doit pas être versionné.

### 5. Créer le schéma

```bash
psql -d workforce_data -f sql/schema.sql
```

> `sql/schema.sql` recrée les tables du prototype. Cette commande est destinée à l’installation initiale ou à la réinitialisation de l’environnement de développement.

## Importer les données

Depuis la racine du projet :

```bash
python main.py
```

Le pipeline :

1. lit le classeur Excel;
2. valide sa structure;
3. inspecte les données;
4. nettoie et valide les valeurs;
5. transforme les données;
6. charge les données dans PostgreSQL.

Le fichier source `data/data.xlsx` n’est jamais modifié.

L’importation est idempotente : plusieurs exécutions ne créent pas de doublons.

Après importation :

```text
101 ministères ou organismes
44 460 enregistrements d’effectif
```

## Exécuter l’API

```bash
python -m uvicorn app.api:app --reload
```

API locale :

```text
http://127.0.0.1:8000
```

Documentation interactive :

```text
http://127.0.0.1:8000/docs
```

## API REST

### Obtenir tous les ministères

```http
GET /api/departments
```

Exemple :

```bash
curl http://127.0.0.1:8000/api/departments
```

### Obtenir les ETP trimestriels d’un ministère

```http
GET /api/departments/{department_id}/fte
```

Filtres facultatifs :

```text
year
tenure
```

Exemples :

```bash
curl "http://127.0.0.1:8000/api/departments/2/fte"
```

```bash
curl "http://127.0.0.1:8000/api/departments/2/fte?year=2020"
```

```bash
curl "http://127.0.0.1:8000/api/departments/2/fte?year=2020&tenure=Term"
```

## Tests

Exécuter toute la suite :

```bash
python -m pytest -v
```

Dernier résultat local :

```text
50 tests passed
```

## Documentation détaillée

- [Importation et qualité des données](docs/data-import.md)
- [Base de données et API](docs/database-and-api.md)
- [Sécurité et priorisation des risques](docs/security.md)
- [Questions de conception](docs/design-questions.md)

## Principaux fichiers d’implémentation

| Sujet | Fichier |
|---|---|
| Lecture du classeur | `app/ingestion.py` |
| Inspection des données | `app/inspection.py` |
| Nettoyage | `app/cleaning.py` |
| Validation | `app/validation.py` |
| Traitement | `app/processing.py` |
| Transformation | `app/transformation.py` |
| Connexion PostgreSQL | `app/database.py` |
| Chargement | `app/loader.py` |
| Requêtes SQL | `app/queries.py` |
| API REST | `app/api.py` |
| Schéma PostgreSQL | `sql/schema.sql` |
| Pipeline principal | `main.py` |
| Tests | `tests/` |

## Utilisation de l’intelligence artificielle

Des outils d’intelligence artificielle ont servi d’aide au développement pour discuter de choix de conception, examiner des idées d’implémentation, résoudre des erreurs et améliorer la documentation.

J’ai examiné, testé, modifié et validé le code et les décisions inclus dans cette soumission. Je demeure responsable du fonctionnement, de l’architecture et de la documentation du projet.