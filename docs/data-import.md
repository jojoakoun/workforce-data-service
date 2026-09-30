# Importation et qualité des données

Ce document décrit le processus d’importation, les contrôles de qualité et les décisions appliquées aux données fournies dans `data/data.xlsx`.

L’objectif est de charger les données dans PostgreSQL sans modifier le fichier source et sans inventer de valeurs qui ne peuvent pas être confirmées.

## Sources de données

Le classeur contient quatre feuilles :

```text
Federal Public Service
RCMP
CAF
Departments
```

Les trois premières contiennent les observations d’effectif.

La feuille `Departments` contient la référence bilingue des ministères et organismes.

Les principaux fichiers utilisés pendant l’importation sont :

```text
app/ingestion.py
app/inspection.py
app/cleaning.py
app/validation.py
app/processing.py
app/transformation.py
app/loader.py
main.py
```

## Processus d’importation

Le pipeline complet est lancé depuis la racine du projet :

```bash
python main.py
```

Il exécute les étapes suivantes :

1. lire le classeur Excel;
2. vérifier les feuilles et les colonnes requises;
3. inspecter les données;
4. nettoyer et valider les types de poste;
5. nettoyer et valider les noms des ministères;
6. traiter les valeurs de `headcount`;
7. valider les valeurs d’ETP;
8. valider les périodes;
9. nettoyer la référence des ministères;
10. vérifier les doublons;
11. préparer les données pour PostgreSQL;
12. charger les données dans la base.

`main.py` orchestre le pipeline. Les règles détaillées restent dans des modules spécialisés afin de séparer les responsabilités.

## Protection du fichier source

Le fichier :

```text
data/data.xlsx
```

n’est jamais modifié.

Le pipeline lit les données avec pandas, puis effectue les corrections et transformations en mémoire.

Cette approche conserve une copie intacte des données reçues.

## Validation de la structure

Avant tout traitement, le pipeline vérifie que les quatre feuilles attendues sont présentes.

### Federal Public Service

Colonnes requises :

```text
date
tenure
department
headcount
fte
```

### RCMP

Colonnes requises :

```text
date
tenure
department
headcount
```

### CAF

Colonnes requises :

```text
date
tenure
department
headcount
```

### Departments

Colonnes requises :

```text
long_name_en
long_name_fr
short_name_en
short_name_fr
```

Une structure invalide arrête le pipeline avant le chargement dans PostgreSQL.

L’implémentation se trouve dans :

```text
app/validation.py
```

## Inspection des données

Le pipeline inspecte les données avant certaines corrections afin de rendre les problèmes visibles.

Les contrôles portent notamment sur :

- les types de poste;
- les espaces inutiles;
- les noms des ministères;
- les valeurs de `headcount`;
- les valeurs d’ETP;
- les périodes;
- les doublons;
- la qualité de la référence `Departments`.

L’implémentation se trouve dans :

```text
app/inspection.py
```

## Nettoyage des textes

Les valeurs texte pertinentes sont normalisées afin de supprimer les espaces inutiles.

Par exemple :

```text
"Term "
```

devient :

```text
"Term"
```

La même règle est appliquée aux noms des ministères et aux champs texte de la référence bilingue.

L’implémentation se trouve dans :

```text
app/cleaning.py
```

## Types de poste

Les valeurs observées dans `Federal Public Service` sont :

```text
Indeterminate
Term
Student
Casual
Missing
```

Les feuilles `RCMP` et `CAF` utilisent :

```text
Combined
```

Le pipeline valide les valeurs selon leur source.

Une distinction est conservée entre :

```text
"Missing"
```

et une véritable valeur manquante.

`"Missing"` est une catégorie présente dans la source. Une valeur manquante représente une absence de donnée.

## Noms des ministères

Les noms provenant des données d’effectif sont comparés avec :

```text
Departments.long_name_en
```

après nettoyage.

Une erreur confirmée dans la source est corrigée explicitement :

```text
Privy Council Officee
```

devient :

```text
Privy Council Office
```

Le prototype n’utilise pas de correspondance approximative (*fuzzy matching*).

Cette décision évite de modifier automatiquement un nom uniquement parce qu’il ressemble à un autre.

Après nettoyage et correction, les noms utilisés dans les données d’effectif doivent correspondre à la référence.

## `headcount`

Une valeur de `headcount` présente doit :

- être entière;
- être égale ou supérieure à zéro.

Les valeurs manquantes sont autorisées.

Une valeur négative a été trouvée dans la source :

```text
-20
```

Cette valeur est remplacée par une valeur manquante.

Elle n’est pas transformée en :

```text
20
```

car la source ne permet pas de confirmer que `20` serait la bonne valeur.

Le pipeline ne calcule pas non plus un `headcount` manquant à partir de l’ETP.

Après nettoyage, `Federal Public Service` contient dix valeurs `headcount` manquantes.

## ETP (`fte`)

La colonne `fte` existe uniquement dans :

```text
Federal Public Service
```

Les valeurs manquantes sont autorisées.

Aucune valeur ETP négative n’a été observée dans les données fournies.

Les feuilles `RCMP` et `CAF` ne contiennent pas de colonne `fte`.

Cette absence signifie que la donnée n’est pas disponible pour ces sources. Le pipeline ne la remplace donc pas par zéro.

## Périodes

Les périodes sont fournies au format :

```text
YYYYMM
```

Par exemple :

```text
201503
```

représente mars 2015.

Pour PostgreSQL, cette valeur devient :

```text
2015-03-01
```

Le premier jour du mois sert uniquement à représenter le mois avec le type PostgreSQL `DATE`.

Les périodes observées sont :

```text
Federal Public Service : 201503 à 202606
RCMP                   : 201504 à 202606
CAF                    : 201504 à 202606
```

Aucune période manquante ou comportant un mois invalide n’a été observée.

La transformation se trouve dans :

```text
app/transformation.py
```

## Référence des ministères

La feuille `Departments` contenait initialement 102 lignes.

Un doublon exact a été identifié et supprimé.

Après nettoyage :

```text
101 lignes uniques
0 long_name_en manquant
0 long_name_fr manquant
12 short_name_en manquants
12 short_name_fr manquants
```

Les noms abrégés manquants restent `NULL`.

Le pipeline ne crée pas d’acronymes qui ne figurent pas dans les données fournies.

## Doublons des données d’effectif

Aucun doublon exact n’a été trouvé dans les trois feuilles d’effectif.

Aucun doublon n’a également été trouvé pour la combinaison :

```text
date
department
tenure
```

à l’intérieur de chaque source.

Dans PostgreSQL, la source est également conservée dans la clé métier :

```text
period
source
department_id
tenure
```

Cette règle empêche deux exécutions du pipeline de créer plusieurs copies du même enregistrement.

## Résultat de l’importation

Après nettoyage et chargement, la base contient :

```text
101 ministères ou organismes
44 460 enregistrements d’effectif
```

Répartition par source :

```text
Federal Public Service    44 408
RCMP                           26
CAF                            26
```

Valeurs manquantes observées après importation :

```text
Federal Public Service
headcount : 10
fte       : 8

RCMP
headcount : 0
fte       : 26

CAF
headcount : 0
fte       : 26
```

Les valeurs ETP manquantes de `RCMP` et `CAF` proviennent de l’absence de cette information dans les feuilles source.

## Tests associés

Les tests du processus d’importation se trouvent dans :

```text
tests/test_ingestion.py
tests/test_inspection.py
tests/test_cleaning.py
tests/test_validation.py
tests/test_processing.py
tests/test_transformation.py
tests/test_loader.py
```

La suite complète peut être exécutée avec :

```bash
python -m pytest -v
```