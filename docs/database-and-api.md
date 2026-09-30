# Base de données et API

Ce document décrit le modèle PostgreSQL, le chargement des données et les deux points de terminaison REST du Workforce Data Service.

## Modèle de données

Le prototype utilise deux tables principales :

```text
departments
workforce_records
```

Le schéma est défini dans :

```text
sql/schema.sql
```

## Table `departments`

La table `departments` contient la référence bilingue des ministères et organismes.

```text
id
long_name_en
long_name_fr
short_name_en
short_name_fr
```

### Règles

`id` est la clé primaire.

`long_name_en` est obligatoire et unique.

`long_name_fr` est obligatoire.

`short_name_en` et `short_name_fr` peuvent être `NULL`, car certaines valeurs sont absentes du fichier fourni.

## Table `workforce_records`

La table `workforce_records` contient les observations d’effectif.

```text
id
period
source
department_id
tenure
headcount
fte
```

### Relations

`department_id` est une clé étrangère vers :

```text
departments.id
```

Cette relation évite de répéter les noms complets des ministères dans chaque observation.

### Source

Le champ `source` conserve l’origine de chaque observation.

Les valeurs utilisées sont :

```text
Federal Public Service
RCMP
CAF
```

La source est conservée parce que les trois jeux de données ne contiennent pas exactement les mêmes informations.

Par exemple, `RCMP` et `CAF` ne fournissent pas de colonne ETP.

### Contraintes de données

PostgreSQL protège également certaines règles de qualité.

`headcount` ne peut pas être négatif lorsqu’il est présent.

`fte` ne peut pas être négatif lorsqu’il est présent.

La base applique aussi une contrainte d’unicité sur :

```text
period
source
department_id
tenure
```

Cette combinaison représente la clé métier utilisée par le prototype.

## Importation idempotente

Le chargement se trouve dans :

```text
app/loader.py
```

Le pipeline peut être exécuté plusieurs fois sans créer de doublons.

Les insertions utilisent les contraintes PostgreSQL pour ignorer les enregistrements déjà présents.

Cette propriété rend l’importation plus sûre à réexécuter pendant le développement ou après un échec partiel.

## Connexion PostgreSQL

La connexion est créée dans :

```text
app/database.py
```

L’application lit :

```text
DATABASE_URL
```

depuis l’environnement.

Exemple de configuration locale :

```text
DATABASE_URL=postgresql://<user>@localhost:5432/workforce_data
```

La valeur réelle est placée dans :

```text
.env
```

Le dépôt contient seulement :

```text
.env.example
```

## API REST

L’API FastAPI se trouve dans :

```text
app/api.py
```

Les requêtes SQL utilisées par l’API se trouvent dans :

```text
app/queries.py
```

Le service est lancé avec :

```bash
python -m uvicorn app.api:app --reload
```

La documentation interactive générée par FastAPI est disponible à :

```text
http://127.0.0.1:8000/docs
```

## Obtenir tous les ministères

### Requête

```http
GET /api/departments
```

### Exemple

```bash
curl http://127.0.0.1:8000/api/departments
```

### Structure de réponse

```json
{
  "departments": [
    {
      "dept_id": 1,
      "dept_long": {
        "en": "Accessibility Standards Canada",
        "fr": "Normes d’accessibilité Canada"
      },
      "dept_short": {
        "en": "ASC",
        "fr": "NAC"
      }
    }
  ]
}
```

Lorsqu’un nom abrégé est absent dans la source, l’API retourne `null`.

Exemple :

```json
{
  "dept_short": {
    "en": null,
    "fr": null
  }
}
```

## Obtenir les ETP trimestriels

### Requête

```http
GET /api/departments/{department_id}/fte
```

Le point de terminaison accepte deux filtres facultatifs :

```text
year
tenure
```

Le paramètre `tenure` représente le type de poste présent dans les données source.

### Sans filtre

```bash
curl "http://127.0.0.1:8000/api/departments/2/fte"
```

### Filtre par année

```bash
curl "http://127.0.0.1:8000/api/departments/2/fte?year=2020"
```

### Filtre par type de poste

```bash
curl "http://127.0.0.1:8000/api/departments/2/fte?tenure=Term"
```

### Combinaison des filtres

```bash
curl "http://127.0.0.1:8000/api/departments/2/fte?year=2020&tenure=Term"
```

### Structure de réponse

```json
{
  "fte_per_quarter": [
    {
      "year": 2020,
      "quarter": 1,
      "indeterminate": 413.2,
      "term": 114.27,
      "casual": 31.13,
      "student": 8.12,
      "missing": 0
    }
  ]
}
```

Le champ :

```text
missing
```

correspond à la catégorie source :

```text
tenure = "Missing"
```

Il ne représente pas les valeurs SQL `NULL`.

## Calcul trimestriel des ETP

Les observations ETP fournies sont mensuelles.

L’exercice demande une réponse trimestrielle, mais ne précise pas la méthode d’agrégation.

Le prototype utilise donc la moyenne arithmétique des valeurs mensuelles disponibles dans chaque trimestre.

Exemple :

```text
Avril : 96
Mai   : 99
Juin  : 99
```

Calcul :

```text
(96 + 99 + 99) / 3 = 98
```

Le service retourne donc :

```text
T2 = 98 ETP
```

Les valeurs mensuelles ne sont pas additionnées.

Une somme donnerait :

```text
294
```

et compterait plusieurs fois un niveau d’effectif mesuré à différents moments du trimestre.

La moyenne trimestrielle est donc une hypothèse de conception du prototype.

Cette logique est mise en œuvre dans :

```text
app/queries.py
```

## Données ETP de RCMP et CAF

Les feuilles `RCMP` et `CAF` ne fournissent pas d’ETP.

Leurs enregistrements sont stockés avec :

```text
fte = NULL
```

Le service ne transforme pas cette absence en zéro.

Une requête ETP pour un ministère ne disposant d’aucune valeur ETP peut donc retourner une liste vide.

## Ministère inexistant

L’API vérifie que le ministère existe avant de demander ses données ETP.

Un identifiant inexistant retourne :

```http
404 Not Found
```

Exemple :

```bash
curl -i "http://127.0.0.1:8000/api/departments/999999/fte"
```

Réponse :

```json
{
  "detail": "Department not found."
}
```

## Requêtes SQL

Les requêtes utilisent des paramètres fournis séparément des instructions SQL.

Cette approche évite de construire une requête en concaténant directement les valeurs reçues par l’API.

Les requêtes sont regroupées dans :

```text
app/queries.py
```

## Tests de l’API

Les tests se trouvent dans :

```text
tests/test_api.py
```

Ils vérifient notamment :

- `GET /api/departments`;
- la structure de la réponse;
- `GET /api/departments/{id}/fte`;
- le filtre `year`;
- le filtre `tenure`;
- la combinaison des deux filtres;
- le comportement `404`.

La suite complète est exécutée avec :

```bash
python -m pytest -v
```

Le dernier passage local a produit :

```text
50 tests passed
```